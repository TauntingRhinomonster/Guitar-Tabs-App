"""Turn a chord's identity into a guitar-friendly voicing.

This module is intentionally pure (no music21, no Flask). Given a chord's
root pitch class, quality, and the written MIDI notes, it returns a playable
guitar voicing — the shape a guitarist would actually grab — rather than just
stacking the written notes.

Strategy (matches docs/conversion-approach.md "smart" chord goal):
  1. Open-position library — standard first-position grips (C, G, Am, E7, ...).
  2. Movable barre shapes — transpose an E-shape or A-shape for any other root.
  3. Literal fallback — place the written notes on distinct strings with the
     smallest fret span, for qualities we don't have a shape for.

String numbering matches services/converter.py: OPEN_MIDI is ordered low E -> high E,
so string 1 = low E and string 6 = high e. (This is the opposite of standard tab
convention; see the team note in converter.py / CLAUDE.md.)
"""
from itertools import permutations

# Open-string MIDI per string, index 0 = string 1 (low E) ... index 5 = string 6 (high e).
OPEN_MIDI = [40, 45, 50, 55, 59, 64]

# Highest fret we'll voice a chord at before giving up on a movable shape.
MAX_FRET = 15

# Note names by pitch class (sharps). Used to label placements.
_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Qualities we know how to voice as real guitar shapes. Anything else -> literal.
SUPPORTED_QUALITIES = {'major', 'minor', 'dom7', 'maj7', 'min7'}

# --- Open-position shapes -----------------------------------------------------
# Frets per string [s1=lowE, s2=A, s3=D, s4=G, s5=B, s6=highE]; None = muted.
# Keyed by (root pitch class, quality).
OPEN_SHAPES = {
    (0, 'major'):  [None, 3, 2, 0, 1, 0],   # C
    (9, 'major'):  [None, 0, 2, 2, 2, 0],   # A
    (7, 'major'):  [3, 2, 0, 0, 0, 3],      # G
    (4, 'major'):  [0, 2, 2, 1, 0, 0],      # E
    (2, 'major'):  [None, None, 0, 2, 3, 2],  # D
    (9, 'minor'):  [None, 0, 2, 2, 1, 0],   # Am
    (4, 'minor'):  [0, 2, 2, 0, 0, 0],      # Em
    (2, 'minor'):  [None, None, 0, 2, 3, 1],  # Dm
    (4, 'dom7'):   [0, 2, 0, 1, 0, 0],      # E7
    (9, 'dom7'):   [None, 0, 2, 0, 2, 0],   # A7
    (2, 'dom7'):   [None, None, 0, 2, 1, 2],  # D7
    (7, 'dom7'):   [3, 2, 0, 0, 0, 1],      # G7
    (0, 'dom7'):   [None, 3, 2, 3, 1, 0],   # C7
    (0, 'maj7'):   [None, 3, 2, 0, 0, 0],   # Cmaj7
    (9, 'maj7'):   [None, 0, 2, 1, 2, 0],   # Amaj7
    (2, 'maj7'):   [None, None, 0, 2, 2, 2],  # Dmaj7
    (9, 'min7'):   [None, 0, 2, 0, 1, 0],   # Am7
    (4, 'min7'):   [0, 2, 0, 0, 0, 0],      # Em7
    (2, 'min7'):   [None, None, 0, 2, 1, 1],  # Dm7
}

# --- Movable barre shapes ----------------------------------------------------
# Relative fret patterns; the barre fret is added to every non-None entry.
# E-shape: root on string 1 (low E). A-shape: root on string 2 (A).
_E_SHAPE = {
    'major': [0, 2, 2, 1, 0, 0],
    'minor': [0, 2, 2, 0, 0, 0],
    'dom7':  [0, 2, 0, 1, 0, 0],
    'maj7':  [0, None, 1, 1, 0, None],
    'min7':  [0, 2, 0, 0, 0, 0],
}
_A_SHAPE = {
    'major': [None, 0, 2, 2, 2, 0],
    'minor': [None, 0, 2, 2, 1, 0],
    'dom7':  [None, 0, 2, 0, 2, 0],
    'maj7':  [None, 0, 2, 1, 2, 0],
    'min7':  [None, 0, 2, 0, 1, 0],
}
_E_ROOT_PC = 4   # low E open string pitch class
_A_ROOT_PC = 9   # A open string pitch class


