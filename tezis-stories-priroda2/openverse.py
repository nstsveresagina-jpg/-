# Поиск фото со свободной лицензией для коммерческого использования (Openverse).
# python3 openverse.py "query" out_dir prefix [n]
import json, os, sys, urllib.parse, urllib.request
q, out, pre = sys.argv[1:4]; n = int(sys.argv[4]) if len(sys.argv) > 4 else 6
os.makedirs(out, exist_ok=True)
UA = {'User-Agent': 'TEZIS-stories/1.0 (free-licence photo search)'}
p = {'q': q, 'license_type': 'commercial', 'category': 'photograph', 'size': 'large', 'page_size': 20, 'mature': 'false'}
url = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode(p)
res = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))['results']
meta = []
for i, r in enumerate(res[:n]):
    f = os.path.join(out, f'{pre}_{i}.jpg')
    try:
        data = urllib.request.urlopen(urllib.request.Request(r['thumbnail'], headers=UA), timeout=40).read()
        open(f, 'wb').write(data)
        meta.append(dict(file=f, title=r['title'], creator=r.get('creator'), license=f"{r['license']} {r.get('license_version', '')}",
                         url=r['url'], page=r['foreign_landing_url'], w=r.get('width'), h=r.get('height')))
    except Exception as e:
        print('skip', e)
json.dump(meta, open(os.path.join(out, pre + '.json'), 'w'), ensure_ascii=False, indent=1)
print(pre, len(meta))
