"""Manual test for convert_notes_to_tab."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.converter import convert_notes_to_tab

notes = [
    {'pitch': 'C', 'octave': 4, 'midi': 60, 'duration': 1.0, 'measure': 1},
    {'pitch': 'E', 'octave': 4, 'midi': 64, 'duration': 1.0, 'measure': 1},
    {'pitch': 'R', 'octave': None, 'midi': None, 'duration': 1.0, 'measure': 1},
    {'pitch': 'A', 'octave': 0, 'midi': 21, 'duration': 1.0, 'measure': 2},  # out of range
]

tab = convert_notes_to_tab(notes)

print(f"Converted {len(tab)} elements:")
for t in tab:
    print(f"  {t}")

# C4 (midi 60) → string 5 (B, open=59), fret 1 — lowest-fret position
assert tab[0]['string'] == 5 and tab[0]['fret'] == 1 and tab[0]['flag'] is None

# E4 (midi 64) → string 6 (High e, open=64), fret 0 — open string
assert tab[1]['string'] == 6 and tab[1]['fret'] == 0 and tab[1]['flag'] is None

# Rest
assert tab[2]['string'] is None and tab[2]['fret'] is None and tab[2]['flag'] == 'rest'

# Out of range
assert tab[3]['string'] is None and tab[3]['fret'] is None and tab[3]['flag'] == 'out_of_range'

print("\nAll assertions passed.")
