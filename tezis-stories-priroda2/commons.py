# Поиск свободных фото на Wikimedia Commons с лицензией, допускающей коммерческое использование.
# python3 commons.py "pomegranate fruit" [n]
import json, sys, urllib.parse, urllib.request
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
UA = {'User-Agent': 'TEZIS-stories/1.0 (content preparation; free-licence photo search)'}
params = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': f'filetype:bitmap {q}', 'gsrnamespace': 6,
          'gsrlimit': 30, 'prop': 'imageinfo', 'iiprop': 'url|size|extmetadata', 'iiurlwidth': 1200}
url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
ok = ('cc0', 'public domain', 'pd', 'cc by 2', 'cc by 3', 'cc by 4', 'cc by-sa')
out = []
for p in data.get('query', {}).get('pages', {}).values():
    ii = p['imageinfo'][0]; md = ii.get('extmetadata', {})
    lic = md.get('LicenseShortName', {}).get('value', '')
    if ii['width'] < 1500 or not any(lic.lower().startswith(o) for o in ok): continue
    art = md.get('Artist', {}).get('value', '')
    import re; art = re.sub('<[^>]+>', '', art).strip()[:60]
    out.append(dict(title=p['title'], w=ii['width'], h=ii['height'], lic=lic, artist=art, thumb=ii['thumburl'], page=ii['descriptionurl']))
for o in out[:n]: print(json.dumps(o, ensure_ascii=False))
