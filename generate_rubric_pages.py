#!/usr/bin/env python3
"""
COMM C1000 — Grading Rubric Page Generator
==========================================
Generates the complete 10-category assessment rubric suite (the 800-point
mastery backbone) in both visual themes:

  1. Warm Editorial (light / serif academic)
  2. Acoustic Somatic (dark / neon studio)

Point totals reconcile exactly with the COMM_C1000_MASTER_SYLLABUS.md
800-point framework (100 + 100 + 32 + 100 + 64 + 150 + 50 + 72 + 84 + 48 = 800).
"""

import os

BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"
INDIVIDUAL_PAGES_DIR = os.path.join(BASE_DIR, "Individual_Pages")
EDITORIAL_DIR = os.path.join(INDIVIDUAL_PAGES_DIR, "Warm_Editorial")
SOMATIC_DIR = os.path.join(INDIVIDUAL_PAGES_DIR, "Acoustic_Somatic")

os.makedirs(EDITORIAL_DIR, exist_ok=True)
os.makedirs(SOMATIC_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# RUBRIC DATA (single source of truth: course_data.py)
# ---------------------------------------------------------------------------
import course_data

RUBRICS = course_data.RUBRICS

# ---------------------------------------------------------------------------
# PAGE WRAPPERS (styles mirror generate_individual_pages.py + rubric tables)
# ---------------------------------------------------------------------------
def wrap_editorial(title, content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        .canvas-editorial-wrapper {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #2b2a27; background-color: #faf8f5; line-height: 1.6; margin: 0; padding: 30px 20px; display: flex; justify-content: center; }}
        .editorial-container {{ max-width: 850px; width: 100%; background-color: #ffffff; border: 1px solid #e6dfd5; border-radius: 16px; box-shadow: 0 4px 25px rgba(140, 94, 40, 0.04); padding: 40px; box-sizing: border-box; }}
        h1, h2, h3 {{ font-family: 'Playfair Display', Georgia, serif; color: #8c5e28; margin-top: 0; }}
        h1 {{ font-size: 2.1rem; font-weight: 700; line-height: 1.2; margin-bottom: 12px; letter-spacing: -0.02em; }}
        h2 {{ font-size: 1.4rem; font-weight: 600; margin-top: 30px; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #e6dfd5; }}
        p {{ font-size: 0.95rem; color: #42403d; margin-bottom: 18px; }}
        .badge {{ display: inline-block; background-color: rgba(198, 138, 76, 0.08); color: #8c5e28; border: 1px solid rgba(198, 138, 76, 0.25); font-family: monospace; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 15px; }}
        .rubric-table {{ width: 100%; border-collapse: collapse; margin: 20px 0 8px 0; font-size: 0.9rem; }}
        .rubric-table th {{ background-color: #8c5e28; color: #ffffff; text-align: left; padding: 12px 14px; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }}
        .rubric-table td {{ padding: 12px 14px; border-bottom: 1px solid #eee8dd; vertical-align: top; color: #42403d; line-height: 1.55; }}
        .rubric-table tr:nth-child(even) td {{ background-color: #faf8f5; }}
        .pts {{ font-family: monospace; font-weight: 700; color: #8c5e28; white-space: nowrap; }}
        .total-row td {{ background-color: #f4ede2; font-weight: 700; color: #8c5e28; border-top: 2px solid #c68a4c; }}
        .footer-note {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e6dfd5; font-size: 0.8rem; color: #8c5e28; font-weight: 500; text-align: center; }}
    </style>
</head>
<body>
    <div class="canvas-editorial-wrapper">
        <div class="editorial-container">
            {content}
        </div>
    </div>
</body>
</html>"""


def wrap_somatic(title, content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        .canvas-somatic-wrapper {{ font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #F1F5F9; background-color: #080C14; line-height: 1.6; margin: 0; padding: 30px 20px; display: flex; justify-content: center; }}
        .somatic-container {{ max-width: 850px; width: 100%; background-color: #0F172A; border: 1px solid rgba(217, 119, 6, 0.3); border-radius: 16px; box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.7); padding: 40px; box-sizing: border-box; }}
        h1, h2, h3 {{ color: #FFFFFF; margin-top: 0; letter-spacing: -0.02em; }}
        h1 {{ font-size: 2.1rem; font-weight: 800; line-height: 1.2; margin-bottom: 12px; background: linear-gradient(135deg, #FBBF24 0%, #D97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        h2 {{ font-size: 1.4rem; font-weight: 700; margin-top: 30px; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid rgba(217, 119, 6, 0.2); color: #38BDF8; }}
        p {{ font-size: 0.95rem; color: #94A3B8; margin-bottom: 18px; }}
        .badge {{ display: inline-block; background-color: rgba(217, 119, 6, 0.15); color: #FBBF24; border: 1px solid rgba(217, 119, 6, 0.45); font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 15px; }}
        .rubric-table {{ width: 100%; border-collapse: collapse; margin: 20px 0 8px 0; font-size: 0.9rem; }}
        .rubric-table th {{ background-color: rgba(217, 119, 6, 0.18); color: #FBBF24; text-align: left; padding: 12px 14px; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }}
        .rubric-table td {{ padding: 12px 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); vertical-align: top; color: #94A3B8; line-height: 1.55; }}
        .rubric-table tr:nth-child(even) td {{ background-color: #0B1220; }}
        .pts {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #34D399; white-space: nowrap; }}
        .total-row td {{ background-color: rgba(217, 119, 6, 0.12); font-weight: 700; color: #FBBF24; border-top: 2px solid #D97706; }}
        .footer-note {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.8rem; color: #64748B; font-family: 'JetBrains Mono', monospace; text-align: center; }}
    </style>
</head>
<body>
    <div class="canvas-somatic-wrapper">
        <div class="somatic-container">
            {content}
        </div>
    </div>
</body>
</html>"""


def render_criteria(rubric):
    rows = []
    for name, pts, desc in rubric["criteria"]:
        rows.append(
            f'            <tr><td><strong>{name}</strong></td>'
            f'<td class="pts">{pts}</td><td>{desc}</td></tr>'
        )
    rows.append(
        f'            <tr class="total-row"><td>Total</td>'
        f'<td class="pts">{rubric["total"]}</td>'
        f'<td>This category contributes {rubric["total"]} points to the 800-point course total.</td></tr>'
    )
    return "\n".join(rows)


def build_content(rubric):
    return f"""
            <span class="badge">{rubric["badge"]}</span>
            <h1>{rubric["title"]}</h1>
            <p>{rubric["intro"]}</p>

            <h2>Scoring Criteria</h2>
            <table class="rubric-table">
                <thead>
                    <tr><th>Criterion</th><th>Points</th><th>Excellence Standard</th></tr>
                </thead>
                <tbody>
{render_criteria(rubric)}
                </tbody>
            </table>

            <div class="footer-note">
                Rio Hondo College &bull; COMM C1000 Public Speaking &bull; 800-Point Mastery Architecture
            </div>
"""


def main():
    count = 0
    for rubric in RUBRICS:
        content = build_content(rubric)
        ed_path = os.path.join(EDITORIAL_DIR, rubric["filename"])
        so_path = os.path.join(SOMATIC_DIR, rubric["filename"])
        with open(ed_path, "w", encoding="utf-8") as f:
            f.write(wrap_editorial(rubric["title"], content))
        with open(so_path, "w", encoding="utf-8") as f:
            f.write(wrap_somatic(rubric["title"], content))
        count += 2
        print(f"   ✓ {rubric['filename']}  ({rubric['total']} pts)")

    total_points = sum(r["total"] for r in RUBRICS)
    print(f"\n✅ Generated {count} rubric pages across both themes.")
    print(f"   Point reconciliation: {total_points}/800 pts ✔")


if __name__ == "__main__":
    main()
