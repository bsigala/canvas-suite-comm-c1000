# COMM C1000 — Canvas Deployment Checklist

Short, ordered runbook for getting the generated audio + quizzes into Canvas.

---

## A. Audio embeds (weekly touchpoints + greetings)

**Files on disk**

- `Audio_Assets/week_01_rsi_touchpoint.mp3` … `week_16_rsi_touchpoint.mp3` (16)
- `Audio_Assets/week_01_rsi_touchpoint.m4a` … `week_16_rsi_touchpoint.m4a` (16)
- `Audio_Assets/course_welcome_greeting.{mp3,m4a}` + `opening_announcement_greeting.{mp3,m4a}`
- Player snippets: `Audio_Assets/course_welcome_greeting.player.html`, `opening_announcement_greeting.player.html`

**Where they're referenced**

- `Home_Page.html` — 16-player touchpoint strip (also mirrored in `Individual_Pages/{Warm_Editorial,Acoustic_Somatic}/Home_Page.html`)
- `Individual_Pages/{Warm_Editorial,Acoustic_Somatic}/Week_XX_Overview.html` — one player per week page
- `Audio_Assets/*.player.html` — greeting embeds

**Steps**

1. Canvas → **Files** → create two folders: `Touchpoints` and `Greetings`.
2. Upload all 16 `week_XX_rsi_touchpoint.mp3` **and** `.m4a` into `Touchpoints`; greetings into `Greetings`. **Keep filenames identical** — the embeds reference them by name.
3. Paste each page into the Rich Content Editor's **HTML editor** (the `</>` button):
   - Homepage → paste `Home_Page.html` body.
   - Each week module → paste that week's `Week_XX_Overview.html` body.
   - Announcement / welcome → paste the `*.player.html` block.
4. **Swap the `src`s.** The local paths (`Audio_Assets/...` or `../../Audio_Assets/...`) won't resolve in Canvas. For each player, replace both `<source src="...">` values with the Canvas file URL:
   - Files → the file's **⋮ menu → Copy Link** (looks like `/courses/####/files/####/download`).
   - Or faster: in the RCE, delete the `<audio>` block and re-insert it with the **media/upload tool**, which fills the correct URL automatically.
5. Save & Publish.

**Cloned-voice note:** after running `clone_voice_and_regenerate.py`, the files are regenerated with the **same filenames**. Re-upload to Canvas and choose **Replace** so the file URLs (and your already-swapped `src`s) keep working with zero page edits.

---

## B. Chapter quiz QTI imports

**Files**

- `COMM_C1000_Chapters_1-5_Quiz_QTI.zip` (5 items)
- `COMM_C1000_Chapters_6-16_Quiz_QTI.zip` (11 items)

**Steps**

1. Course → **Settings** → **Import Course Content**.
2. Content Type: **QTI .zip file** → choose the zip → **Import**.
3. Repeat for the second zip.
4. Both quizzes appear under **Quizzes** (QTI 1.2 / classic quizzes). Set point values, availability dates, and publish.
5. If the course uses **New Quizzes**, Canvas prompts to migrate each imported quiz — accept on the Quiz page.

---

## Recommended order (top → bottom)

1. Import both QTI zips (no dependencies).
2. Upload audio to Canvas Files.
3. Paste pages and swap `src`s.
4. (Later) Clone voice → re-upload cloned audio via **Replace**.
