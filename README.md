# Guitar-Tabs-App (TabVerter)

TabVerter is a full-stack web application that turns digital sheet music into
playable guitar tablature. A user uploads a **MusicXML** file (`.xml` or `.mxl`),
the app parses the notes, maps each one to a guitar string and fret, and then
renders the finished tab in the browser as a downloadable **PDF**.

The long-term goal is to let guitarists take sheet music they own and convert it
into easy-to-read tabs. For the MVP we focus on MusicXML input because it is
structured data; converting a **PDF or photo** of sheet music is a planned future
feature (see [Software Features](#software-features)).

---

## Team Members

| Name          | Role / Focus Area                        |
| ------------- | ---------------------------------------- |
| Hunter        | Project Manager / Full-Stack Integrator  |
| Rhino         | Frontend Developer                       |
| Luke          | Backend Developer                        |
| Jo            | MusicXML / Conversion Developer          |
| Emily         | Testing / Documentation / Rendering Lead |

---

## Architecture

TabVerter is a two-part application: a **React + TypeScript** frontend and a
**Python + Flask** backend, connected over HTTP with JSON.

### Request flow

```
Browser (React) ──upload .xml/.mxl──▶  POST /upload   ──▶ validate + store, return file_id
                                                            │
Browser (React) ──file_id (JSON)────▶  POST /convert  ──▶ music21 parses notes
                                                            │        │
                                                            │        ▼
                                                            │   map each note → string + fret
                                                            ▼
                                              returns tab JSON
                                                            │
                          React renders tab as a PDF ◀──────┘  (view + download)
```

### Tech Stack

| Layer | Technology | Why We Chose It |
|---|---|---|
| Frontend | React + TypeScript (Vite) | Component-based UI for the upload and result pages; TypeScript catches errors early. |
| Backend | **Python + Flask** | We pivoted from our original Node/Express plan to Python so we could use `music21`, a mature music-theory library. |
| Music Parsing / Conversion | **music21** + rule-based pitch-to-fret mapping | `music21` reads MusicXML natively and gives us MIDI numbers, ties, chords, and multi-staff handling for free. Fret placement is then simple arithmetic. |
| File Format (input) | MusicXML (`.xml` / `.mxl`) | Structured, standard, and far easier to parse reliably than an image or PDF. |
| Tab Rendering / Output | `@react-pdf/renderer` | Renders the generated tab in the browser and produces a downloadable PDF. (Originally we planned to output a MusicXML tab file; we chose PDF instead.) |
| Testing / CI | pytest + GitHub Actions | Automated backend tests run on every push. |
| Hosting | Local (`localhost`) | Runs locally for the MVP; public deployment is a future goal. |

> **Note on our pivot:** Our Sprint 1 plan called for a Node/Express + TypeScript
> backend that output a MusicXML tab file. During development we switched the
> backend to **Python + Flask** to use `music21`, and we chose to render/download
> the result as a **PDF** instead of MusicXML. The design reasoning in
> [Design Decisions](#design-decisions-sprint-1) reflects our original choices and
> is kept for history.

---

## Software Features

Feature status is accurate as of the final report. Unfinished planned features are
kept in the list (unchecked); features we added beyond the original plan are noted.

### Core features (planned in Sprint 1)

- [x] Upload a MusicXML file (`.xml` / `.mxl`) through the web UI
- [x] Backend validates file type and size (5 MB max) before accepting it
- [x] Backend stores each upload with a unique ID and returns it (`POST /upload`)
- [x] Parse MusicXML with `music21` — extract pitch, octave, MIDI number, duration, and measure for every note and rest
- [x] Convert each note to a guitar string + fret using standard tuning (E A D G B e)
- [x] Choose the lowest-fret playable position for the most natural fingering
- [x] Flag out-of-range notes instead of silently dropping them
- [x] Convert endpoint returns structured tab JSON (`POST /convert`)
- [x] Render the generated tab visually in the browser
- [x] Download the generated tab as a PDF
- [x] Download the original uploaded file (`GET /download`)
- [x] Health-check endpoint (`GET /health`)
- [x] README with local setup instructions for the whole team

### Features added beyond the original plan

- [x] Multi-staff / piano input — melody extraction keeps the highest in-range note at each beat
- [x] Chord parsing and detection with `music21`
- [x] Chord voicing engine — a chord-shape library plus a brute-force fallback that places chords on the fretboard
- [x] Multi-page, multi-system PDF tab layout (measures wrap across systems and pages)
- [x] Automated backend test suite (pytest: parser, converter, chords, multi-staff)
- [x] Continuous Integration via GitHub Actions (runs backend tests on every push)

### Planned but not completed

- [ ] Output a MusicXML tab file (we pivoted to PDF output instead)
- [ ] Carry lyrics from the input file through to the output
- [ ] Support alternate guitar tunings (standard tuning only for now)
- [ ] PDF input — upload a PDF of sheet music (currently MusicXML only)
- [ ] Image / photo input — photograph sheet music and convert it
- [ ] Deploy to a public host (currently runs locally only)

> **Known limitation:** internally the backend numbers strings 1–6 as low-E → high-e,
> which is reversed from the standard tab convention (string 1 = high e). The
> frontend compensates when rendering. Reconciling this convention across the whole
> app is on our list.

---

## Team Communication

- **In person:** we met during our scheduled class work sessions (Mon / Wed / Fri)
  for stand-ups, planning, and integration.
- **Group chat:** we used a team messaging channel for day-to-day questions, quick
  updates, and coordinating who was working on what.
- **GitHub:** all code was shared through the repository using branches and pull
  requests; the **GitHub Project board** (`CSE 310 #2`) tracked tasks, status, and
  assignments.

> _Team: update the specific channels above (Discord/Teams/text, etc.) to match how
> you actually communicated._

---

## Team Responsibilities

| Name          | Responsibilities                                                                                          |
| ------------- | --------------------------------------------------------------------------------------------------------- |
| Hunter        | Sprint planning, GitHub management, team coordination, merging pull requests, full-stack integration      |
| Rhino         | React UI: upload page, result/download page, styling, and the in-browser tab viewer                       |
| Luke          | Flask server setup, API routes, file upload/validation handling, CI, and fret-conversion logic            |
| Jo            | MusicXML parsing with `music21`, pitch/chord mapping, and guitar tab conversion                            |
| Emily         | Test files, error testing, README/documentation, rendering research, and final demo prep                  |

---

## Reflections

We held a team retrospective (lessons-learned meeting) to review the project.
The findings below are scoped to the team as a whole.

### What the team learned

1. How to split a full-stack app into a clear frontend/backend contract (JSON over
   HTTP) so team members could work in parallel without blocking each other.
2. That choosing the right library matters more than building everything from
   scratch — `music21` handled music-theory edge cases (ties, accidentals, chords,
   multi-staff) that would have taken us weeks to implement by hand.
3. How to run a real Git workflow — feature branches, pull requests, and code review
   — instead of everyone pushing directly to `main`.
4. That the core of the problem (turning a note into a fret) is simple math once you
   have MIDI numbers; the harder work was the surrounding plumbing — parsing,
   rendering, and file handling.
5. How Continuous Integration (GitHub Actions) catches broken code automatically
   before it reaches `main`.

### What can be improved

1. We changed our backend stack from Node/Express to Python/Flask partway through.
   Confirming library support and locking in the stack earlier would have saved rework.
2. Our documentation drifted from the actual code (the README described Express long
   after we moved to Flask). Updating docs alongside code changes would keep them honest.
3. Task ownership was uneven — some board items had no assignee and status was not
   always kept current, which made it hard to tell what was in progress.
4. We let internal inconsistencies (such as the reversed string-numbering convention)
   sit unresolved instead of reconciling them early.
5. More end-to-end testing with a wider variety of real MusicXML files would have
   surfaced edge cases sooner.

### Future plans for this project

1. Add **PDF and photo input** using optical music recognition or a vision model, so
   users don't need a MusicXML file to start.
2. Support **alternate tunings** and capo settings.
3. **Deploy** the app to a public host (e.g. Vercel/Render) so it works without
   running it locally.
4. Improve the tab output — better chord fingerings, lyrics under the tab, and a
   single consistent string-numbering convention across the whole app.
5. Add user accounts / saved tabs so people can build a library of converted songs.

> _Team: confirm these reflections reflect your actual retrospective discussion and
> adjust any point before submitting._

---

## Running Locally

### Frontend (React + Vite)

```bash
npm install
npm run dev          # http://localhost:5173
```

### Backend (Python + Flask)

```bash
cd server
python -m venv venv
venv\Scripts\activate         # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py                 # http://localhost:5000
```

### How the backend works

**1. Upload — `POST /upload`**
Send a `.xml` or `.mxl` file as form data. The server validates the file type and
size (5 MB max), saves it with a unique ID, and returns that `file_id`.

**2. Convert — `POST /convert`**
Send `{ "file_id": "..." }` as JSON. The server runs two steps:
- **Parse** — uses `music21` to read the MusicXML file and extract every note, chord,
  and rest with pitch, octave, MIDI number, duration, and measure number.
- **Convert** — maps each MIDI number to a guitar string and fret using standard
  tuning (E A D G B e). Out-of-range notes are flagged `out_of_range`; rests are
  flagged `rest`.

Returns a JSON array of tab entries that the frontend renders as the visual tab / PDF.

**3. Download — `GET /download?file_id=...`**
Returns the original uploaded MusicXML file as a downloadable attachment.

### Standard tuning reference
| String | Open Note | Open MIDI |
|--------|-----------|-----------|
| 6 (low) | E2 | 40 |
| 5 | A2 | 45 |
| 4 | D3 | 50 |
| 3 | G3 | 55 |
| 2 | B3 | 59 |
| 1 (high) | E4 | 64 |

---

## Design Decisions (Sprint 1)

> These sections capture our original Sprint 1 reasoning. Some choices changed during
> development (see the [Architecture pivot note](#architecture)); we keep them here for
> history.

### Why We Chose This Stack

We chose a full-stack web application to keep the project realistic for a student team
while still being useful and resume-worthy. React gives us a strong framework for the
upload screen, results page, and tab viewer. A lightweight backend handles uploaded
files, parses them, converts them, and returns downloadable output. Since MusicXML is
structured data, we could start with a rule-based conversion system instead of relying
on AI or image recognition for the MVP.

### Major Tradeoffs

**React + TypeScript**
- **Pros:** great for interactive web apps; component structure keeps the UI organized;
  TypeScript prevents bugs; opens a path toward React Native later.
- **Tradeoffs:** extra setup; some teammates needed time with components, props, and state.

**Backend (originally Node/Express, now Python/Flask)**
- **Pros:** simple to set up; good for file-upload routes and API endpoints; easy for a
  small team to maintain.
- **Tradeoffs:** Node lacks mature music libraries, which is exactly why we moved to
  Python + `music21`.

**MusicXML Input**
- **Pros:** structured and easier to parse than images/PDFs; reliable for an MVP; avoids
  the cost and complexity of AI vision/OCR.
- **Tradeoffs:** users must already have a MusicXML file; no photo/PDF input in the MVP;
  some files have quirks that still need edge-case handling.

**Rule-Based Conversion**
- **Pros:** no API cost; predictable; easy to test with known input/output; works well for
  standard tuning and basic notation.
- **Tradeoffs:** the same note can be played on multiple strings, so fingering choices are
  not always the easiest to play; alternate tunings and complex arrangements are harder.

### Summary

Overall this stack balances simplicity, reliability, and long-term potential. The MVP is a
clean web app that uploads MusicXML, parses it, converts it into guitar tablature, displays
the result, and lets the user download it as a PDF. Richer input types like PDF or photo
upload can be added once the core pipeline is solid.
