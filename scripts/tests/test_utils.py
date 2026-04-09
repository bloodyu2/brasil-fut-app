# Brasil Fut App/scripts/tests/test_utils.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import ovr_from_mv, salary_from_ovr, pos_from_tm, normalize_name


def test_ovr_from_mv_zero_returns_55():
    assert ovr_from_mv(0) == 55

def test_ovr_from_mv_one_million():
    result = ovr_from_mv(1_000_000)
    assert 55 <= result <= 68

def test_ovr_from_mv_100_million():
    result = ovr_from_mv(100_000_000)
    assert 82 <= result <= 92

def test_ovr_from_mv_200_million():
    assert ovr_from_mv(200_000_000) <= 99

def test_ovr_from_mv_negative_returns_55():
    assert ovr_from_mv(-1) == 55

def test_salary_from_ovr_60():
    assert salary_from_ovr(60) == 1000

def test_salary_from_ovr_increases_with_ovr():
    assert salary_from_ovr(70) > salary_from_ovr(60)
    assert salary_from_ovr(80) > salary_from_ovr(70)

def test_salary_from_ovr_50():
    assert salary_from_ovr(50) < 1000

def test_pos_from_tm_goalkeeper():
    assert pos_from_tm('Goalkeeper') == 'GOL'
    assert pos_from_tm('GK') == 'GOL'

def test_pos_from_tm_centre_back():
    assert pos_from_tm('Centre-Back') == 'ZAG'
    assert pos_from_tm('CB') == 'ZAG'

def test_pos_from_tm_fullback():
    assert pos_from_tm('Right-Back') == 'LAT'
    assert pos_from_tm('Left-Back') == 'LAT'
    assert pos_from_tm('Full-Back') == 'LAT'

def test_pos_from_tm_defensive_mid():
    assert pos_from_tm('Defensive Midfield') == 'VOL'
    assert pos_from_tm('Defensive Midfielder') == 'VOL'

def test_pos_from_tm_central_mid():
    assert pos_from_tm('Central Midfield') == 'MEI'
    assert pos_from_tm('Attacking Midfield') == 'MEI'

def test_pos_from_tm_winger():
    assert pos_from_tm('Left Winger') == 'ALA'
    assert pos_from_tm('Right Winger') == 'ALA'

def test_pos_from_tm_forward():
    assert pos_from_tm('Centre-Forward') == 'ATA'
    assert pos_from_tm('Second Striker') == 'ATA'

def test_pos_from_tm_unknown_returns_mei():
    assert pos_from_tm('Unknown Role') == 'MEI'

def test_normalize_name_strips_accents():
    assert normalize_name('Félix') == 'felix'

def test_normalize_name_lowercases():
    assert normalize_name('RODRIGO GARRO') == 'rodrigo garro'

def test_normalize_name_strips_extra_spaces():
    assert normalize_name('  Pedro  Henrique  ') == 'pedro henrique'
