"""End-to-end test: parse tests/test_chords.xml and convert to tab.

Exercises the full chord path: parser identifies the chord, converter
substitutes a guitar-friendly voicing.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app

FIXTURE = os.path.join(os.path.dirname(__file__), 'test_chords.xml')

app = create_app()
app.config['UPLOAD_FOLDER'] = os.path.dirname(FIXTURE)
file_id = os.path.basename(FIXTURE)

with app.app_context():
    from services.parser import parse_musicxml
    from services.converter import convert_notes_to_tab
    notes = parse_musicxml(file_id)
    tab = convert_notes_to_tab(notes)

print(f"Parsed {len(notes)} elements:")
for n in notes:
    print(f"  {n}")
print(f"\nTab ({len(tab)} elements):")
for t in tab:
    print(f"  {t}")

# Fixture is: single E4, C-major chord (C4/E4/G4), single D4.
assert len(notes) == 3, f"Expected 3 elements, got {len(notes)}"

# Element 0: melody note E4
assert notes[0]['type'] == 'note' and notes[0]['midi'] == 64
assert tab[0]['type'] == 'note' and tab[0]['flag'] is None

# Element 1: the chord, identified as C major
chord = notes[1]
assert chord['type'] == 'chord', chord
assert chord['root'] == 'C'
assert chord['root_pc'] == 0
assert chord['quality'] == 'major'
assert chord['name'] == 'C', chord['name']
assert chord['midis'] == [60, 64, 67]

# Converter substitutes the guitar-friendly open-C shape (not the 3 written notes)
chord_tab = tab[1]
assert chord_tab['type'] == 'chord'
assert chord_tab['voicing_source'] == 'shape', chord_tab
assert chord_tab['flag'] is None
got = sorted((p['string'], p['fret']) for p in chord_tab['placements'])
assert got == [(2, 3), (3, 2), (4, 0), (5, 1), (6, 0)], got

# Element 2: melody note D4
assert notes[2]['type'] == 'note' and notes[2]['midi'] == 62
assert tab[2]['type'] == 'note' and tab[2]['flag'] is None

print("\nAll chord integration assertions passed.")
