# PPL video transcripts

This directory is populated by `scripts/fetch-ppl-transcripts.py`.

The extractor reads the lesson cards in `ppl/ppl-ground-course.html` and downloads
the **original English YouTube automatic captions** (`en-orig`) as raw WebVTT
files. It downloads captions only; it does not download video or audio.

Raw VTT is intentionally preserved because timestamps are useful when lesson
notes need to point back to a visual demonstration in the video.

## Requirements

- Python 3
- `yt-dlp` available on `PATH`

Verify:

```bash
python3 --version
yt-dlp --version
```

## Recommended first run

Test a small sample before downloading the full course:

```bash
python3 scripts/fetch-ppl-transcripts.py --lesson 2 --lesson 15 --lesson 39
```

If the sample succeeds, download the full course:

```bash
python3 scripts/fetch-ppl-transcripts.py
```

The script pauses two seconds between lessons by default to reduce the chance of
YouTube rate limiting. Existing transcript files are skipped.

## Useful options

See every discovered lesson and target filename without downloading anything:

```bash
python3 scripts/fetch-ppl-transcripts.py --dry-run
```

Download or retry one lesson:

```bash
python3 scripts/fetch-ppl-transcripts.py --lesson 35.2
```

Re-download an existing transcript:

```bash
python3 scripts/fetch-ppl-transcripts.py --lesson 2 --force
```

Use cookies from a logged-in browser if YouTube asks you to sign in or reports a
bot check:

```bash
python3 scripts/fetch-ppl-transcripts.py --cookies-from-browser chrome
```

Replace `chrome` with another browser supported by your yt-dlp installation,
such as `firefox`, `safari`, or `brave`.

Change the pause between lessons:

```bash
python3 scripts/fetch-ppl-transcripts.py --delay 5
```

## Output

Files are named from the course lesson number and title, for example:

```text
ppl/transcripts/02-creating-lift.en-orig.vtt
ppl/transcripts/15-types-of-airspace-explained.en-orig.vtt
ppl/transcripts/35-2-non-towered-radio-calls.en-orig.vtt
ppl/transcripts/39-weather-basics.en-orig.vtt
```

At the end of a run, the script reports how many lessons were downloaded,
skipped, or failed. A failed bulk run is safe to rerun because successful files
are skipped by default.

## After extraction

Inspect the results and commit them to the current branch:

```bash
git status --short ppl/transcripts
git add ppl/transcripts
git commit -m "Add PPL video transcripts"
git push
```

Once the VTT files are in the repository, the lesson notes can be audited and
regenerated directly against the actual lesson transcripts.
