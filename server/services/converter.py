from services.chord_voicer import voice_chord

# Standard tuning open-string MIDI values, strings 1 (low E) -> 6 (high e).
# NOTE: this numbers string 1 as the low E, which is the reverse of standard tab
# convention (string 1 = high e). Kept for consistency with the existing melody
# path; flagged for the team to reconcile separately. See CLAUDE.md.
OPEN_MIDI = [40, 45, 50, 55, 59, 64]


MAX_FRET = 24  # standard guitar goes to ~20-24 frets; 24 covers full MIDI 40-88 range


def midi_to_string_fret(midi: int) -> dict | None:
    """Map a MIDI note number to the most playable guitar position (lowest fret).

    Prefers the highest string (thinnest) where the fret number is minimised,
    which produces the most natural single-note melody fingering.
    Returns {'string': 1-6, 'fret': 0-24} or None if out of playable range.
    """
    best = None
    for string_num, open_note in enumerate(OPEN_MIDI, start=1):
        fret = midi - open_note
        if 0 <= fret <= MAX_FRET:
            if best is None or fret < best['fret']:
                best = {'string': string_num, 'fret': fret}
    return best


def convert_notes_to_tab(notes: list[dict]) -> list[dict]:
    """Convert parsed notes/chords/rests to guitar tab assignments.

    Each input dict carries a 'type' of 'note', 'chord', or 'rest'. Older callers
    that omit 'type' are treated as melody notes (rests use pitch 'R').
    """
    tab = []
    for note in notes:
        kind = note.get('type')

        if kind == 'chord':
            voicing = voice_chord(note['root_pc'], note['quality'], note['midis'])
            tab.append({**note, **voicing})
            continue

        if kind == 'rest' or note.get('pitch') == 'R':
            tab.append({**note, 'type': 'rest', 'string': None, 'fret': None, 'flag': 'rest'})
            continue

        placement = midi_to_string_fret(note['midi'])
        if placement is None:
            tab.append({**note, 'type': 'note', 'string': None, 'fret': None, 'flag': 'out_of_range'})
        else:
            tab.append({**note, 'type': 'note', **placement, 'flag': None})
    return tab
