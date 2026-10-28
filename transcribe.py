#!/usr/bin/env python3

# YouTube Transcript Copier - prosty skrypt bez GUI
# Pobiera link ze schowka i kopiuje transkrypcję

import json
import os
import re
import subprocess
from urllib.parse import urlparse, parse_qs
import pyperclip
import yt_dlp


APP_NAME = "YouTube Transcript Copier"
LANGUAGES = ["pl", "en"]
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
# Opcjonalny plik z ciasteczkami YouTube (format Netscape) - pomaga yt-dlp, gdy YouTube żąda logowania
COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")


def get_video_id(url):
    """Wyciąga ID video z URL YouTube"""
    if "://" not in url:
        url = "https://" + url
    parsed_url = urlparse(url)
    hostname = (parsed_url.hostname or "").lower()
    path_parts = [part for part in parsed_url.path.split("/") if part]

    video_id = None
    if hostname in YOUTUBE_HOSTS:
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        elif len(path_parts) >= 2 and path_parts[0] in ("shorts", "live", "embed", "v"):
            video_id = path_parts[1]
    elif hostname == "youtu.be" and path_parts:
        video_id = path_parts[0]

    if video_id and VIDEO_ID_PATTERN.match(video_id):
        return video_id
    return None


def pick_subtitle_track(tracks, original_only=False):
    """Wybiera ścieżkę napisów w formacie json3 wg kolejności LANGUAGES (np. 'en' pasuje też do 'en-US')"""
    for language in LANGUAGES:
        for track_language, formats in tracks.items():
            base_language = track_language.split("-")[0]
            if base_language != language:
                continue
            # Automatyczne napisy oznaczone "-orig" to oryginał, pozostałe są maszynowo tłumaczone
            if original_only and not track_language.endswith("-orig"):
                continue
            for subtitle_format in formats:
                if subtitle_format.get("ext") == "json3":
                    return subtitle_format["url"]
    return None


def fetch_transcript(video_id):
    """Pobiera napisy przez yt-dlp"""
    class SilentLogger:
        # Wycisza ostrzeżenia yt-dlp - wynik i tak trafia do powiadomienia
        def debug(self, msg): pass
        def info(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass

    options = {"skip_download": True, "quiet": True, "no_warnings": True, "logger": SilentLogger()}
    if os.path.isfile(COOKIES_FILE):
        options["cookiefile"] = COOKIES_FILE
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        subtitle_url = (
            pick_subtitle_track(info.get("subtitles") or {})
            or pick_subtitle_track(info.get("automatic_captions") or {}, original_only=True)
            or pick_subtitle_track(info.get("automatic_captions") or {})
        )
        if not subtitle_url:
            raise LookupError("No Polish or English subtitles found for this video.")
        data = json.loads(ydl.urlopen(subtitle_url).read().decode("utf-8"))

    # Segmenty w obrębie zdarzenia sklejamy bezpośrednio, a kolejne zdarzenia (linie napisów) spacją
    lines = [
        "".join(segment.get("utf8", "") for segment in event.get("segs", []))
        for event in data.get("events", [])
    ]
    return " ".join(lines)


def notify(summary, body, urgency="normal"):
    """Wyślij powiadomienie systemowe, jeśli notify-send jest dostępne."""
    try:
        subprocess.run(
            ["notify-send", "-u", urgency, summary, body],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass


def fail(message):
    print(f"ERROR: {message}")
    notify(APP_NAME, message, "critical")


def short_error_message(error):
    """Skraca komunikat błędu yt-dlp do pierwszej niepustej linii"""
    message = str(error)
    if "Sign in to confirm" in message:
        return "YouTube requires sign-in - see 'cookies.txt' in README."
    lines = [line.strip() for line in message.splitlines() if line.strip()]
    return lines[0].removeprefix("ERROR: ") if lines else type(error).__name__


def main():
    # Pobierz URL ze schowka
    url = pyperclip.paste().strip()

    # Walidacja URL
    if not url or not ("youtube.com" in url or "youtu.be" in url):
        fail("No valid YouTube URL in clipboard")
        return

    # Wyciągnij ID video
    video_id = get_video_id(url)
    if not video_id:
        fail("Invalid YouTube URL")
        return

    # Pobierz transkrypcję
    try:
        text = fetch_transcript(video_id)
    except Exception as error:
        fail(short_error_message(error))
        return

    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        fail("The transcript is empty")
        return

    # Skopiuj do schowka
    pyperclip.copy(text)
    print("SUCCESS: Transcript copied to clipboard")
    notify(APP_NAME, "Transcript copied to clipboard")


if __name__ == "__main__":
    main()
