"""
Scrape squad data from Transfermarkt with file-based caching.
Cache files: scripts/cache/<slug>.json  (expires after 7 days)
"""
import json
import time
import random
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).parent / 'cache'
CACHE_TTL_DAYS = 7
BASE_URL = 'https://www.transfermarkt.com'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
    'Accept': 'text/html,application/xhtml+xml',
    'Referer': 'https://www.transfermarkt.com/',
}


def _cache_path(slug: str) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR / f'{slug}.json'


def _is_cache_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - mtime < timedelta(days=CACHE_TTL_DAYS)


def _parse_market_value(raw: str) -> int:
    """Parse '€45.00m', '€750Th.', '€1.20bn' → integer euros. Returns 0 on failure."""
    raw = raw.strip().replace('\u20ac', '').replace(',', '.').lower()
    try:
        if 'bn' in raw:
            return int(float(raw.replace('bn', '').strip()) * 1_000_000_000)
        elif 'm' in raw:
            return int(float(raw.replace('m', '').strip()) * 1_000_000)
        elif 'th.' in raw or 'k' in raw:
            return int(float(raw.replace('th.', '').replace('k', '').strip()) * 1_000)
        else:
            return int(float(raw))
    except (ValueError, AttributeError):
        return 0


def fetch_squad(slug: str, url_path: str, verein_id: int) -> list[dict]:
    """
    Return squad as list of {name, age, tm_position, mv_eur}.
    Uses cache if fresh; fetches from Transfermarkt otherwise.
    """
    cache = _cache_path(slug)
    if _is_cache_fresh(cache):
        log.info(f'  [cache] {slug}')
        with open(cache, encoding='utf-8') as f:
            return json.load(f)

    url = f'{BASE_URL}/{url_path}/kader/verein/{verein_id}/saison_id/2024/plus/1'
    log.info(f'  [fetch] {slug} — {url}')
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warning(f'  Failed to fetch {slug}: {e}')
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    players = []

    # Transfermarkt squad table: each player row has class 'odd' or 'even'
    rows = soup.select('table.items tbody tr.odd, table.items tbody tr.even')

    for row in rows:
        # Name — current TM structure: td.posrela > inline-table > td.hauptlink > a
        name_tag = row.select_one('td.posrela td.hauptlink a')
        if not name_tag:
            # Legacy fallback
            name_tag = row.select_one('a.spielprofil_tooltip')
        if not name_tag:
            continue
        name = name_tag.get_text(strip=True)

        # Age — extracted from the date cell which has format "DD/MM/YYYY (age)"
        age = 0
        for cell in row.select('td.zentriert'):
            m = re.search(r'\((\d+)\)', cell.get_text(strip=True))
            if m:
                age = int(m.group(1))
                break

        # Position — second row of inline-table inside posrela cell
        pos_td = row.select_one('td.posrela table.inline-table tr:nth-child(2) td')
        tm_position = pos_td.get_text(strip=True) if pos_td else ''

        # Market value — td with both classes rechts and hauptlink (no nested <a> needed)
        mv_td = row.select_one('td.rechts.hauptlink')
        mv_raw = mv_td.get_text(strip=True) if mv_td else '0'
        mv_eur = _parse_market_value(mv_raw)

        if name:
            players.append({
                'name': name,
                'age': age,
                'tm_position': tm_position,
                'mv_eur': mv_eur,
            })

    if not players:
        log.warning(f'  No players parsed for {slug} — check HTML structure')
        log.debug(f'  HTML snippet: {resp.text[:2000]}')
        return []

    with open(cache, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    # Rate limiting
    time.sleep(random.uniform(2.5, 4.5))
    return players
