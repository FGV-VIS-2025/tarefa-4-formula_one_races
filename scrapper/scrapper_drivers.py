import os
import time
import json
import requests
from urllib.parse import unquote

ROOT          = "img"
DRIVERS_DIR   = os.path.join(ROOT, "drivers")
DRIVERS_MAP   = os.path.join(DRIVERS_DIR, "drivers_mapping.json")

os.makedirs(DRIVERS_DIR, exist_ok=True)

try:
    with open(DRIVERS_MAP, "r", encoding="utf-8") as f:
        drivers_map = json.load(f)
except FileNotFoundError:
    drivers_map = {}

seen_drivers = set(drivers_map.keys())

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"})

def get_entities(season):
    """Retorna lista de pilotos via Ergast API."""
    url = f"http://ergast.com/api/f1/{season}/drivers.json?limit=1000"
    resp = session.get(url)
    resp.raise_for_status()
    return resp.json()["MRData"]["DriverTable"]["Drivers"]

def get_wiki_thumb(name, size=400):
    """Tenta pegar thumbnail do infobox da Wikipedia."""
    params = {
        "action": "query",
        "format": "json",
        "titles": name,
        "prop": "pageimages",
        "pithumbsize": size
    }
    try:
        r = session.get("https://en.wikipedia.org/w/api.php", params=params)
        r.raise_for_status()
    except requests.RequestException:
        return None

    pages = r.json().get("query", {}).get("pages", {})
    for p in pages.values():
        if "thumbnail" in p:
            return p["thumbnail"]["source"]
    return None

for season in range(2000, 2026):
    drivers = get_entities(season)
    for d in drivers:
        name = f"{d['givenName']} {d['familyName']}"
        if name in seen_drivers:
            continue

        thumb = get_wiki_thumb(name)
        if not thumb:
            continue

        ext   = os.path.splitext(thumb.split("?")[0])[1] or ".jpg"
        fname = f"{season}_{name.replace(' ', '_')}{ext}"
        path  = os.path.join(DRIVERS_DIR, fname)

        img_data = session.get(thumb).content
        with open(path, "wb") as f:
            f.write(img_data)

        drivers_map[name] = fname
        seen_drivers.add(name)
        print(f"✔️  Driver: {name} → {fname}")
        time.sleep(0.2)

    time.sleep(0.5)
with open(DRIVERS_MAP, "w", encoding="utf-8") as f:
    json.dump(drivers_map, f, ensure_ascii=False, indent=2)

print(f"\n🏁 Concluído: {len(drivers_map)} pilotos.")
