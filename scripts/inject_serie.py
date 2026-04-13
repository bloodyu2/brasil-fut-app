"""
inject_serie.py
Injects real Brasfoot player data into ALL Brazilian league team definitions
(SERIE_A, SERIE_B, SERIE_C, SERIE_D, BRA_EST_TEAMS) in brasil-fut.html.

Strategy:
  1. Extract all team IDs from the JS arrays
  2. Attempt to find a .ban file for each ID via several strategies
  3. Parse matched .ban files -> 18-slot player strings
  4. Inject a `const REAL_ROSTERS = {...}` block into the HTML
  5. Patch buildSquad() to use buildSquadFromNames() when real data exists

Usage:
    python inject_serie.py               # patch all matched teams
    python inject_serie.py --dry-run     # print matches, don't write
    python inject_serie.py --show-map    # print the ID → ban mapping
"""
import sys, io, re, logging, argparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from parser_ban import parse_ban_file
from utils import normalize_brasfoot_ovr

HTML_PATH = SCRIPTS_DIR.parent / 'brasil-fut.html'
BF_DIR    = Path(r'C:\Users\Victor Lima\Documents\Brasfoot22-23\teams')

# ── MANUAL OVERRIDES (team id → ban stem) ─────────────────────────────────
# Cases where auto-matching fails because the slug doesn't match the ID
MANUAL_MAP = {
    # ── Série A ──
    'flamengo':      'flarj',
    'fluminense':    'flurj',
    'botafogo':      'botafogorj_bra',
    'saopaulo':      'saopaulo_bra',
    'atleticomg':    'atleticomg_bra',
    'internacional': 'internacional_bra',
    'corinthians':   'corinthians_bra',
    'cruzeiro':      'cruzeiro_bra',
    'atleticopr':    'atleticopr_bra',
    'bragantino':    'bragantino_bra',
    'criciuma':      'criciuma_bra',
    'atleticogo':    'atleticogo_bra',
    'cuiaba':        'cuiaba_bra',
    # ── Série B ──
    'coritiba':      'coritiba_bra',
    'ceara':         'ceara_bra',
    'chapecoense':   'chapecoense_bra',
    'avai':          'avai_bra',
    'americamg':     'americamg_bra',
    'ponte':         'pontepreta_bra',
    'botafogosp':    'botafogosp_bra',
    'crb':           'crb_bra',
    'operario':      'operario_pr',
    'sampaio':       'sampaiocorrea_rj',
    'guarani':       'guaranisp_bra',
    'csa':           'csa_bra',
    # ── Série C ──
    'botafogopb':    'botafogopb_bra',
    'abc':           'abcrn_bra',
    'ferroviario':   'ferroviarioce_bra',
    'saobernardo':   'saobernardo_sp',
    'ituano':        'ituano_sp',
    'voltaredonda':  'voltaredondarj_bra',
    'londrina':      'londrina_pr',
    'tombense':      'tombense_mg',
    'portuguesa':    'portuguesasp_bra',
    'aparecidense':  'aparecidense_go',
    'confianca':     'confianca_se',
    'treze':         'trezepb_bra',
    'ypiranga':      'ypiranga_rs',
    'campinense':    'campinensepb_bra',
    'sousa':         'sousapb_bra',
    # ── Série D ──
    'americago':     'americago_bra',
    'brasiliense':   'brasiliense_df_bra',
    'luverdense':    'luverdensemt_bra',
    'operariodourad':'operariodourados_bra',
    'anapolis':      'anapolisgo_bra',
    'tocantinsfc':   'tocantinsfc_bra',
    'rondoniense':   'rondoniense_bra',
    'castanhalpa':   'castanhalpa_bra',
    'novoperario':   'novoperario_bra',
    'cracgo':        'cracgo_bra',
    'saojosers':     'saojosers_bra',
    'esportivors':   'esportivors_bra',
    'toledopr':      'toledopr_bra',
    'jacuipense':    'jacuipense_bra',
    'vitoriaconq':   'vitoriaconquista_bra',
    'coimbramg':     'coimbramg_bra',
    'tapajospa':     'tapajospa_bra',
    # ── BRA_EST_TEAMS ──
    'americanorj':   'americanorj_bra',
    'fluminenseba':  'fluminenseba_bra',
    'vitoriape':     'vitoriape_bra',
    'gremiomauasp':  'gremiomauasp_bra',
    'gremiobarueri': 'gremiobaruerisp_bra',
    'guaranisc':     'guaranisc_bra',
    'boavistajf':    'boavista_bra',
    'jequieense':    'jequieenseba_bra',
    'guaranysobral': 'guaranysobralce_bra',
    'tuntumpa':      'tuntumma_bra',
    # ── INTER_SA — Argentina ──
    'riverplate':    'riverplate_arg',
    'boca':          'bocajuniors_arg',
    'racing':        'racing_arg',
    'independiente': 'independiente_arg',
    'sanlorenzo':    'sanlorenzo_ar',
    'talleres':      'talleres_arg',
    'estudiantes':   'estudiantes_ar',
    'velezarg':      'velezsarsfield_arg',
    'humancan':      'huracan_arg',
    'lalanarg':      'lanus_arg',
    # ── INTER_SA — Uruguay ──
    'penyarol':      'penarol_uru',
    'nacional':      'nacional_uru',
    'defensor':      'defensor_uru',
    'danubio':       'danubio_uru',
    # ── INTER_SA — Colombia ──
    'atleticonac':   'nacional_col',
    'millonarios':   'millonarios_col',
    'juniorcol':     'junior_col',
    'americacali':   'americacali_col',
    # ── INTER_SA — Chile ──
    'colocolo':      'colocolo_chi',
    'udechile':      'universidadchile_chi',
    # ── INTER_SA — Paraguay ──
    'olimpiapar':    'olimpia_par',
    'cerroporteno':  'cerroporteno_par',
    'libertadpar':   'libertad_par',
    # ── INTER_SA — Ecuador ──
    'ldqecu':        'ldu_equ',
    # ── INTER_SA — Bolivia ──
    'bolivarbol':    'bolivar_bol',
    'thestrongest':  'thestrongest_bol',
    # ── INTER_SA — Venezuela ──
    'caracasfc':     'caracas_ven',
    # ── INTER_SA — Peru ──
    'alianzalima':   'alianzalima_per',
    'universitario': 'universitario_per',
    'sportingcristal':'sportingcristal_per',
    # ── BRA_EST_TEAMS / Série C / D additional ──
    'cearense':      'ferroviarioce_bra',   # Ferroviário-CE (id 'cearense' in SERIE_C)
    'altos':         'altos_pi',
    'gama':          'gama_df_bra',
    'taguatinga':    'taguatinga_df_bra',
    'sobradinho':    'sobradinho_df_bra',
    'ceilandia':     'ceilandia_df_bra',
    'maranhao':      'maranhaoma_bra',
    'potiguarrn2':   'potyguarrn_bra',
    'palmas':        'palmas_to',
    'sergipese':     'sergipe_se',
    'confiancase':   'confianca_se',
}

