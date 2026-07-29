#!/usr/bin/env python3
"""Remove identified faculty and author profile PII from release records."""

from __future__ import annotations

import json
from pathlib import Path


TARGETS = {
    "PRISM-EN-004393": {
        "heading": "## Teacher Introduction",
        "title": "History of Abstract Algebra",
        "subtitle": "Teacher Introduction",
        "topic": "History of Abstract Algebra",
    },
    "PRISM-EN-004395": {
        "heading": "## Instructor Introduction",
        "title": "History of Abstract Algebra",
        "subtitle": "Instructor Introduction",
        "topic": "History of Abstract Algebra",
    },
    "PRISM-ZH-001820": {
        "heading": "## 教师自我介绍",
        "title": "抽象代数历史",
        "subtitle": "授课教师介绍",
        "topic": "抽象代数历史",
    },
    "PRISM-EN-004375": {
        "heading": "## About Me",
        "title": "About Me",
        "subtitle": "General Introduction",
        "topic": "About Me",
    },
    "PRISM-EN-004483": {
        "heading": "## Instructor",
        "title": "Instructor",
        "subtitle": "General Introduction",
        "topic": "Instructor",
    },
    "PRISM-EN-005049": {
        "heading": "# Introduction\n\n## About Me",
        "title": "Introduction",
        "subtitle": "About Me",
        "topic": "About Me",
    },
    "PRISM-ZH-001937": {
        "heading": "## 关于我",
        "title": "关于我",
        "subtitle": "个人简介",
        "topic": "关于我",
    },
}

PROFILE_MARKERS = (
    "qian chen",
    "钱忱",
    "qianc@",
    "sjtu.edu.cn",
    "qianc62.github.io",
    "school of artificial intelligence",
    "人工智能学院",
    "room 330",
)


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
        body = heading
    return instruction[: start + 2] + body


def clean_reference(language: str, title: str, subtitle: str, topic: str) -> str:
    if language == "zh":
        return (
            "from manim import *\n\n"
            "class TeacherIntroduction(Scene):\n"
            "    def construct(self):\n"
            f"        title = Text(\"{subtitle}\", font_size=34, font=\"AR PL UKai CN\", weight=BOLD)\n"
            "        title.to_edge(UP, buff=0.5)\n"
            f"        topic = Text(\"{topic}\", font_size=30, font=\"AR PL UKai CN\")\n"
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
        profile_text = f"{row['instruction']}\n{row['reference_answer']}".lower()
        if spec and any(marker in profile_text for marker in PROFILE_MARKERS):
            row["instruction"] = clean_instruction(row["instruction"], spec["heading"])
            row["reference_answer"] = clean_reference(
                row["language"], spec["title"], spec["subtitle"], spec["topic"]
            )
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
