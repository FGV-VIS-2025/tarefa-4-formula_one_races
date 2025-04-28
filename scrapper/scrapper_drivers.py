
import os, re, json, time, itertools, logging
from pathlib import Path
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from tqdm import tqdm   # barra de progresso elegante

# --------------------------------------------------------------------------- #
# 1. CONFIGURAÇÃO GERAL
# --------------------------------------------------------------------------- #
ROOT          = Path("img")
DRIVERS_DIR   = ROOT / "drivers"
TEAMS_DIR     = ROOT / "teams"
DRIVERS_MAP   = DRIVERS_DIR / "drivers_mapping.json"
TEAMS_LOGOS   = TEAMS_DIR / "constructors_logos.json"

try:
    from bs4 import BeautifulSoup
    BS_PARSER = "lxml"
except Exception:           # lxml ausente
    from bs4 import BeautifulSoup
    BS_PARSER = "html.parser"

for p in (DRIVERS_DIR, TEAMS_DIR):
    p.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# --------------------------------------------------------------------------- #
# 2. SESSÃO HTTP ROBUSTA
# --------------------------------------------------------------------------- #
session = requests.Session()
retry_strategy = Retry(
    total          = 5,
    backoff_factor = 1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://",  adapter)
session.mount("https://", adapter)
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; F1Scraper/1.0)"})

def safe_get(url, **kw):
    """GET com tratamento de exceção + log; retorna Response ou None."""
    try:
        resp = session.get(url, timeout=10, **kw)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        logging.warning("❌ Request failed for %s – %s", url, e)
        return None

# --------------------------------------------------------------------------- #
# 3. UTILITÁRIOS TEXTO / DATA
# --------------------------------------------------------------------------- #
team_year_re = re.compile(r"^(.*?):\s*([\d–\-\u2013, ]+)$")        # en-dash ou hyphen
slugify       = lambda n: "-".join(n.lower().split())

def expand_years(span: str):
    """'1998–2000, 2002' → [1998,1999,2000,2002]"""
    years = set()
    for part in span.replace(" ", "").split(","):
        if not part:
            continue
        if "–" in part or "-" in part:
            a, b = re.split("[–-]", part)
            years.update(range(int(a), int(b)+1))
        else:
            years.add(int(part))
    return sorted(years)

# --------------------------------------------------------------------------- #
# 4. RACEFANS → EQUIPES × ANOS
# --------------------------------------------------------------------------- #
def get_driver_teams_racefans(name: str) -> dict[int, str]:
    url  = f"https://www.racefans.net/f1-information/drivers/{slugify(name)}/"
    resp = safe_get(url)
    if not resp:
        return {}
    soup = BeautifulSoup(resp.text, BS_PARSER)

    header = soup.find(lambda t: t.name in ("h2", "h3") and "Teams" in t.text)
    if not header:
        return {}

    ul = header.find_next("ul")
    if not ul:
        return {}

    mapping = {}
    for li in ul.find_all("li"):
        m = team_year_re.match(li.get_text(strip=True))
        if m:
            team, span = m.groups()
            for yr in expand_years(span):
                mapping[yr] = team.strip()
    return mapping


# --------------------------------------------------------------------------- #
# 5. Fallback: ERGAST → EQUIPES × ANOS
# --------------------------------------------------------------------------- #
def get_driver_teams_ergast(driver_id: str) -> dict[int, str]:
    """
    Consulta ano a ano (1950-2025) via Ergast:
        /{year}/drivers/{driverId}/constructors.json
    Mais lento, só usar se RaceFans falhar.
    """
    mapping = {}
    for yr in range(2000, 2026):
        url = f"http://ergast.com/api/f1/{yr}/drivers/{driver_id}/constructors.json"
        resp = safe_get(url, params={"limit": 10})
        if not resp:
            continue
        data = resp.json()["MRData"]["ConstructorTable"]["Constructors"]
        if data:
            mapping[yr] = data[0]["name"]
        time.sleep(0.05)
    return mapping

# --------------------------------------------------------------------------- #
# 6. ERGAST → LISTA DE PILOTOS POR TEMPORADA
# --------------------------------------------------------------------------- #
def get_ergast_drivers(season: int) -> list[dict]:
    url = f"http://ergast.com/api/f1/{season}/drivers.json?limit=1000"
    resp = safe_get(url)
    if not resp:
        return []
    return resp.json()["MRData"]["DriverTable"]["Drivers"]

