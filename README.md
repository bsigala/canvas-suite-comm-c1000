# Canvas_Suite — COMM C1000 Course Package

Generated course content and import runbooks for the **COMM C1000: Public Speaking** Canvas course (Rio Hondo College, Fall 2026). 800-point mastery architecture, ZTC OER framework, Title 5 RSI weekly touchpoints.

---

## What's in this package

| Area | Files |
| :--- | :--- |
| **Course pages** | `Home_Page.html`, `Syllabus.html`, `Opening_Announcement.html`, `Profile_Page.html`, discussion etiquette/icebreaker |
| **Week modules** | 16 × `Week_XX_Overview.html` (two themes under `Individual_Pages/`) |
| **Grading rubrics** | 10 × `Rubric_*.html` (reconcile to 800 pts) |
| **Assignments & discussions** | 4 × `Assignment_Speech_*.html`, 4 × `Discussion_Module_*.html` |
| **Audio** | `Audio_Assets/` — 16 weekly touchpoints (mp3 + m4a), 2 greetings, player snippets |
| **Quizzes** | `COMM_C1000_Chapters_1-5_Quiz_QTI.zip`, `COMM_C1000_Chapters_6-16_Quiz_QTI.zip` (imported separately) |
| **One-click import** | `COMM_C1000_Course_Export.imscc` — modules, pages, assignments, **and audio** in one step |
| **Single source of truth** | `course_data.py` — weeks, rubrics, assignments, discussions, module layout |
| **Build** | `build.py` — regenerate everything + 800-point reconciliation |
| **Generators** | `generate_*.py`, `clone_voice_and_regenerate.py` |

## How it works

`course_data.py` is the single source of truth: all 16 weeks, 10 rubrics (800 pts), 4 speech assignments, 5 discussions, and the module layout. Every generator reads it. Edit `course_data.py`, then rebuild:

```bash
python3 build.py          # pages + rubrics + cartridge (deterministic)
python3 build.py --all    # + quiz QTI zips and audio TTS (needs API keys)
```

The cartridge (`generate_canvas_cartridge.py`) bundles the 16 weekly audio touchpoints and rewires their players with Canvas's `$IMS-CC-FILEBASE$` token, so audio works immediately after import — no manual upload or `src` swap.

## Deployment

**Fast path (recommended):**

1. Import `COMM_C1000_Course_Export.imscc` (Settings → Import Course Content → Common Cartridge). Recreates the 17 modules, all pages, the 4 speech Assignments (100/100/150/50 pts), the syllabus, and working audio players.
2. Import both QTI quiz zips (the only thing not bundled).

**Manual fallback:** `CANVAS_MODULES_IMPORT_CHECKLIST.md` (paste pages by hand) and `CANVAS_DEPLOYMENT_CHECKLIST.md` (audio upload + `src` swap + quiz import) remain for the paste-pages path only.

---

## Voice cloning (optional)

`clone_voice_and_regenerate.py` re-renders the 2 greetings **and all 16 weekly touchpoints** in a cloned voice, in place. After re-rendering, rerun `python3 generate_canvas_cartridge.py` to re-bundle the new audio, then re-import the cartridge. Requires `ELEVENLABS_API_KEY=sk_...` in `~/genkit-huggingface-project/.env` (an Instant Voice Cloning paid plan is required).