# ── POSITION ENCODING ─────────────────────────────────────────────────────
SLOT_POSITIONS = [
    'GOL','ZAG','ZAG','LAT','LAT','VOL','VOL','MEI','MEI','ALA','ATA',
    'ZAG','LAT','MEI','VOL','ALA','ATA','GOL',
]
POS_TO_SLOTS = {
    'GOL': [0, 17],
    'ZAG': [1, 2, 11],
    'LAT': [3, 4, 12],
    'MEI': [5, 6, 7, 8, 9, 14, 13, 15],
    'ATA': [10, 16],
}

def pos_code_to_game(code: int) -> str:
    return {0:'GOL', 1:'LAT', 2:'ZAG', 3:'MEI', 4:'ATA'}.get(code, 'MEI')

_STADIUM_WORDS = {'maracanã','arena','estádio','estadio','stadium','campo','vila','parque','couto','mineirão',
                  'mineiro','morumbi','itaquerão','pacaembu','beira-rio','beeirafeito','allianz','neo quimica'}

def _is_player_name(name: str) -> bool:
    """Return False for obvious stadium/infrastructure artifacts."""
    low = name.strip().lower()
    for word in _STADIUM_WORDS:
        if word in low:
            return False
    # Names with more than 3 words are suspicious (stadium descriptions)
    if len(low.split()) > 4:
        return False
    return True

def parse_ban(stem: str) -> list:
    path = BF_DIR / f'{stem}.ban'
    if not path.exists():
        return []
    raw = parse_ban_file(str(path))
    result = []
    for p in raw:
        if not _is_player_name(p['name']):
            continue
        raw_ovr = p['ovr']
        ovr = normalize_brasfoot_ovr(raw_ovr)
        age = p['age'] if 14 <= p['age'] <= 45 else 22
        pos_code = p['pos_code'] if p['pos_code'] <= 4 else 3
        pos = pos_code_to_game(pos_code)
        result.append({'name': p['name'], 'ovr': ovr, 'raw_ovr': raw_ovr, 'age': age, 'pos': pos})
    return result

def assign_slots(players: list) -> list:
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

    gol_slots = {0, 17}
    gol_pool   = sorted([p for p in players if p['pos'] == 'GOL'],
                        key=lambda x: (x['ovr'], x.get('raw_ovr', 0)), reverse=True)
    field_pool = sorted([p for p in players if p['pos'] != 'GOL'],
                        key=lambda x: (x['ovr'], x.get('raw_ovr', 0)), reverse=True)

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

