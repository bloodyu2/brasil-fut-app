# Brasil Fut App/scripts/update_rosters.py
"""
Main pipeline: scrape Transfermarkt → cross-ref Brasfoot → patch brasil-fut.html.
Usage: python update_rosters.py [--dry-run] [--slug corinthians_bra]
"""
import argparse
import logging
import sys
import io
import os
import random
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

from team_map import TEAM_MAP
from scraper import fetch_squad
from parser_ban import parse_ban_file
from patcher import replace_team_players, extract_existing_players, preserve_existing_contract_ends
from utils import ovr_from_mv, salary_from_ovr, pos_from_tm, normalize_name, normalize_brasfoot_ovr

HTML_PATH = Path(__file__).parent.parent / 'brasil-fut.html'
BRASFOOT_DIR = Path(r'C:\Users\Victor Lima\Documents\Brasfoot22-23\teams')

SLOT_POSITIONS = [
    'GOL', 'ZAG', 'ZAG', 'LAT', 'LAT', 'VOL', 'VOL', 'MEI', 'MEI', 'ALA', 'ATA',
    'ZAG', 'LAT', 'MEI', 'VOL', 'ALA', 'ATA', 'GOL',
]


def load_brasfoot(slug: str) -> dict:
    """Return normalized_name → {name, ovr, age, pos_code} with OVR already on game scale."""
    ban_path = BRASFOOT_DIR / f'{slug}.ban'
    if not ban_path.exists():
        return {}
    players = parse_ban_file(str(ban_path))
    result = {}
    for p in players:
        norm = normalize_name(p['name'])
        result[norm] = {
            'name': p['name'],
            'ovr': normalize_brasfoot_ovr(p['ovr']),
            'age': p['age'],
            'pos_code': p['pos_code'],
        }
    return result


def pos_code_to_game(code: int) -> str:
    return {0: 'GOL', 1: 'ZAG', 2: 'LAT', 3: 'MEI', 4: 'ATA'}.get(code, 'MEI')


def assign_to_slots(players: list) -> list:
    """Assign enriched players to 18 WORLD_DB slots by position, best OVR first."""
    by_pos = {pos: [] for pos in ['GOL', 'ZAG', 'LAT', 'VOL', 'MEI', 'ALA', 'ATA']}
    for p in players:
        pos = p.get('pos', 'MEI')
        if pos not in by_pos:
            pos = 'MEI'
        by_pos[pos].append(p)

    for pos in by_pos:
        by_pos[pos].sort(key=lambda x: x['ovr'], reverse=True)

    all_sorted = sorted(players, key=lambda x: x['ovr'], reverse=True)
    used_ids = set()
    result = []

    for slot_pos in SLOT_POSITIONS:
        pool = [p for p in by_pos.get(slot_pos, []) if id(p) not in used_ids]
        if pool:
            chosen = pool[0]
        else:
            fallback = [p for p in all_sorted if id(p) not in used_ids]
            if not fallback:
                result.append('Player|22|65')
                continue
            chosen = fallback[0]
        used_ids.add(id(chosen))
        result.append(f"{chosen['name']}|{chosen['age']}|{chosen['ovr']}")

    return result[:18]


def process_team(slug: str, url_path: str, verein_id: int, html: str) -> tuple:
    """Scrape, cross-ref, and patch one team. Returns (updated_html, success)."""
    log.info(f'Processing {slug}...')

    tm_players = fetch_squad(slug, url_path, verein_id)
    if not tm_players:
        log.warning(f'  Skipping {slug} — no Transfermarkt data')
        return html, False

    bf_lookup = load_brasfoot(slug)
    existing = extract_existing_players(html, slug)

    enriched = []
    for p in tm_players:
        norm = normalize_name(p['name'])
        tm_pos = pos_from_tm(p.get('tm_position', ''))

        if norm in bf_lookup:
            bf = bf_lookup[norm]
            ovr = bf['ovr']  # already normalized
            # Prefer TM position if it resolves to ALA (Brasfoot has no wingers)
            pos = tm_pos if tm_pos == 'ALA' else pos_code_to_game(bf['pos_code'])
        else:
            ovr = ovr_from_mv(p.get('mv_eur', 0))
            pos = tm_pos

        age = p['age'] if p.get('age', 0) >= 15 else 22
        enriched.append({
            'name': p['name'],
            'age': age,
            'ovr': ovr,
            'pos': pos,
            'mv_eur': p.get('mv_eur', 0),
        })

    preserve_existing_contract_ends(enriched, existing)
    player_strings = assign_to_slots(enriched)
    updated = replace_team_players(html, slug, player_strings)

    if updated == html:
        log.warning(f'  No change for {slug} — slug not found in WORLD_DB?')
        return html, False

    log.info(f'  OK: {len(player_strings)} slots filled for {slug}')
    return updated, True


def main():
    parser = argparse.ArgumentParser(description='Update Brasil Fut App rosters from Transfermarkt')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing HTML')
    parser.add_argument('--slug', help='Process only this one team slug')
    args = parser.parse_args()

    with open(HTML_PATH, encoding='utf-8') as f:
        html = f.read()

    if args.slug:
        if args.slug not in TEAM_MAP:
            log.error(f'Slug "{args.slug}" not in TEAM_MAP')
            sys.exit(1)
        targets = {args.slug: TEAM_MAP[args.slug]}
    else:
        targets = TEAM_MAP

    updated_count = 0
    failed = []

    for slug, (url_path, verein_id) in targets.items():
        html, success = process_team(slug, url_path, verein_id, html)
        if success:
            updated_count += 1
        else:
            failed.append(slug)

    # Encoding spot-check
    all_names = re.findall(r'"([^"|]+)\|\d+\|\d+"', html)
    if all_names:
        sample = random.sample(all_names, min(20, len(all_names)))
        encoding_ok = True
        for name in sample:
            try:
                name.encode('utf-8')
            except UnicodeEncodeError as e:
                log.error(f'Encoding issue in name "{name}": {e}')
                encoding_ok = False
        if encoding_ok:
            log.info(f'Encoding spot-check OK ({len(sample)} names sampled)')

    if not args.dry_run:
        with open(HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(html)
        log.info(f'Wrote {HTML_PATH}')

    log.info(f'Done. Updated: {updated_count}, Failed: {len(failed)}')
    if failed:
        log.warning(f'Failed teams ({len(failed)}): {failed}')

    # Vercel file count check
    total_files = sum(len(files) for _, _, files in os.walk(HTML_PATH.parent))
    if total_files > 9500:
        log.warning(f'File count {total_files} approaching Vercel 10k limit!')


if __name__ == '__main__':
    main()
