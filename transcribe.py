#!/home/minis/Developer/scripts/YouTubeTranscriptCopier/venv/bin/python

# YouTube Transcript Copier - prosty skrypt bez GUI
# Pobiera link ze schowka i kopiuje transkrypcję

import re
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import pyperclip


def get_video_id(url):
    """Wyciąga ID video z URL YouTube"""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query_params = parse_qs(parsed_url.query)
        return query_params.get("v", [None])[0]
    elif parsed_url.hostname in ["youtu.be"]:
        return parsed_url.path[1:]
    return None


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


def main():
    # Pobierz URL ze schowka
    url = pyperclip.paste().strip()
    
    # Walidacja URL
    if not url or not ("youtube.com" in url or "youtu.be" in url):
        print("ERROR: No valid YouTube URL in clipboard")
        notify("YouTube Transcript Copier", "No valid YouTube URL in clipboard", "critical")
        return
    
    # Wyciągnij ID video
    video_id = get_video_id(url)
    if not video_id:
        print("ERROR: Invalid YouTube URL")
        notify("YouTube Transcript Copier", "Invalid YouTube URL", "critical")
        return
    
    # Pobierz transkrypcję
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id, languages=["pl", "en"])
        text = re.sub(r'\s+', ' ', " ".join([snippet.text for snippet in fetched_transcript.snippets]))
        
        # Skopiuj do schowka
        pyperclip.copy(text)
        print("SUCCESS: Transcript copied to clipboard")
        notify("YouTube Transcript Copier", "Transcript copied to clipboard")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        notify("YouTube Transcript Copier", str(e), "critical")


if __name__ == "__main__":
    main()
