# Brasil Fut App/scripts/update_rosters.py
"""
Main pipeline: Brasfoot .ban (primary squad) + Transfermarkt (market value enrichment) → patch brasil-fut.html.
Usage: python update_rosters.py [--dry-run] [--slug corinthians_bra]

Priority:
  1. Brasfoot .ban file → correct player names, OVR, position, age
  2. Transfermarkt → market value enrichment (optional; best-effort by name match)
  3. If no Brasfoot file → fall back to TM-only (for European clubs not in Brasfoot)
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


def load_brasfoot_squad(slug: str) -> list:
    """Return all players from .ban file as list of enriched dicts (OVR already on game scale)."""
    ban_path = BRASFOOT_DIR / f'{slug}.ban'
    if not ban_path.exists():
        return []
    raw = parse_ban_file(str(ban_path))
    result = []
    for p in raw:
        result.append({
            'name': p['name'],
            'ovr': normalize_brasfoot_ovr(p['ovr']),
            'age': p['age'] if 14 <= p['age'] <= 45 else 22,
            'pos': pos_code_to_game(p['pos_code']),
            'mv_eur': 0,
        })
    return result


def pos_code_to_game(code: int) -> str:
    # Observed from real Brasfoot data: 1=LAT (full backs), 2=ZAG (center backs)
    return {0: 'GOL', 1: 'LAT', 2: 'ZAG', 3: 'MEI', 4: 'ATA'}.get(code, 'MEI')


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
    used_names = set()
    result = []

    for slot_pos in SLOT_POSITIONS:
        pool = [p for p in by_pos.get(slot_pos, []) if normalize_name(p['name']) not in used_names]
        if pool:
            chosen = pool[0]
        else:
            fallback = [p for p in all_sorted if normalize_name(p['name']) not in used_names]
            if not fallback:
                result.append('Player|22|65')
                continue
            chosen = fallback[0]
        used_names.add(normalize_name(chosen['name']))
        result.append(f"{chosen['name']}|{chosen['age']}|{chosen['ovr']}")

    return result[:18]


def process_team(slug: str, url_path: str, verein_id: int, html: str) -> tuple:
    """
    Brasfoot-primary pipeline:
      1. Load Brasfoot squad (correct player names + OVR)
      2. Enrich with TM market values by name match (best-effort)
      3. Fall back to TM-only if no Brasfoot file exists
    Returns (updated_html, success).
    """
    log.info(f'Processing {slug}...')

    # ── 1. Primary source: Brasfoot ──────────────────────────────────────────
    bf_players = load_brasfoot_squad(slug)

    # ── 2. Secondary: Transfermarkt market values (always try, even if BF has data) ──
    tm_players = fetch_squad(slug, url_path, verein_id)
    tm_by_name = {normalize_name(p['name']): p for p in tm_players}

    existing = extract_existing_players(html, slug)

    if bf_players:
        # Brasfoot is truth — enrich with TM market values where names match
        for p in bf_players:
            norm = normalize_name(p['name'])
            tm = tm_by_name.get(norm)
            if tm:
                p['mv_eur'] = tm.get('mv_eur', 0) or 0
                # Update age from TM if it looks more current (and valid)
                if tm.get('age', 0) >= 15:
                    p['age'] = tm['age']
        enriched = bf_players
        log.info(f'  Brasfoot: {len(bf_players)} players; TM enriched {sum(1 for p in bf_players if p["mv_eur"]>0)}')
    elif tm_players:
        # No Brasfoot file — fall back to TM-only (European clubs)
        enriched = []
        for p in tm_players:
            enriched.append({
                'name': p['name'],
                'age': p['age'] if p.get('age', 0) >= 15 else 22,
                'ovr': ovr_from_mv(p.get('mv_eur', 0)),
                'pos': pos_from_tm(p.get('tm_position', '')),
                'mv_eur': p.get('mv_eur', 0),
            })
        log.info(f'  TM-only (no Brasfoot): {len(enriched)} players')
    else:
        log.warning(f'  Skipping {slug} — no data from Brasfoot or Transfermarkt')
        return html, False

    preserve_existing_contract_ends(enriched, existing)
    player_strings = assign_to_slots(enriched)
    updated = replace_team_players(html, slug, player_strings)

    if updated == html:
        log.warning(f'  No change for {slug} — slug not found in WORLD_DB?')
        return html, False

    log.info(f'  OK: {len(player_strings)} slots patched for {slug}')
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
