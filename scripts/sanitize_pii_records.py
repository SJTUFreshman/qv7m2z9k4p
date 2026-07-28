#!/usr/bin/env python3
"""Remove the three non-author faculty profiles identified in the ethics review."""

from __future__ import annotations

import json
from pathlib import Path


TARGETS = {
    "PRISM-EN-004393": {
        "heading": "## Teacher Introduction",
        "title": "History of Abstract Algebra",
        "subtitle": "Teacher Introduction",
    },
    "PRISM-EN-004395": {
        "heading": "## Instructor Introduction",
        "title": "History of Abstract Algebra",
        "subtitle": "Instructor Introduction",
    },
    "PRISM-ZH-001820": {
        "heading": "## 教师自我介绍",
        "title": "抽象代数历史",
        "subtitle": "授课教师介绍",
    },
}


def clean_instruction(instruction: str, heading: str) -> str:
    # The profile was a complete Markdown subsection. Keep the task and its
    # context, while removing the personal profile text itself.
    start = instruction.find("\n\n", instruction.find("Markdown"))
    if start < 0:
        raise ValueError("instruction body not found")
    body = instruction[start + 2 :]
    marker = body.find("<!-- CONTEXT:BEGIN -->")
    if marker >= 0:
        suffix = body[marker:]
        body = heading + "\n\n" + suffix
    else:
        body = body.splitlines()[0].split(":", 1)[0].rstrip() if body else heading
        body = heading if not body.startswith("#") else body
    return instruction[: start + 2] + body


def clean_reference(language: str, title: str, subtitle: str) -> str:
    if language == "zh":
        return (
            "from manim import *\n\n"
            "class TeacherIntroduction(Scene):\n"
            "    def construct(self):\n"
            f"        title = Text(\"{subtitle}\", font_size=34, font=\"AR PL UKai CN\", weight=BOLD)\n"
            "        title.to_edge(UP, buff=0.5)\n"
            "        topic = Text(\"抽象代数历史\", font_size=30, font=\"AR PL UKai CN\")\n"
            "        topic.next_to(title, DOWN, buff=0.6)\n"
            "        self.play(Write(title), FadeIn(topic))\n"
            "        self.wait(2)\n"
        )
    return (
        "from manim import *\n"
        "from manim import config\n"
        "Text.set_default(font='SimHei')\n\n"
        "class TeacherIntroduction(Scene):\n"
        "    def construct(self):\n"
        f"        title = Text('{title}', font_size=48, weight=BOLD)\n"
        "        title.to_edge(UP)\n"
        f"        subtitle = Text('{subtitle}', font_size=36, color=BLUE)\n"
        "        subtitle.next_to(title, DOWN, buff=0.4)\n"
        "        self.play(Write(title), FadeIn(subtitle, shift=UP))\n"
        "        self.wait(2)\n"
    )


def sanitize(src: Path, dst: Path) -> int:
    rows = []
    changed = 0
    for raw in src.open(encoding="utf-8"):
        row = json.loads(raw)
        spec = TARGETS.get(row["id"])
        if spec:
            row["instruction"] = clean_instruction(row["instruction"], spec["heading"])
            row["reference_answer"] = clean_reference(row["language"], spec["title"], spec["subtitle"])
            changed += 1
        rows.append(row)
    with dst.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return changed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path)
    parser.add_argument("dst", type=Path)
    args = parser.parse_args()
    print(f"sanitized {sanitize(args.src, args.dst)} records")
