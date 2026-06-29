"""Manual tests for chord_voicer.voice_chord (pure, no Flask needed)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.chord_voicer import voice_chord


def pairs(result):
    """(string, fret) tuples sorted by string, for easy comparison."""
    return sorted((p['string'], p['fret']) for p in result['placements'])


# --- Open-position shape: C major --------------------------------------------
c = voice_chord(0, 'major', [60, 64, 67])
assert c['voicing_source'] == 'shape'
assert c['flag'] is None
assert pairs(c) == [(2, 3), (3, 2), (4, 0), (5, 1), (6, 0)], pairs(c)
print("C major  ->", pairs(c))

# --- Open-position shape: A minor --------------------------------------------
am = voice_chord(9, 'minor', [57, 60, 64])
assert am['voicing_source'] == 'shape'
assert pairs(am) == [(2, 0), (3, 2), (4, 2), (5, 1), (6, 0)], pairs(am)
print("A minor  ->", pairs(am))

# --- Open-position shape: G7 -------------------------------------------------
g7 = voice_chord(7, 'dom7', [55, 59, 62, 65])
assert g7['voicing_source'] == 'shape'
assert pairs(g7) == [(1, 3), (2, 2), (3, 0), (4, 0), (5, 0), (6, 1)], pairs(g7)
print("G7       ->", pairs(g7))

# --- Movable E-shape barre: F major (root pc 5) -----------------------------
f = voice_chord(5, 'major', [53, 57, 60])
assert f['voicing_source'] == 'shape'
# E-shape major barred at fret 1
assert pairs(f) == [(1, 1), (2, 3), (3, 3), (4, 2), (5, 1), (6, 1)], pairs(f)
print("F major  ->", pairs(f))

# --- Movable A-shape barre chosen when lower: C# major (root pc 1) -----------
csharp = voice_chord(1, 'major', [61, 65, 68])
assert csharp['voicing_source'] == 'shape'
# A-shape (fret 4) beats E-shape (fret 9)
assert pairs(csharp) == [(2, 4), (3, 6), (4, 6), (5, 6), (6, 4)], pairs(csharp)
print("C# major ->", pairs(csharp))

# --- Unsupported quality falls back to literal voicing of written notes ------
# B diminished triad: B3(59), D4(62), F4(65)
bdim = voice_chord(11, 'other', [59, 62, 65])
assert bdim['voicing_source'] == 'literal'
assert bdim['flag'] is None
assert len(bdim['placements']) == 3, bdim['placements']
# every written note is represented, each on its own string
assert len({p['string'] for p in bdim['placements']}) == 3
assert sorted(p['midi'] for p in bdim['placements']) == [59, 62, 65]
print("Bdim     ->", pairs(bdim), bdim['voicing_source'])

# --- Out-of-range note in a literal voicing is flagged partial ---------------
oor = voice_chord(9, 'other', [21, 60, 64])  # 21 = A0, below the guitar
assert oor['voicing_source'] == 'literal'
assert oor['flag'] == 'partial'
placed = sorted(p['midi'] for p in oor['placements'])
assert 21 not in placed and 60 in placed and 64 in placed, placed
print("partial  ->", pairs(oor), oor['flag'])

print("\nAll chord_voicer assertions passed.")