def find_ban_for_id(team_id: str) -> str | None:
    """Try multiple strategies to find a .ban file for a team ID."""
    # 1. Manual override
    if team_id in MANUAL_MAP:
        stem = MANUAL_MAP[team_id]
        if (BF_DIR / f'{stem}.ban').exists():
            return stem
        log.warning(f'  Manual override {team_id}→{stem} — file not found')
        return None

    # 2. Direct match
    if (BF_DIR / f'{team_id}.ban').exists():
        return team_id

    # 3. With _bra suffix
    if (BF_DIR / f'{team_id}_bra.ban').exists():
        return f'{team_id}_bra'

    # 4. Common state suffixes
    for suffix in ['sp_bra', 'rj_bra', 'mg_bra', 'rs_bra', 'pr_bra',
                   'sc_bra', 'ba_bra', 'ce_bra', 'pe_bra', 'go_bra',
                   'pa_bra', 'am_bra', 'mt_bra', 'ms_bra', 'pi_bra',
                   'pb_bra', 'rn_bra', 'ma_bra', 'se_bra', 'al_bra']:
        if (BF_DIR / f'{team_id}_{suffix}.ban').exists():
            return f'{team_id}_{suffix}'

    return None

def extract_league_ids(html: str) -> list:
    """Extract all team IDs from SERIE_A/B/C/D and BRA_EST_TEAMS definitions."""
    # Match {id:'xxx', ...} objects inside JS array definitions
    return re.findall(r"\{id:'([^']+)'", html)

def build_roster_js(team_id: str, slots: list) -> str:
    """Build JS array literal for 18 player strings."""
    items = ', '.join(f'"{s}"' for s in slots)
    return f'  "{team_id}": [{items}]'

BUILDSQUAD_CHECK = (
    "if(REAL_ROSTERS&&REAL_ROSTERS[team.id])"
    "return buildSquadFromNames(team.rating||65,REAL_ROSTERS[team.id],'BRA');"
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--show-map', action='store_true')
    args = parser.parse_args()

    with open(HTML_PATH, encoding='utf-8') as f:
        html = f.read()

    league_ids = extract_league_ids(html)
    # Deduplicate while preserving order
    seen = set()
    unique_ids = [x for x in league_ids if not (x in seen or seen.add(x))]
    log.info(f'Found {len(unique_ids)} unique team IDs in league definitions')

    roster_lines = []
    matched = 0
    unmatched = []

    for team_id in unique_ids:
        stem = find_ban_for_id(team_id)
        if stem is None:
            unmatched.append(team_id)
            continue
        players = parse_ban(stem)
        if not players:
            log.warning(f'  {team_id} → {stem}.ban parsed 0 players — skipping')
            unmatched.append(team_id)
            continue
        slots = assign_slots(players)
        roster_lines.append(build_roster_js(team_id, slots))
        matched += 1
        if args.show_map:
            log.info(f'  {team_id:25s} → {stem}.ban  ({len(players)} players, starter GK: {slots[0]})')

    log.info(f'Matched: {matched}/{len(unique_ids)} teams')
    if unmatched:
        log.info(f'Unmatched ({len(unmatched)}): {", ".join(unmatched)}')

    if matched == 0:
        log.error('Nothing to inject')
        return

    # Build the REAL_ROSTERS constant
    rosters_block = 'const REAL_ROSTERS = {\n' + ',\n'.join(roster_lines) + '\n};\n'

    # ── Idempotent cleanup: remove previous injections if present ──
    if 'const REAL_ROSTERS' in html:
        html = re.sub(r'const REAL_ROSTERS = \{.*?\};\n?', '', html, flags=re.DOTALL)
    # Remove CHECK if already injected into buildSquad body
    html = html.replace(
        'function buildSquad(team){' + BUILDSQUAD_CHECK,
        'function buildSquad(team){',
    )

    # Find the original buildSquad and:
    # 1. Inject REAL_ROSTERS const before it
    # 2. Add lookup check at start of its body
    # Pattern: "function buildSquad(team){" or with space before {
    m = re.search(r'function buildSquad\(team\) *\{', html)
    if not m:
        log.error('Cannot find "function buildSquad(team)" in HTML')
        return

    func_open = m.group(0)           # e.g. "function buildSquad(team){"
    replacement = (
        rosters_block
        + func_open
        + BUILDSQUAD_CHECK
    )
    html = html[:m.start()] + replacement + html[m.end():]

    if args.dry_run:
        log.info('[dry-run] Not writing HTML. Showing first 500 chars of REAL_ROSTERS:')
        print(rosters_block[:500])
        return

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    log.info(f'Saved {HTML_PATH} — {matched} teams now use real Brasfoot rosters')

if __name__ == '__main__':
    main()
