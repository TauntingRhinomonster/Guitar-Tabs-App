"""Manual test for parse_musicxml against a minimal MusicXML fixture."""
import os
import sys
import tempfile

# Minimal MusicXML with 3 notes (C4, E4, G4) and a rest
SAMPLE_MUSICXML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN"
  "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>Guitar</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
        <clef><sign>G</sign><line>2</line></clef>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>1</duration><type>quarter</type>
      </note>
      <note>
        <pitch><step>E</step><octave>4</octave></pitch>
        <duration>1</duration><type>quarter</type>
      </note>
      <note>
        <pitch><step>G</step><octave>4</octave></pitch>
        <duration>1</duration><type>quarter</type>
      </note>
      <note><rest/><duration>1</duration><type>quarter</type></note>
    </measure>
  </part>
</score-partwise>
"""

# Write fixture to a temp file
tmp = tempfile.NamedTemporaryFile(suffix='.xml', delete=False, mode='w')
tmp.write(SAMPLE_MUSICXML)
tmp.close()

# Bootstrap Flask app context so current_app works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import create_app

app = create_app()
# Point upload folder at the temp dir so parse_musicxml can find the file
app.config['UPLOAD_FOLDER'] = os.path.dirname(tmp.name)
file_id = os.path.basename(tmp.name)

with app.app_context():
    from services.parser import parse_musicxml
    notes = parse_musicxml(file_id)

os.unlink(tmp.name)

print(f"Parsed {len(notes)} elements:")
for n in notes:
    print(f"  {n}")

# Assertions
assert len(notes) == 4, f"Expected 4 elements, got {len(notes)}"

c4 = notes[0]
assert c4['pitch'] == 'C', f"Expected C, got {c4['pitch']}"
assert c4['octave'] == 4
assert c4['midi'] == 60
assert c4['duration'] == 1.0
assert c4['measure'] == 1

e4 = notes[1]
assert e4['pitch'] == 'E'
assert e4['midi'] == 64

g4 = notes[2]
assert g4['pitch'] == 'G'
assert g4['midi'] == 67

rest = notes[3]
assert rest['pitch'] == 'R'
assert rest['octave'] is None
assert rest['midi'] is None

print("\nAll assertions passed.")
