# Brasil Fut App/scripts/patcher.py
"""
Patch WORLD_DB player arrays in brasil-fut.html.
Locates each team entry by slug and replaces its players list with new data.
"""
import re
import logging
from utils import normalize_name

log = logging.getLogger(__name__)


def find_team_players_span(html: str, slug: str) -> tuple[int, int]:
    """
    Find the start and end indices of the players array for `slug` in WORLD_DB.
    The team entry looks like: ["slug","Name",div,"#color","#color",["player1","player2",...]]
    Returns (-1, -1) if not found.
    """
    pattern = rf'(?<!\w)"{re.escape(slug)}"'
    m = re.search(pattern, html)
    if not m:
        return -1, -1

    # From the slug position, find the player array start: the 6th element is players
    # Walk forward to find 5 commas then the opening [
    pos = m.end()
    commas = 0
    while pos < len(html) and commas < 5:
        if html[pos] == ',':
            commas += 1
        pos += 1

    # Skip whitespace to find '['
    while pos < len(html) and html[pos] in ' \t\n\r':
        pos += 1

    if pos >= len(html) or html[pos] != '[':
        return -1, -1

    # Find matching closing ']' using bracket counting
    start = pos
    depth = 0
    i = pos
    while i < len(html):
        if html[i] == '[':
            depth += 1
        elif html[i] == ']':
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    return -1, -1


def replace_team_players(html: str, slug: str, new_players: list[str]) -> str:
    """
    Replace the players array for `slug` with `new_players`.
    `new_players` is a list of strings like "Name|age|ovr".
    Returns unchanged html if slug not found.
    """
    start, end = find_team_players_span(html, slug)
    if start == -1:
        log.warning(f'Team slug not found in HTML: {slug}')
        return html

    items = ', '.join(f'"{p}"' for p in new_players)
    new_array = f'[{items}]'
    return html[:start] + new_array + html[end:]


def preserve_existing_contract_ends(
    new_players: list[dict],
    existing_players: list[dict],
) -> list[dict]:
    """
    For players that exist in both lists (matched by normalized name),
    copy contractEnd from the existing player into the new player dict.
    """
    existing_map = {normalize_name(p['name'].split('|')[0]): p for p in existing_players}
    for p in new_players:
        raw_name = p['name'].split('|')[0]
        key = normalize_name(raw_name)
        if key in existing_map and 'contractEnd' in existing_map[key]:
            p['contractEnd'] = existing_map[key]['contractEnd']
    return new_players


def extract_existing_players(html: str, slug: str) -> list[dict]:
    """
    Extract current player strings from WORLD_DB for a team.
    Returns list of dicts with 'name' and optionally 'contractEnd'.
    """
    start, end = find_team_players_span(html, slug)
    if start == -1:
        return []
    array_str = html[start:end]
    names = re.findall(r'"([^"]+)"', array_str)
    return [{'name': n} for n in names]
