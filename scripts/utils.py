# Brasil Fut App/scripts/utils.py
import math
import unicodedata
import re


def ovr_from_mv(mv_eur: int) -> int:
    """Derive OVR (50–99) from market value in euros."""
    if mv_eur <= 0:
        return 55
    raw = 50 + math.log(mv_eur / 1_000_000 + 1) / math.log(300) * 49
    return max(50, min(99, round(raw)))


def salary_from_ovr(ovr: int) -> int:
    """Derive monthly salary (in-game currency) from OVR."""
    return int(1000 * 1.08 ** (ovr - 60))


_TM_POS_MAP = {
    'goalkeeper': 'GOL', 'gk': 'GOL',
    'centre-back': 'ZAG', 'central defender': 'ZAG', 'cb': 'ZAG', 'sweeper': 'ZAG',
    'right-back': 'LAT', 'left-back': 'LAT', 'full-back': 'LAT',
    'right back': 'LAT', 'left back': 'LAT', 'wing-back': 'LAT',
    'defensive midfield': 'VOL', 'defensive midfielder': 'VOL', 'holding midfield': 'VOL',
    'central midfield': 'MEI', 'central midfielder': 'MEI',
    'attacking midfield': 'MEI', 'attacking midfielder': 'MEI',
    'left midfield': 'MEI', 'right midfield': 'MEI',
    'left winger': 'ALA', 'right winger': 'ALA', 'winger': 'ALA',
    'centre-forward': 'ATA', 'striker': 'ATA', 'second striker': 'ATA',
    'centre forward': 'ATA', 'cf': 'ATA', 'st': 'ATA', 'fw': 'ATA',
}


def pos_from_tm(tm_position: str) -> str:
    """Map Transfermarkt position string to game position code."""
    key = tm_position.strip().lower()
    if key in _TM_POS_MAP:
        return _TM_POS_MAP[key]
    # Partial match
    for k, v in _TM_POS_MAP.items():
        if k in key:
            return v
    return 'MEI'  # Fallback


def normalize_brasfoot_ovr(raw: int) -> int:
    """Normalize Brasfoot OVR (scale ~30–220) to game scale (50–99)."""
    clamped = max(30, min(220, raw))
    return max(50, min(99, round(50 + (clamped - 30) / 190 * 49)))


def normalize_name(name: str) -> str:
    """Lowercase, strip accents, collapse spaces — for fuzzy matching."""
    nfkd = unicodedata.normalize('NFKD', name)
    no_accents = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', no_accents.lower()).strip()
