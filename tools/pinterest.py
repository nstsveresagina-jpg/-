#!/usr/bin/env python3
"""Pinterest photo finder and downloader. Standard library only, no API key.

Uses the same public JSON endpoints the pinterest.com web app calls for
logged-out visitors.

  pinterest.py search "jeju island autumn" -n 30
  pinterest.py search "minimal bakery" -n 20 -o refs/
  pinterest.py get https://www.pinterest.com/pin/811070214161207304/ -o refs/
  pinterest.py get https://pin.it/4kDdXyP -o refs/
  pinterest.py get https://www.pinterest.com/enoh471/south-korea/ -n 50 -o refs/
  pinterest.py get https://www.pinterest.com/enoh471/ -n 20
  pinterest.py search "jeju waterfall" --videos --vertical -n 10 -o clips/

Without -o it prints the list of found pins. With -o it downloads the images
(and videos with --video) into that folder and writes pins.json next to them
with each file's source pin, author and title.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://www.pinterest.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
SIZES = ["orig", "736x", "474x", "236x"]
# Pinterest paths that are not user names.
RESERVED = {"search", "pin", "ideas", "today", "explore", "business",
            "categories", "topics", "_", "resource", "settings"}


class PinterestError(Exception):
    pass


def http(url, headers=None, timeout=30, retries=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.geturl(), r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise PinterestError(f"HTTP {e.code} for {url}") from None
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise PinterestError(f"{e.reason} for {url}") from None


def resource(name, options, source_url, handler):
    query = urllib.parse.urlencode({
        "source_url": source_url,
        "data": json.dumps({"options": options, "context": {}}),
    })
    try:
        _, body = http(f"{BASE}/resource/{name}/get/?{query}", {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "X-Pinterest-PWS-Handler": handler,
            "X-Pinterest-AppState": "active",
            "Referer": BASE + "/",
        })
    except PinterestError as e:
        if "HTTP 404" in str(e):
            raise PinterestError(f"not found on Pinterest: {source_url}") from None
        raise
    rr = json.loads(body).get("resource_response") or {}
    if rr.get("error"):
        raise PinterestError(f"{name}: {rr['error'].get('message') or rr['error']}")
    return rr.get("data"), rr.get("bookmark")


def paginate(name, options, source_url, handler, limit, keep=lambda p: True):
    """Yields up to `limit` pins accepted by `keep` from a paged feed.

    Feeds sometimes answer a page with no bookmark or no pins although more
    exist, so such a page is re-requested a few times before giving up.
    """
    seen, ids, bookmark = 0, set(), None
    while seen < limit:
        opts = dict(options, page_size=50)
        if bookmark:
            opts["bookmarks"] = [bookmark]
        for attempt in range(4):
            data, next_bookmark = resource(name, opts, source_url, handler)
            items = data.get("results", []) if isinstance(data, dict) else (data or [])
            pins = [p for p in items if isinstance(p, dict) and p.get("type") == "pin"]
            if next_bookmark == "-end-" or (pins and next_bookmark):
                break
            time.sleep(1)
        for p in pins:
            if p.get("id") in ids or not keep(p):
                continue
            ids.add(p.get("id"))
            seen += 1
            yield p
            if seen >= limit:
                return
        bookmark = next_bookmark
        if not pins or not bookmark or bookmark == "-end-":
            return


def best_image(images, size):
    images = images or {}
    order = SIZES[SIZES.index(size):] if size in SIZES else SIZES
    for key in order + list(images):
        if images.get(key, {}).get("url"):
            return images[key]
    return None


def hls_to_mp4(entry):
    """The 720p mp4 Pinterest keeps next to an HLS stream (same top quality, with sound).

    .../videos/iht/hls/c8/db/59/<hash>.m3u8 -> .../videos/iht/720p/c8/db/59/<hash>.mp4
    The listed size is the canvas, not the encode, so it is scaled to a 720 px short side.
    """
    url = re.sub(r"/hls/(.+)\.m3u8$", r"/720p/\1.mp4", entry["url"])
    w, h = entry.get("width") or 0, entry.get("height") or 0
    k = 720 / min(w, h) if min(w, h) > 720 else 1
    return dict(entry, url=url, hls=entry["url"], width=round(w * k), height=round(h * k))


def best_video(pin):
    """Best mp4 of a video pin: a progressive one, else the one derived from HLS."""
    lists = [((pin.get("videos") or {}).get("video_list") or {})]
    for page in ((pin.get("story_pin_data") or {}).get("pages") or []):
        for block in page.get("blocks") or []:
            lists.append(((block.get("video") or {}).get("video_list") or {}))
    entries = [v for vl in lists for v in vl.values() if isinstance(v, dict) and v.get("url")]
    mp4s = [v for v in entries if v["url"].endswith(".mp4")]
    if not mp4s:
        mp4s = [hls_to_mp4(v) for v in entries if v["url"].endswith(".m3u8")]
    return max(mp4s, key=lambda v: v.get("width") or 0, default=None)


def idea_pin_images(pin, size):
    """Extra pages of a multi-page Idea pin, beyond the cover image."""
    out = []
    for page in ((pin.get("story_pin_data") or {}).get("pages") or []):
        for block in page.get("blocks") or []:
            img = best_image((block.get("image") or {}).get("images"), size)
            if img and img not in out:
                out.append(img)
    return out


def summarize(pin, size):
    pinner = pin.get("pinner") or pin.get("native_creator") or {}
    board = pin.get("board") or {}
    pid = str(pin.get("id"))
    images = []
    cover = best_image(pin.get("images"), size)
    if cover:
        images.append(cover)
    for img in idea_pin_images(pin, size):
        if img["url"] not in {i["url"] for i in images}:
            images.append(img)
    video = best_video(pin)
    return {
        "id": pid,
        # Logged-out search returns encrypted "e1_..." ids that have no public page.
        "pin_url": f"{BASE}/pin/{pid}/" if pid.isdigit() else "",
        "title": " ".join((pin.get("grid_title") or pin.get("title") or "").split()),
        "description": (pin.get("description") or "").strip(),
        "alt": pin.get("auto_alt_text") or pin.get("seo_alt_text") or "",
        "author": pinner.get("username") or pinner.get("full_name") or "",
        "board": board.get("url") and BASE + board["url"],
        "source_link": pin.get("link") or "",
        "dominant_color": pin.get("dominant_color") or "",
        "images": [{"url": i["url"], "width": i.get("width"), "height": i.get("height")}
                   for i in images],
        "video": video and {"url": video["url"], "hls": video.get("hls", ""),
                            "width": video.get("width"), "height": video.get("height"),
                            "duration_ms": video.get("duration")},
    }


def search(query, limit, keep=lambda p: True, videos=False):
    scope = "videos" if videos else "pins"
    src = f"/search/{scope}/?" + urllib.parse.urlencode({"q": query, "rs": "typed"})
    return paginate("BaseSearchResource", {"query": query, "scope": scope,
                                           "auto_correction_disabled": False},
                    src, "www/search/[scope].js", limit, keep)


def get_pin(pin_id):
    data, _ = resource("PinResource", {"id": pin_id, "field_set_key": "detailed"},
                       f"/pin/{pin_id}/", "www/pin/[id].js")
    if not data:
        raise PinterestError(f"pin {pin_id} not found")
    return data


def board_pins(username, slug, limit, keep=lambda p: True):
    src = f"/{username}/{slug}/"
    board, _ = resource("BoardResource", {"username": username, "slug": slug,
                                          "field_set_key": "detailed"},
                        src, "www/[username]/[slug].js")
    if not board or not board.get("id"):
        raise PinterestError(f"board /{username}/{slug}/ not found")
    print(f"# board «{board.get('name')}» by {username}, {board.get('pin_count')} pins",
          file=sys.stderr)
    return paginate("BoardFeedResource", {"board_id": board["id"],
                                          "board_url": src, "field_set_key": "react_grid_pin"},
                    src, "www/[username]/[slug].js", limit, keep)


def user_pins(username, limit, keep=lambda p: True):
    return paginate("UserPinsResource", {"username": username, "field_set_key": "grid_item"},
                    f"/{username}/", "www/[username].js", limit, keep)


def from_url(url, limit, keep=lambda p: True, videos=False):
    """Pins for any Pinterest link: pin, pin.it, board, profile or search page."""
    if re.fullmatch(r"\d+", url):
        return [get_pin(url)]
    if not re.match(r"https?://", url):
        url = "https://" + url
    host = urllib.parse.urlparse(url).netloc.lower()
    if host in ("pin.it", "www.pin.it"):
        url, _ = http(url)
        if "/pin/" not in url:
            raise PinterestError(f"short link did not lead to a pin (landed on {url})")
    parsed = urllib.parse.urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    if parts and parts[0] == "pin" and len(parts) > 1:
        pin_id = parts[1].split("--")[-1]
        if not pin_id.isdigit():
            raise PinterestError(f"{pin_id} is not a public pin id; use the image URL "
                                 "from the search results instead")
        return [get_pin(pin_id)]
    if parts and parts[0] == "search":
        q = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
        if not q:
            raise PinterestError("search URL has no ?q=")
        return search(q, limit, keep, videos or parts[1:2] == ["videos"])
    if len(parts) >= 2 and parts[0] not in RESERVED:
        return board_pins(parts[0], parts[1], limit, keep)
    if len(parts) == 1 and parts[0] not in RESERVED:
        return user_pins(parts[0], limit, keep)
    raise PinterestError(f"don't know how to read {url}")


def ext_of(url):
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    return ext if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4") else ".jpg"


def file_stem(pin, media):
    """Numeric pin id, or the image hash for pins that only have an e1_ id."""
    if pin["id"].isdigit():
        return pin["id"]
    return os.path.splitext(os.path.basename(urllib.parse.urlparse(media["url"]).path))[0]


def save_hls(hls_url, path):
    """Fallback for video pins without an mp4: remux the HLS stream with ffmpeg."""
    if not shutil.which("ffmpeg"):
        return False
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", hls_url,
                        "-c", "copy", "-bsf:a", "aac_adtstoasc", path])
    return r.returncode == 0 and os.path.exists(path)


def download(pins, out_dir, want_video, min_width):
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, "pins.json")
    manifest = []
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
    known = {m["file"] for m in manifest}
    saved = 0
    for pin in pins:
        targets = [] if not want_video else ([pin["video"]] if pin["video"] else [])
        targets += [i for i in pin["images"] if (i.get("width") or min_width) >= min_width]
        if want_video and pin["video"]:
            targets = targets[:1]  # the video, not its poster frame
        for n, media in enumerate(targets):
            suffix = f"_{n + 1}" if len(targets) > 1 else ""
            name = f"{file_stem(pin, media)}{suffix}{ext_of(media['url'])}"
            path = os.path.join(out_dir, name)
            if name in known and os.path.exists(path):
                continue
            try:
                _, body = http(media["url"], {"Referer": BASE + "/"}, timeout=300)
                with open(path, "wb") as f:
                    f.write(body)
            except PinterestError as e:
                if not (media.get("hls") and save_hls(media["hls"], path)):
                    print(f"  skip {name}: {e}", file=sys.stderr)
                    continue
            saved += 1
            print(f"  saved {path} ({media.get('width')}x{media.get('height')}, "
                  f"{os.path.getsize(path) // 1024} KB)  {pin['title'][:60]}")
            manifest.append({"file": name, **{k: pin[k] for k in (
                "pin_url", "title", "alt", "author", "board", "source_link")},
                "media_url": media["url"], "width": media.get("width"),
                "height": media.get("height")})
            known.add(name)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"# {saved} new file(s) in {out_dir}, sources in {manifest_path}", file=sys.stderr)


def print_list(pins):
    for n, p in enumerate(pins, 1):
        v = p["video"]
        media = v or (p["images"][0] if p["images"] else {})
        kind = f" [video {(v['duration_ms'] or 0) / 1000:.0f}s]" if v else ""
        extra = f" [+{len(p['images']) - 1} pages]" if len(p["images"]) > 1 else ""
        print(f"{n:3}. {p['id']}  {media.get('width')}x{media.get('height')}{kind}{extra}  "
              f"{p['title'][:70] or p['alt'][:70]}")
        print(f"     {media.get('url', '-')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search pins (or videos with --videos) by text")
    s.add_argument("query")
    g = sub.add_parser("get", help="pins from a pin / pin.it / board / profile / search URL")
    g.add_argument("url")
    for p in (s, g):
        p.add_argument("-n", "--limit", type=int, default=25, help="max pins (default 25)")
        p.add_argument("-o", "--out", help="download into this folder")
        p.add_argument("--size", choices=SIZES, default="orig",
                       help="preferred image size (default orig)")
        p.add_argument("--min-width", type=int, default=0,
                       help="skip images narrower than this many px")
        p.add_argument("--video", action="store_true",
                       help="download the mp4 instead of the cover for video pins")
        p.add_argument("--videos", action="store_true",
                       help="videos only: search Pinterest's video tab, skip non-video "
                            "pins, download mp4s (implies --video)")
        p.add_argument("--vertical", action="store_true",
                       help="keep only portrait media (taller than wide), e.g. for Reels")
        p.add_argument("--min-duration", type=float, default=0,
                       help="videos: skip clips shorter than this many seconds")
        p.add_argument("--max-duration", type=float, default=0,
                       help="videos: skip clips longer than this many seconds")
        p.add_argument("--json", action="store_true", help="print pins as JSON")
    a = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)

    try:
        video_filters = a.videos or a.min_duration or a.max_duration

        def keep(pin):
            video = best_video(pin)
            media = video or (pin.get("images") or {}).get("orig") or {}
            w, h = media.get("width") or 0, media.get("height") or 0
            if video_filters:
                if not video:
                    return False
                secs = (video.get("duration") or 0) / 1000
                if secs < a.min_duration or (a.max_duration and secs > a.max_duration):
                    return False
            if w < a.min_width:
                return False
            return not a.vertical or h > w
        raw = (search(a.query, a.limit, keep, a.videos) if a.cmd == "search"
               else from_url(a.url, a.limit, keep, a.videos))
        pins = [summarize(p, a.size) for p in raw if keep(p)]
        if a.json:
            print(json.dumps(pins, ensure_ascii=False, indent=2))
        elif not a.out:
            print_list(pins)
        if a.out:
            download(pins, a.out, a.video or a.videos, a.min_width)
        if not pins:
            print("# nothing found", file=sys.stderr)
            sys.exit(1)
    except PinterestError as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