# --------------------------------------------------------------------------- #
# 7. WIKIPEDIA → THUMBNAIL PILOTO
# --------------------------------------------------------------------------- #
def get_wikipedia_thumb(name: str, size=400):
    params = {
        "action": "query",
        "format": "json",
        "titles": name,
        "prop": "pageimages",
        "pithumbsize": size,
    }
    resp = safe_get("https://en.wikipedia.org/w/api.php", params=params)
    if not resp:
        return None
    pages = resp.json().get("query", {}).get("pages", {})
    for p in pages.values():
        if "thumbnail" in p:
            return p["thumbnail"]["source"]
    return None

# --------------------------------------------------------------------------- #
# 8. SEEKLOGO → LOGO DE CONSTRUTOR
# --------------------------------------------------------------------------- #
def get_seeklogo_url(team: str):
    search_url = f"https://seeklogo.com/search?q={quote_plus(team)}"
    resp = safe_get(search_url, headers={"Referer": "https://seeklogo.com/"})
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, "lxml")
    img = soup.select_one("ul.logoGroupCt img.logoImage")
    if img and img.get("src"):
        return img["src"]
    return None

def download_logo(team: str) -> str | None:
    """Salva logo e retorna filename salvo (ou None)."""
    url = get_seeklogo_url(team)
    if not url:
        logging.warning("⚠️  Logo não encontrado p/ %s", team)
        return None
    ext = os.path.splitext(url.split("?")[0])[1] or ".png"
    fname = f"{team.replace(' ', '_')}{ext}"
    path  = TEAMS_DIR / fname
    if path.exists():
        return fname
    resp = safe_get(url)
    if not resp:
        return None
    with open(path, "wb") as f:
        f.write(resp.content)
    logging.info("✔️  Logo %s baixado", team)
    time.sleep(0.2)
    return fname

# --------------------------------------------------------------------------- #
# 9. CARREGA/SALVA JSON SEGURO
# --------------------------------------------------------------------------- #
def load_json(path: Path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error("❌ Falha abrindo %s – %s (sobrescrevendo)", path, e)
    return default

def save_json(path: Path, data):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

# --------------------------------------------------------------------------- #
# 10. MAIN
# --------------------------------------------------------------------------- #
def main():
    drivers_map   = load_json(DRIVERS_MAP, {})
    team_logo_map = load_json(TEAMS_LOGOS, {})
    seen_drivers  = set(drivers_map)

    # ---------- LOOP TEMPORADAS / PILOTOS ---------- #
    for season in range(2000, 2026):
        logging.info("===== Temporada %d =====", season)
        drivers = get_ergast_drivers(season)
        if not drivers:
            logging.warning("⚠️  Skipping season %d (sem dados)", season)
            continue

        for d in tqdm(drivers, desc=f"{season}", unit="piloto"):
            name      = f"{d['givenName']} {d['familyName']}"
            driver_id = d["driverId"]
            entry     = drivers_map.setdefault(name, {})

            if not isinstance(entry, dict):
                entry = {"thumb": entry}            # aproveita a string antiga como 'thumb'
                drivers_map[name] = entry

            # 1️⃣ THUMBNAIL
            if "thumb" not in entry:
                thumb_url = get_wikipedia_thumb(name)
                if thumb_url:
                    ext   = os.path.splitext(thumb_url.split("?")[0])[1] or ".jpg"
                    fname = f"{season}_{slugify(name)}{ext}"
                    path  = DRIVERS_DIR / fname
                    if not path.exists():
                        img = safe_get(thumb_url)
                        if img:
                            with open(path, "wb") as f: f.write(img.content)
                            logging.info("✔️  Foto %s", name)
                            time.sleep(0.1)
                    entry["thumb"] = fname
                else:
                    logging.debug("⚠️  Sem thumbnail %s", name)

            # 2️⃣ EQUIPES × ANOS
            if "teams" not in entry:
                teams = get_driver_teams_racefans(name)
                if not teams:
                    teams = get_driver_teams_ergast(driver_id)
                entry["teams"] = teams

            seen_drivers.add(name)

        time.sleep(0.5)  # respiro entre temporadas

    # ---------- LOOP LOGOS DE EQUIPES ---------- #
    all_teams = set(itertools.chain.from_iterable(
        d.get("teams", {}).values() for d in drivers_map.values()
    ))

    logging.info("===== Logos de Construtores (%d) =====", len(all_teams))
    for team in tqdm(sorted(all_teams), unit="equipe"):
        if team in team_logo_map:
            continue
        fname = download_logo(team)
        if fname:
            team_logo_map[team] = fname

    # ---------- SALVA JSONs ---------- #
    save_json(DRIVERS_MAP, drivers_map)
    save_json(TEAMS_LOGOS, team_logo_map)
    logging.info("🏁 Concluído – %d pilotos, %d equipes.",
                 len(drivers_map), len(team_logo_map))

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("❌ Interrompido pelo usuário.")
