"""
Parse Brasfoot .ban files (Java serialized binary).
Player format: 2-byte big-endian length + UTF-8 name + 30 metadata bytes.
  metadata[14] = OVR (Brasfoot scale, typically 50-200)
  metadata[18] = age (typically 15-45)
  metadata[22] = position code (0=GOL, 1=ZAG, 2=LAT, 3=MEI, 4=ATA)
"""
import struct
import logging
import unicodedata

log = logging.getLogger(__name__)

POS_CODE_MAP = {0: 'GOL', 1: 'ZAG', 2: 'LAT', 3: 'MEI', 4: 'ATA'}
META_LEN = 30
MIN_NAME_LEN = 2
MAX_NAME_LEN = 60
# Brasfoot OVR is on its own scale (not FIFA 0-99); real values observed 50-200+
MIN_OVR = 30
MAX_OVR = 255
MIN_AGE = 14
MAX_AGE = 45


def _looks_like_player_name(name: str) -> bool:
    """Heuristic: reject Java class field names and hex/code strings."""
    if not name:
        return False
    # Must be printable
    if not all(c.isprintable() for c in name):
        return False
    # Reject strings that look like Java identifiers or hex colors
    if name.startswith('#') or name.startswith('0x'):
        return False
    # Must contain at least one letter
    if not any(c.isalpha() for c in name):
        return False
    # Reject if mostly digits or special chars
    alpha_count = sum(1 for c in name if c.isalpha() or c in " '-.")
    if alpha_count < len(name) * 0.6:
        return False
    return True


def parse_ban_file(path: str) -> list[dict]:
    """Return list of {name, ovr, age, pos_code} dicts. Returns [] on error."""
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except (FileNotFoundError, PermissionError) as e:
        log.warning(f'Cannot open {path}: {e}')
        return []

    players = []
    i = 0
    while i < len(data) - 2:
        name_len = struct.unpack_from('>H', data, i)[0]
        if name_len < MIN_NAME_LEN or name_len > MAX_NAME_LEN:
            i += 1
            continue
        name_end = i + 2 + name_len
        meta_end = name_end + META_LEN
        if meta_end > len(data):
            i += 1
            continue
        try:
            name = data[i + 2:name_end].decode('utf-8')
        except UnicodeDecodeError:
            i += 1
            continue
        if not _looks_like_player_name(name):
            i += 1
            continue
        meta = data[name_end:meta_end]
        ovr = meta[14]
        age = meta[18]
        pos_code = meta[22]
        if not (MIN_OVR <= ovr <= MAX_OVR):
            i += 1
            continue
        if not (MIN_AGE <= age <= MAX_AGE):
            i += 1
            continue
        players.append({
            'name': name,
            'ovr': ovr,
            'age': age,
            'pos_code': pos_code,
        })
        i = meta_end
    return players
