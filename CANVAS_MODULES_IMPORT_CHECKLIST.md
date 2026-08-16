# COMM C1000 — Canvas Modules Import Checklist

Short, ordered runbook for pasting the generated pages into Canvas **Modules**, in course order. Companion to `CANVAS_DEPLOYMENT_CHECKLIST.md` (audio + quizzes). Rubrics are HTML **pages**, not native Canvas rubrics — see section C.

---

## A. What you're importing

**Source: pick ONE theme folder and stay consistent.**

- `Individual_Pages/Warm_Editorial/` **or** `Individual_Pages/Acoustic_Somatic/`
- Don't mix themes in one course. Root-level `Home_Page.html`, `Syllabus.html`, `Opening_Announcement.html`, etc. are mirrored inside each theme folder.

**Page families (per theme):**

| Family | Files | Count |
| :--- | :--- | :---: |
| Week overviews | `Week_01_Overview.html` … `Week_16_Overview.html` | 16 |
| Grading rubrics | `Rubric_*.html` | 10 |
| Speech assignments | `Assignment_Speech_{1,2,3,4}_*.html` | 4 |
| Discussion modules | `{02,05,10,11}_Discussion_Module_*.html` | 4 |
| Course shell | `Syllabus.html`, `Home_Page.html`, `Opening_Announcement.html`, `Profile_Page.html`, `Discussion_Etiquette.html`, `Discussion_Icebreaker.html` | 6 |

---

## B. Build the module skeleton first

Canvas modules **link** pages; create the containers before filling them.

1. **Pages** → create each page by pasting the file's body into the RCE **HTML editor** (`</>`). Keep page names matching the filenames (drop `.html`).
2. **Modules** → create 17 modules in this order:

   | # | Module name | Canvas items to add |
   | :-: | :--- | :--- |
   | 0 | **Start Here & Orientation** | `Syllabus`, `Opening_Announcement`, `Discussion_Etiquette`, `Discussion_Icebreaker`, `Rubric_Scavenger_Hunt_Orientation` |
   | 1 | **Week 1 — Welcome & Framing Apprehension** | `Week_01_Overview` |
   | 2 | **Week 2 — Somatic Control & Acoustic Geometry** | `Week_02_Overview`, `02_Discussion_Module_1_Apprehension_Audit` |
   | 3 | **Week 3 — Speech 1 Pre-Flight** | `Week_03_Overview`, `Assignment_Speech_1_Introductory`, `Rubric_Speech_1_Introductory` |
   | 4 | **Week 4 — Post-Speech 1 & Peer Critique 1** | `Week_04_Overview` |
   | 5 | **Week 5 — Information Literacy** | `Week_05_Overview`, `Rubric_Annotated_Bibliography`, `05_Discussion_Module_2_Verbal_Citations` |
   | 6 | **Week 6 — Visual Aid Design** | `Week_06_Overview` |
   | 7 | **Week 7 — Speech 2 Outlining** | `Week_07_Overview`, `Assignment_Speech_2_Informative`, `Rubric_Speech_2_Informative` |
   | 8 | **Week 8 — Speech 2 Post-Mortem & Peer Critique 2** | `Week_08_Overview` |
   | 9 | **Week 9 — Rhetorical Proofs** | `Week_09_Overview`, `Rubric_Rhetorical_Analysis_Paper` |
   | 10 | **Week 10 — Monroe's Sequence** | `Week_10_Overview`, `10_Discussion_Module_3_Motivated_Sequence` |
   | 11 | **Week 11 — Logical Fallacies** | `Week_11_Overview`, `11_Discussion_Module_4_Logical_Fallacies` |
   | 12 | **Week 12 — Speech 3 Pre-Flight** | `Week_12_Overview`, `Assignment_Speech_3_Persuasive_Policy`, `Rubric_Speech_3_Persuasive_Policy` |
   | 13 | **Week 13 — Post-Persuasion** | `Week_13_Overview` |
   | 14 | **Week 14 — Speech 4 Execution** | `Week_14_Overview`, `Assignment_Speech_4_Ceremonial`, `Rubric_Speech_4_Ceremonial` |
   | 15 | **Week 15 — Final Peer Critique & Synthesis** | `Week_15_Overview` |
   | 16 | **Week 16 — Capstone** | `Week_16_Overview` |

3. Add items with the **+** button → **Page** → pick the existing page. Order within a module: overview first, then rubric/assignment/discussion.

---

## C. Rubric placement — three recurring rubrics span multiple weeks

Nine rubrics attach to a single week; three are **course-wide** and should also be reachable from every week they apply to:

| Rubric page | Points | First home | Also reference from |
| :--- | :---: | :--- | :--- |
| `Rubric_Weekly_Discussions` | 84 | Start Here | Weeks 2, 5, 9, 10, 11 (any discussion module) |
| `Rubric_Chapter_Quizzes` | 48 | Start Here | Every week with a quiz deadline |
| `Rubric_Peer_Critique_Rounds` | 72 | Week 4 | Weeks 8 and 15 (rounds 2 & 3) |

Canvas doesn't auto-sync pages, so add the **same page** as a module item in each of those weeks (or hyperlink the module items to the one page). Same page = single source of truth; no duplication to maintain.

**Native-rubric option:** for auto-scoring, recreate the tables as **native Canvas rubrics** (Outcomes → Rubrics) and attach each to its assignment. The generated HTML pages then serve as the student-facing copy. Do this *after* the pages are imported, or paste the criteria text into the rubric builder.

---

## D. Import order runbook (top → bottom)

1. Create the 17 modules (skeletons) in week order — section B.
2. Create & link all **course-shell pages** in Start Here (`Syllabus`, `Opening_Announcement`, etiquette, icebreaker).
3. Import the **16 week overview pages**, one per module, in week order.
4. Import the **4 assignment pages** + their 4 single-week rubrics into Weeks 3, 7, 12, 14.
5. Import the **4 discussion-module pages** into Weeks 2, 5, 10, 11.
6. Add the **3 recurring rubrics** to Start Here, then re-link them in the weeks listed in section C.
7. Verify point totals reconcile to **800** (rubric headers list each category's points).
8. Set module availability dates (or publish-all at once for a self-paced open course) and **Publish**.

**Cross-reference:** the audio players inside `Week_XX_Overview.html` and `Home_Page.html` need the `src` swap from `CANVAS_DEPLOYMENT_CHECKLIST.md` section A — do that when you paste each week page.
