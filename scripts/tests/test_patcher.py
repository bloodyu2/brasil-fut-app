# Brasil Fut App/scripts/tests/test_patcher.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from patcher import find_team_players_span, replace_team_players, preserve_existing_contract_ends


SAMPLE_HTML = '''
const WORLD_DB = {"BRA":{"n":"Brasil","t":[["corinthians_bra","Corinthians",0,"#000","#fff",["Cássio|37","Felipe|28","Raul|24"]],["palmeiras","Palmeiras",0,"#028b4c","#fff",["Wéverton|37","Marcos Rocha|36"]]]}}
'''

NEW_PLAYERS = ['Mateus|23|65', 'Cacá|26|79', 'Rodrigo Garro|26|78']


def test_find_team_returns_span():
    start, end = find_team_players_span(SAMPLE_HTML, 'corinthians_bra')
    assert start >= 0
    assert end > start


def test_find_team_span_covers_player_array():
    start, end = find_team_players_span(SAMPLE_HTML, 'corinthians_bra')
    extracted = SAMPLE_HTML[start:end]
    assert 'Cássio|37' in extracted


def test_find_missing_team_returns_minus_one():
    s, e = find_team_players_span(SAMPLE_HTML, 'nonexistent_team')
    assert s == -1


def test_replace_team_players_updates_content():
    result = replace_team_players(SAMPLE_HTML, 'corinthians_bra', NEW_PLAYERS)
    assert 'Rodrigo Garro|26|78' in result
    assert 'Cacá|26|79' in result


def test_replace_does_not_touch_other_team():
    result = replace_team_players(SAMPLE_HTML, 'corinthians_bra', NEW_PLAYERS)
    assert 'Wéverton|37' in result


def test_replace_old_players_removed():
    result = replace_team_players(SAMPLE_HTML, 'corinthians_bra', NEW_PLAYERS)
    assert 'Cássio|37' not in result


def test_replace_nonexistent_team_returns_unchanged():
    result = replace_team_players(SAMPLE_HTML, 'ghost_team', NEW_PLAYERS)
    assert result == SAMPLE_HTML


def test_preserve_contract_ends_keeps_existing():
    existing = [{'name': 'Rodrigo Garro', 'contractEnd': 18}]
    new = [{'name': 'Rodrigo Garro|26|78'}]
    result = preserve_existing_contract_ends(new, existing)
    assert result[0].get('contractEnd') == 18


def test_preserve_contract_ends_leaves_new_players_alone():
    existing = []
    new = [{'name': 'New Player|22|70'}]
    result = preserve_existing_contract_ends(new, existing)
    assert 'contractEnd' not in result[0]
