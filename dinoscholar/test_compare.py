import urllib.request
import re

# Get species IDs from the encyclopedia page
resp = urllib.request.urlopen("http://127.0.0.1:5000/encyclopedia/")
html = resp.read().decode()
ids = list(set(re.findall(r'/encyclopedia/([a-z_-]+)', html)))
ids = [i for i in ids if i != "compare"]
print(f"Found {len(ids)} species IDs, first 5: {ids[:5]}")

# Try compare with two species
if len(ids) >= 2:
    url = f"http://127.0.0.1:5000/encyclopedia/compare?species={ids[0]}&species={ids[1]}"
    print(f"Testing: {url}")
    try:
        resp2 = urllib.request.urlopen(url)
        print(f"Status: {resp2.status}")
    except urllib.error.HTTPError as e:
        print(f"Status: {e.code}")
        body = e.read().decode()
        m = re.search(r'class="errormsg">(.*?)</p>', body, re.DOTALL)
        if m:
            clean = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            print(f"Error: {clean}")
        # Find traceback frames
        frames = re.findall(
            r'<div class="frame".*?<h4>File <cite class="filename">"(.*?)"</cite>,\s*line\s*<em>(\d+)</em>',
            body, re.DOTALL
        )
        for fname, line in frames:
            print(f"  {fname}:{line}")