def _placement(string_num: int, fret: int) -> dict:
    """Build a single placement dict from a 1-based string number and fret."""
    midi = OPEN_MIDI[string_num - 1] + fret
    return {
        'string': string_num,
        'fret': fret,
        'midi': midi,
        'pitch': _NOTE_NAMES[midi % 12],
        'octave': midi // 12 - 1,
    }


def _shape_to_placements(shape: list) -> list[dict]:
    """Convert a per-string fret list (None = muted) to placement dicts."""
    return [_placement(i + 1, fret) for i, fret in enumerate(shape) if fret is not None]


def _movable_shape(root_pc: int, quality: str) -> list | None:
    """Pick the lower of the E-shape / A-shape barre voicings for this chord."""
    candidates = []
    f_e = (root_pc - _E_ROOT_PC) % 12
    f_a = (root_pc - _A_ROOT_PC) % 12
    for barre, shapes in ((f_e, _E_SHAPE), (f_a, _A_SHAPE)):
        pattern = shapes.get(quality)
        if pattern is None:
            continue
        frets = [None if f is None else f + barre for f in pattern]
        if max(f for f in frets if f is not None) <= MAX_FRET:
            candidates.append((barre, frets))
    if not candidates:
        return None
    # Prefer the most playable (lowest) position.
    candidates.sort(key=lambda c: c[0])
    return candidates[0][1]


def _literal_voicing(midis: list[int]) -> dict:
    """Fallback: place the written notes on distinct strings, minimal span.

    Tries every assignment of notes to distinct strings (n <= 6, so brute force
    is trivial) and keeps the one with the smallest fretted-fret span, breaking
    ties toward lower positions. Notes that fit nowhere are flagged.
    """
    notes = sorted(set(m for m in midis if m is not None))
    best = None  # (span, max_fret, placements)
    n = len(notes)
    for strings in permutations(range(6), n):
        placements = []
        ok = True
        for midi, s in zip(notes, strings):
            fret = midi - OPEN_MIDI[s]
            if not (0 <= fret <= MAX_FRET):
                ok = False
                break
            placements.append(_placement(s + 1, fret))
        if not ok:
            continue
        fretted = [p['fret'] for p in placements if p['fret'] > 0]
        span = (max(fretted) - min(fretted)) if fretted else 0
        top = max((p['fret'] for p in placements), default=0)
        key = (span, top)
        if best is None or key < best[0]:
            best = (key, placements)

    if best is None:
        # Couldn't even place the full set together; place each note on its own
        # best string independently and flag what we couldn't fit.
        placements, missing = _place_independently(notes)
        return {
            'placements': placements,
            'voicing_source': 'literal',
            'flag': 'partial' if missing else None,
        }

    placed_midis = {p['midi'] for p in best[1]}
    missing = [m for m in notes if m not in placed_midis]
    return {
        'placements': best[1],
        'voicing_source': 'literal',
        'flag': 'partial' if missing else None,
    }


def _place_independently(notes: list[int]) -> tuple[list[dict], list[int]]:
    """Greedily place each note on the lowest free string that can play it."""
    placements = []
    used = set()
    missing = []
    for midi in notes:
        placed = False
        for s in range(6):
            if s in used:
                continue
            fret = midi - OPEN_MIDI[s]
            if 0 <= fret <= MAX_FRET:
                placements.append(_placement(s + 1, fret))
                used.add(s)
                placed = True
                break
        if not placed:
            missing.append(midi)
    placements.sort(key=lambda p: p['string'])
    return placements, missing


def voice_chord(root_pc: int, quality: str, midis: list[int]) -> dict:
    """Return a guitar-friendly voicing for a chord.

    Args:
        root_pc: root pitch class (0=C .. 11=B).
        quality: one of SUPPORTED_QUALITIES, or anything else for literal voicing.
        midis: the written MIDI notes (used only for the literal fallback).

    Returns:
        {'placements': [...], 'voicing_source': 'shape'|'literal', 'flag': None|'partial'}
    """
    if quality in SUPPORTED_QUALITIES:
        shape = OPEN_SHAPES.get((root_pc % 12, quality))
        if shape is None:
            shape = _movable_shape(root_pc % 12, quality)
        if shape is not None:
            return {
                'placements': _shape_to_placements(shape),
                'voicing_source': 'shape',
                'flag': None,
            }
    # Unsupported quality (diminished, sus, etc.) -> faithful literal voicing.
    return _literal_voicing(midis)
