#!/usr/bin/env python3
"""Download English-original YouTube automatic captions for the PPL course.

The script reads ppl/ppl-ground-course.html, discovers each lesson's number,
title, and YouTube URL, and saves raw WebVTT captions under ppl/transcripts/.

It downloads captions only; it never downloads video or audio.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


EXPECTED_LESSON_COUNT = 64
DEFAULT_DELAY_SECONDS = 2.0
CAPTION_LANGUAGE = "en-orig"


@dataclass
class Lesson:
    number: str = ""
    title: str = ""
    video_url: str = ""

    @property
    def canonical_number(self) -> str:
        return canonicalize_lesson_number(self.number)

    @property
    def stem(self) -> str:
        return f"{filename_lesson_number(self.number)}-{slugify(self.title)}"


class CourseLessonParser(HTMLParser):
    """Extract lesson number, title, and video URL from course lesson cards."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lessons: list[Lesson] = []
        self.current: Lesson | None = None
        self.lesson_div_depth = 0
        self.capture_field: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        classes = set(attr_map.get("class", "").split())

        if tag == "div" and "lesson" in classes:
            self.current = Lesson()
            self.lesson_div_depth = 1
            self.capture_field = None
            return

        if self.current is not None and tag == "div":
            self.lesson_div_depth += 1

        if self.current is None:
            return

        if tag == "span" and "l-num" in classes:
            self.capture_field = "number"
        elif tag == "span" and "l-title" in classes:
            self.capture_field = "title"
        elif tag == "a" and "btn-video" in classes:
            self.current.video_url = attr_map.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        if self.current is None:
            return

        if tag == "span":
            self.capture_field = None

        if tag == "div":
            self.lesson_div_depth -= 1
            if self.lesson_div_depth == 0:
                if self.current.number and self.current.title and self.current.video_url:
                    self.lessons.append(self.current)
                self.current = None
                self.capture_field = None

    def handle_data(self, data: str) -> None:
        if self.current is None or self.capture_field is None:
            return

        value = " ".join(data.split())
        if not value:
            return

        current_value = getattr(self.current, self.capture_field)
        setattr(
            self.current,
            self.capture_field,
            f"{current_value} {value}".strip(),
        )


def canonicalize_lesson_number(value: str) -> str:
    value = value.strip()
    if "." in value:
        head, tail = value.split(".", 1)
        return f"{int(head)}.{tail}"
    return str(int(value))


def filename_lesson_number(value: str) -> str:
    value = value.strip()
    if "." in value:
        head, tail = value.split(".", 1)
        return f"{int(head):02d}-{tail}"
    return f"{int(value):02d}"


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.replace("'", "").replace("’", "")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def parse_course(course_path: Path) -> list[Lesson]:
    parser = CourseLessonParser()
    parser.feed(course_path.read_text(encoding="utf-8"))
    return parser.lessons


def build_command(
    yt_dlp: str,
    lesson: Lesson,
    out_dir: Path,
    cookies_from_browser: str | None,
) -> list[str]:
    output_template = str(out_dir / f"{lesson.stem}.%(ext)s")

    command = [
        yt_dlp,
        "--skip-download",
        "--write-auto-subs",
        "--sub-langs",
        CAPTION_LANGUAGE,
        "--sub-format",
        "vtt",
        "-o",
        output_template,
    ]

    if cookies_from_browser:
        command.extend(["--cookies-from-browser", cookies_from_browser])

    command.append(lesson.video_url)
    return command


