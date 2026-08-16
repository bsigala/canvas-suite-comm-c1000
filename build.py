#!/usr/bin/env python3
"""One-command build for the COMM C1000 course package.

Deterministic steps (pages, rubrics, cartridge) run by default. The steps
that need an API key (quiz QTI generation, weekly audio TTS) run only with
--all.

Usage:
  python3 build.py           # deterministic rebuild + reconciliation
  python3 build.py --all     # also regenerate quizzes and audio (needs keys)
"""

import subprocess
import sys

import course_data as cd


def run(step, *cmd):
    print("\n[build] %s" % step)
    subprocess.run([sys.executable] + list(cmd), check=True)


def main():
    print("[build] verifying course data")
    for line in cd.verify():
        print("        " + line)

    run("individual pages", "generate_individual_pages.py")
    run("rubric pages", "generate_rubric_pages.py")
    run("canvas cartridge (pages + assignments + audio)", "generate_canvas_cartridge.py")

    if "--all" in sys.argv:
        run("quiz QTI (chapters 1-5)", "generate_comm_c1000_quizzes.py")
        run("quiz QTI (chapters 6-16)", "generate_quizzes_ch6_16.py")
        run("weekly audio touchpoints (TTS)", "generate_course_audio.py")

    print("\n[build] done")


if __name__ == "__main__":
    main()
