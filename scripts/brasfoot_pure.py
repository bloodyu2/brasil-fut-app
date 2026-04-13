# scripts/brasfoot_pure.py
"""
Pure Brasfoot roster builder.
Reads ALL .ban files, matches slugs to WORLD_DB entries in brasil-fut.html,
and replaces player arrays with exact Brasfoot data (name, OVR, age, position).
No Transfermarkt. No random. No TEAM_MAP needed.

Usage:
    python brasfoot_pure.py               # process all matched teams
    python brasfoot_pure.py --slug saopaulo_bra  # single team
    python brasfoot_pure.py --dry-run     # print changes, don't write
"""
import sys
import io
import os
import re
import logging
import argparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from parser_ban import parse_ban_file
from patcher import replace_team_players
from utils import normalize_brasfoot_ovr

HTML_PATH = SCRIPTS_DIR.parent / 'brasil-fut.html'
BF_DIR    = Path(r'C:\Users\Victor Lima\Documents\Brasfoot22-23\teams')

# 18-slot layout: index → game position label (determines in-game role)
SLOT_POSITIONS = [
    'GOL',  # 0  starter GK
    'ZAG',  # 1  starter CB
    'ZAG',  # 2  starter CB
    'LAT',  # 3  starter LB
    'LAT',  # 4  starter RB
    'VOL',  # 5  starter DM
    'VOL',  # 6  starter DM
    'MEI',  # 7  starter CM
    'MEI',  # 8  starter CM
    'ALA',  # 9  starter winger
    'ATA',  # 10 starter striker
    'ZAG',  # 11 bench CB
    'LAT',  # 12 bench LB
    'MEI',  # 13 bench CM
    'VOL',  # 14 bench DM
    'ALA',  # 15 bench winger
    'ATA',  # 16 bench striker
    'GOL',  # 17 bench GK
]

# Brasfoot pos_code → slot indices to fill (priority order)
# MEI covers VOL, MEI, ALA — fill VOL first (more defensive), then MEI, then ALA
POS_TO_SLOTS = {
    'GOL': [0, 17],
    'ZAG': [1, 2, 11],
    'LAT': [3, 4, 12],
    'MEI': [5, 6, 7, 8, 9, 14, 13, 15],
    'ATA': [10, 16],
}


def pos_code_to_game(code: int) -> str:
    """Confirmed position mapping from real Brasfoot data investigation:
    0=GOL, 1=LAT (full backs), 2=ZAG (center backs), 3=MEI (midfielders), 4=ATA (forwards)
    """
    return {0: 'GOL', 1: 'LAT', 2: 'ZAG', 3: 'MEI', 4: 'ATA'}.get(code, 'MEI')


def load_ban(slug: str) -> list:
    """Parse .ban file for slug. Returns list of {name, ovr, raw_ovr, age, pos} dicts.
    raw_ovr is kept for tiebreaking when normalized OVR values collide (e.g. both map to 50).
    pos_code values > 4 are invalid (artifacts like stadiums) and are treated as MEI.
    """
    path = BF_DIR / f'{slug}.ban'
    if not path.exists():
        return []
    raw = parse_ban_file(str(path))
    result = []
    for p in raw:
        raw_ovr = p['ovr']
        ovr = normalize_brasfoot_ovr(raw_ovr)
        age = p['age'] if 14 <= p['age'] <= 45 else 22
        # pos_code > 4 means invalid/artifact (e.g. stadium names with code 97)
        pos_code = p['pos_code'] if p['pos_code'] <= 4 else 3  # treat as MEI
        pos = pos_code_to_game(pos_code)
        result.append({'name': p['name'], 'ovr': ovr, 'raw_ovr': raw_ovr, 'age': age, 'pos': pos})
    return result


def assign_slots(players: list) -> list:
    """Assign players to 18 game slots. Best OVR first within each position group."""
    # Group by game position, sorted by OVR descending
    by_pos = {'GOL': [], 'ZAG': [], 'LAT': [], 'MEI': [], 'ATA': []}
    for p in players:
        pos = p['pos'] if p['pos'] in by_pos else 'MEI'
        by_pos[pos].append(p)
    for grp in by_pos.values():
        grp.sort(key=lambda x: (x['ovr'], x.get('raw_ovr', 0)), reverse=True)

    slots = [None] * 18
    used = set()

    def pick(grp):
        for p in grp:
            if p['name'] not in used:
                return p
        return None

    for bf_pos, slot_indices in POS_TO_SLOTS.items():
        grp = by_pos[bf_pos]
        for idx in slot_indices:
            player = pick(grp)
            if player:
                slots[idx] = f"{player['name']}|{player['age']}|{player['ovr']}"
                used.add(player['name'])

    # Fill remaining empty slots — GOL slots (0, 17) only accept goalkeepers
    gol_slots = {0, 17}
    gol_pool   = sorted([p for p in players if p['pos'] == 'GOL'], key=lambda x: x['ovr'], reverse=True)
    field_pool = sorted([p for p in players if p['pos'] != 'GOL'], key=lambda x: x['ovr'], reverse=True)

    for i, s in enumerate(slots):
        if s is None:
            pool = gol_pool if i in gol_slots else field_pool
            fb = next((p for p in pool if p['name'] not in used), None)
            if fb:
                slots[i] = f"{fb['name']}|{fb['age']}|{fb['ovr']}"
                used.add(fb['name'])
            else:
                slots[i] = 'Reserva|22|50'

    return slots


def get_all_game_slugs(html: str) -> set:
    """Extract all team slugs present in WORLD_DB."""
    return set(re.findall(r'\["([a-z][a-z0-9_]*)","\s*[^"]+\s*",\s*\d\s*,', html))


def main():
    parser = argparse.ArgumentParser(description='Pure Brasfoot roster builder')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing HTML')
    parser.add_argument('--slug', help='Process only this one team slug')
    args = parser.parse_args()

    with open(HTML_PATH, encoding='utf-8') as f:
        html = f.read()

    game_slugs = get_all_game_slugs(html)
    log.info(f'Game has {len(game_slugs)} teams in WORLD_DB')

    if args.slug:
        if args.slug not in game_slugs:
            log.error(f'Slug "{args.slug}" not found in WORLD_DB')
            sys.exit(1)
        targets = [args.slug]
    else:
        ban_files = [f.stem for f in BF_DIR.glob('*.ban')]
        targets = sorted(set(ban_files) & game_slugs)
        log.info(f'Found {len(ban_files)} .ban files, {len(targets)} match game teams')

    ok = 0
    skipped = 0

    for slug in targets:
        players = load_ban(slug)
        if not players:
            log.warning(f'SKIP {slug} — parse returned 0 players')
            skipped += 1
            continue
        player_strings = assign_slots(players)
        new_html = replace_team_players(html, slug, player_strings)
        if new_html == html:
            log.warning(f'SKIP {slug} — patcher found no match in HTML')
            skipped += 1
            continue
        html = new_html
        ok += 1
        if ok % 100 == 0:
            log.info(f'  Progress: {ok} teams patched...')

    log.info(f'Done — patched: {ok}, skipped: {skipped}')

    if not args.dry_run:
        with open(HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(html)
        log.info(f'Saved {HTML_PATH}')
    else:
        log.info('[dry-run] HTML not written')


if __name__ == '__main__':
    main()
