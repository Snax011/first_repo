from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd
import yt_dlp
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "replace-this-with-a-long-random-secret"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
VIDEO_DIR = STATIC_DIR / "videos"
CSV_PATH = DATA_DIR / "highlights_log.csv"

# Ensure folders exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str, max_len: int = 120) -> str:
    """
    Create a filesystem-safe filename (Windows-friendly).
    Keeps it readable while removing characters that break paths.
    """
    name = (name or "").strip()
    name = name.replace("\u2014", "-").replace("\u2013", "-")  # em/en dash -> hyphen
    name = re.sub(r"[^\w\s\-.()$$$$]+", "", name, flags=re.UNICODE)  # remove weird chars
    name = re.sub(r"\s+", " ", name).strip()
    name = name.replace(" ", "_")
    if not name:
        name = "video"
    return name[:max_len]


def ensure_csv_exists() -> None:
    if not CSV_PATH.exists():
        df = pd.DataFrame(columns=["title", "start_time", "duration", "tags", "video_file"])
        df.to_csv(CSV_PATH, index=False, encoding="latin1")


def load_highlights() -> list[dict]:
    ensure_csv_exists()
    df = pd.read_csv(CSV_PATH, encoding="latin1")

    # Normalize expected columns
    for col in ["title", "start_time", "duration", "tags", "video_file"]:
        if col not in df.columns:
            df[col] = ""

    # Replace NaN with empty strings for templates
    df = df.fillna("")

    # Make duration numeric-ish if possible, but don't crash if not
    def _coerce_duration(v):
        try:
            return float(v) if str(v).strip() != "" else 0.0
        except Exception:
            return 0.0

    df["duration"] = df["duration"].apply(_coerce_duration)

    return df.to_dict(orient="records")


def save_highlight(entry: dict) -> None:
    ensure_csv_exists()
    df = pd.read_csv(CSV_PATH, encoding="latin1")

    # If CSV existed but had different columns, normalize
    for col in ["title", "start_time", "duration", "tags", "video_file"]:
        if col not in df.columns:
            df[col] = ""

    new_row = pd.DataFrame([entry])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_PATH, index=False, encoding="latin1")


@app.route("/")
def index():
    highlights = load_highlights()
    return render_template("index.html", highlights=highlights)


@app.route("/download_video", methods=["GET", "POST"])
def download_video():
    if request.method == "GET":
        return render_template("download_video.html")

    youtube_url = (request.form.get("youtube_url") or "").strip()
    title = (request.form.get("title") or "").strip()
    start_time = (request.form.get("start_time") or "").strip()
    duration = (request.form.get("duration") or "").strip()
    tags = (request.form.get("tags") or "").strip()

    if not youtube_url:
        flash("YouTube URL is required.", "error")
        return redirect(url_for("download_video"))

    # yt-dlp output template. Use id to avoid collisions, but keep readable title.
    outtmpl = str(VIDEO_DIR / "%(title).80s__%(id)s.%(ext)s")

    ydl_opts = {
        "format": "mp4/bestvideo+bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        # Ensure Windows filenames are safe; we additionally sanitize ourselves for CSV title.
        "restrictfilenames": False,
        # Optional: keep it more compatible
        "merge_output_format": "mp4",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)

        # Determine the final file name yt-dlp wrote
        # `prepare_filename` returns the path before postprocessors sometimes,
        # but for most mp4 merges it's accurate enough. We'll also fall back.
        with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
            expected_path = ydl2.prepare_filename(info)

        expected = Path(expected_path)
        if expected.suffix.lower() != ".mp4":
            # If merge_output_format mp4 is used, final might be .mp4 even if expected isn't.
            alt = expected.with_suffix(".mp4")
            final_path = alt if alt.exists() else expected
        else:
            final_path = expected

        # If still not found, try best-effort scan by id in VIDEO_DIR
        if not final_path.exists():
            vid = info.get("id")
            if vid:
                matches = list(VIDEO_DIR.glob(f"*__{vid}.*"))
                if matches:
                    final_path = matches[0]

        if not final_path.exists():
            raise FileNotFoundError(
                "Download finished but the output file could not be located in static/videos."
            )

        video_filename = final_path.name

        video_title = info.get("title") or "video"
        safe_title = sanitize_filename(title if title else video_title)

        # Parse duration field from form safely
        try:
            duration_val = float(duration) if duration.strip() else 0.0
        except Exception:
            duration_val = 0.0

        entry = {
            "title": safe_title,
            "start_time": start_time if start_time else "0:00",
            "duration": duration_val,
            "tags": tags,
            "video_file": video_filename,
        }

        save_highlight(entry)
        flash(f"Added highlight and linked video: {video_filename}", "success")
        return redirect(url_for("index"))

    except Exception as e:
        flash(f"Error downloading video: {e}", "error")
        return redirect(url_for("download_video"))


if __name__ == "__main__":
    app.run(debug=True)
