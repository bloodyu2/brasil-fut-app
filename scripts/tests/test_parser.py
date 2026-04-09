import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from parser_ban import parse_ban_file

FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'mini.ban')


def test_parse_returns_list():
    players = parse_ban_file(FIXTURE)
    assert isinstance(players, list)


def test_parse_finds_all_players():
    players = parse_ban_file(FIXTURE)
    assert len(players) == 4


def test_parse_name():
    players = parse_ban_file(FIXTURE)
    names = [p['name'] for p in players]
    assert 'Hugo Souza' in names
    assert 'Felix Torres' in names


def test_parse_ovr():
    players = parse_ban_file(FIXTURE)
    hugo = next(p for p in players if p['name'] == 'Hugo Souza')
    assert hugo['ovr'] == 72


def test_parse_age():
    players = parse_ban_file(FIXTURE)
    felix = next(p for p in players if p['name'] == 'Felix Torres')
    assert felix['age'] == 28


def test_parse_position_goalkeeper():
    players = parse_ban_file(FIXTURE)
    hugo = next(p for p in players if p['name'] == 'Hugo Souza')
    assert hugo['pos_code'] == 0


def test_parse_position_mid():
    players = parse_ban_file(FIXTURE)
    garro = next(p for p in players if p['name'] == 'Garro')
    assert garro['pos_code'] == 3


def test_parse_skips_garbage_strings():
    players = parse_ban_file(FIXTURE)
    assert all(len(p['name']) > 0 for p in players)


def test_parse_missing_file_returns_empty():
    players = parse_ban_file('/nonexistent/path.ban')
    assert players == []
