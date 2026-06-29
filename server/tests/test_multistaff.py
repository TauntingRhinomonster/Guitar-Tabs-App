"""Tests for multi-staff (piano) MusicXML parsing.

Tests both the internal _extract_melody_stream() helper and the public
parse_musicxml() interface to confirm multi-part detection is automatic.
"""
import sys
import os
import music21

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app

FIXTURE = os.path.join(os.path.dirname(__file__), 'test_piano.xml')

app = create_app()
app.config['UPLOAD_FOLDER'] = os.path.dirname(FIXTURE)
file_id = os.path.basename(FIXTURE)


# ---------------------------------------------------------------------------
# Unit tests for _extract_melody_stream()
# ---------------------------------------------------------------------------

def test_extract_melody_returns_four_elements():
    """Fixture has 4 beats; melody stream should have exactly 4 elements."""
    from services.parser import _extract_melody_stream
    score = music21.converter.parse(FIXTURE)
    result = _extract_melody_stream(score)
    assert len(result) == 4, f"Expected 4, got {len(result)}: {result}"


def test_extract_melody_beat1_picks_treble():
    """Beat 1: treble E4 (64) beats bass C3 (48)."""
    from services.parser import _extract_melody_stream
    score = music21.converter.parse(FIXTURE)
    result = _extract_melody_stream(score)
    el = result[0]
    assert isinstance(el, music21.note.Note), f"Expected Note, got {type(el)}"
    assert el.pitch.midi == 64, f"Expected E4 (64), got {el.pitch.midi}"


def test_extract_melody_beat3_picks_bass():
    """Beat 3: treble has a rest, so bass F4 (65) becomes the melody."""
    from services.parser import _extract_melody_stream
    score = music21.converter.parse(FIXTURE)
    result = _extract_melody_stream(score)
    el = result[2]
    assert isinstance(el, music21.note.Note), f"Expected Note, got {type(el)}"
    assert el.pitch.midi == 65, f"Expected F4 (65), got {el.pitch.midi}"


def test_extract_melody_beat4_drops_below_range():
    """Beat 4: bass C2 (36) is below MIDI 40 and must be dropped; treble G4 wins."""
    from services.parser import _extract_melody_stream
    score = music21.converter.parse(FIXTURE)
    result = _extract_melody_stream(score)
    el = result[3]
    assert isinstance(el, music21.note.Note), f"Expected Note, got {type(el)}"
    assert el.pitch.midi == 67, f"Expected G4 (67), got {el.pitch.midi}"


# ---------------------------------------------------------------------------
# Integration test: parse_musicxml() auto-detects multi-part
# ---------------------------------------------------------------------------

def test_parse_musicxml_auto_detects_multipart():
    """parse_musicxml() should silently pick the melody path for two-part files."""
    with app.app_context():
        from services.parser import parse_musicxml
        notes = parse_musicxml(file_id)

    assert len(notes) == 4, f"Expected 4 note dicts, got {len(notes)}"

    midis = [n['midi'] for n in notes]
    assert midis == [64, 62, 65, 67], f"Expected [64,62,65,67], got {midis}"

    for n in notes:
        assert n['type'] == 'note', f"Expected type='note', got {n['type']}"


if __name__ == '__main__':
    test_extract_melody_returns_four_elements()
    test_extract_melody_beat1_picks_treble()
    test_extract_melody_beat3_picks_bass()
    test_extract_melody_beat4_drops_below_range()
    test_parse_musicxml_auto_detects_multipart()
    print("All multi-staff tests passed.")