def tail(text: str, lines: int = 10) -> str:
    chunks = [line for line in text.splitlines() if line.strip()]
    return "\n".join(chunks[-lines:])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download en-orig YouTube automatic captions for every PPL lesson "
            "listed in ppl/ppl-ground-course.html."
        )
    )
    parser.add_argument(
        "--lesson",
        action="append",
        default=[],
        metavar="NUMBER",
        help="Download only this lesson number. Repeatable, e.g. --lesson 2 --lesson 35.2.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download transcripts that already exist.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        metavar="SECONDS",
        help=f"Pause between lessons to reduce rate-limit risk (default: {DEFAULT_DELAY_SECONDS}).",
    )
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        help="Pass browser cookies to yt-dlp, e.g. chrome, firefox, safari, or brave.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show discovered lessons and output paths without downloading captions.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.delay < 0:
        print("error: --delay must be zero or greater", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parents[1]
    course_path = repo_root / "ppl" / "ppl-ground-course.html"
    out_dir = repo_root / "ppl" / "transcripts"

    if not course_path.exists():
        print(f"error: course page not found: {course_path}", file=sys.stderr)
        return 2

    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        print(
            "error: yt-dlp was not found on PATH.\n"
            "Install it first, then verify with: yt-dlp --version",
            file=sys.stderr,
        )
        return 2

    lessons = parse_course(course_path)
    if not lessons:
        print("error: no lesson cards with video links were found", file=sys.stderr)
        return 2

    print(f"Discovered {len(lessons)} lesson videos in {course_path.relative_to(repo_root)}.")
    if len(lessons) != EXPECTED_LESSON_COUNT:
        print(
            f"warning: expected {EXPECTED_LESSON_COUNT} lessons, found {len(lessons)}. "
            "Continuing with what the course page contains."
        )

    requested = {canonicalize_lesson_number(value) for value in args.lesson}
    if requested:
        known = {lesson.canonical_number for lesson in lessons}
        missing = sorted(requested - known)
        if missing:
            print(f"error: lesson(s) not found: {', '.join(missing)}", file=sys.stderr)
            return 2
        lessons = [lesson for lesson in lessons if lesson.canonical_number in requested]

    out_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        for lesson in lessons:
            print(
                f"{lesson.number:>4}  {lesson.title}\n"
                f"      {lesson.video_url}\n"
                f"      -> ppl/transcripts/{lesson.stem}.{CAPTION_LANGUAGE}.vtt"
            )
        return 0

    successes: list[tuple[Lesson, Path]] = []
    skipped: list[tuple[Lesson, Path]] = []
    failures: list[tuple[Lesson, str]] = []

    for index, lesson in enumerate(lessons, start=1):
        expected = out_dir / f"{lesson.stem}.{CAPTION_LANGUAGE}.vtt"

        if expected.exists() and not args.force:
            print(f"[{index:02d}/{len(lessons):02d}] SKIP {lesson.number} {lesson.title}")
            skipped.append((lesson, expected))
            continue

        if args.force and expected.exists():
            expected.unlink()

        print(f"[{index:02d}/{len(lessons):02d}] GET  {lesson.number} {lesson.title}")
        command = build_command(
            yt_dlp=yt_dlp,
            lesson=lesson,
            out_dir=out_dir,
            cookies_from_browser=args.cookies_from_browser,
        )

        try:
            result = subprocess.run(
                command,
                cwd=repo_root,
                text=True,
                capture_output=True,
                timeout=180,
                check=False,
            )
        except subprocess.TimeoutExpired:
            failures.append((lesson, "yt-dlp timed out after 180 seconds"))
        else:
            if result.returncode == 0 and expected.exists():
                successes.append((lesson, expected))
            else:
                details = tail("\n".join([result.stdout, result.stderr]))
                if not details:
                    details = f"yt-dlp exited with status {result.returncode}"
                failures.append((lesson, details))

        if index != len(lessons) and args.delay:
            time.sleep(args.delay)

    print("\nTranscript extraction summary")
    print("-----------------------------")
    print(f"Downloaded: {len(successes)}")
    print(f"Skipped:    {len(skipped)}")
    print(f"Failed:     {len(failures)}")
    print(f"Output:     {out_dir.relative_to(repo_root)}/")

    if failures:
        print("\nFailures:")
        for lesson, details in failures:
            print(f"\n- Lesson {lesson.number}: {lesson.title}")
            print(details)
        print(
            "\nRe-run failed lessons individually, for example:\n"
            "  python3 scripts/fetch-ppl-transcripts.py --lesson 2\n"
            "If YouTube requires authentication, add:\n"
            "  --cookies-from-browser chrome"
        )
        return 1

    print("\nAll requested transcript downloads completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
