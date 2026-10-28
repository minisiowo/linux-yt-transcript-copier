# YouTube Transcript Copier

A simple Linux script that:

- reads a YouTube video URL from the clipboard,
- fetches a transcript in `pl` or `en` via `yt-dlp`,
- copies the result back to the clipboard,
- sends a desktop notification through `notify-send`.

## Requirements

- Linux
- Python 3
- clipboard support:
  - `wl-clipboard` for Wayland
  - or `xclip` for X11
- `notify-send`:
  - on Debian/Ubuntu this is usually provided by `libnotify-bin`

## Project Files

- `transcribe.py` - main script
- `requirements.txt` - Python dependencies
- `install.sh` - simple installer for dependencies and the `.desktop` launcher
- `youtube-transcript-copier.desktop` - desktop entry template
- `youtube-transcript-copier.png` - application icon

## Installation

The easiest way:

```bash
chmod +x install.sh
./install.sh
```

The script:

- detects the package manager,
- installs system dependencies,
- creates a `venv` if it does not exist,
- installs Python packages,
- generates a launcher at `~/.local/share/applications/youtube-transcript-copier.desktop`.

## Manual Run

If you do not want to use the launcher:

```bash
./venv/bin/python transcribe.py
```

## Usage

1. Copy a YouTube video URL to the clipboard.
2. Run the script or launch the app from your application launcher.
3. The transcript will be copied to the clipboard.
4. You will get a success or error notification.

## `.desktop` Launcher

The installer writes this file:

```text
~/.local/share/applications/youtube-transcript-copier.desktop
```

The generated launcher contains the correct local paths to:

- `venv/bin/python`
- `transcribe.py`
- `youtube-transcript-copier.png`

## Python Dependencies

- `yt-dlp` - fetching subtitles
- `pyperclip` - clipboard operations

`yt-dlp` breaks whenever YouTube changes things, so update it from time to time:

```bash
./venv/bin/pip install --upgrade yt-dlp
```

Re-running `./install.sh` also upgrades it.

## Why `yt-dlp` instead of `youtube-transcript-api`

Earlier versions used `youtube-transcript-api`. It was replaced because it stopped working reliably.

| | `youtube-transcript-api` | `yt-dlp` |
|---|---|---|
| Speed | Fast (1-2 requests) | Slower (~1-3 s, fetches full video info) |
| Size | Small library | Large dependency |
| Maintenance | Mostly a single maintainer, fixes can take weeks | Large, very active community, fixes for YouTube changes usually within days |
| Blocking | Often blocked by YouTube (`IpBlocked`, `RequestBlocked`), even on home IPs | Better at avoiding blocks (switches between YouTube clients, supports cookies) |
| Python 3.15 | Not supported yet (does not install) | Supported |

For a script run by hand from time to time, reliability matters more than a second of latency, so `yt-dlp` is the better choice.

Combining both (the API first, `yt-dlp` as a fallback) would only be faster in the cases where the API happens to work. It is not worth a second dependency and the extra code.

The trade-off: `yt-dlp` has to be kept up to date. An old version quickly stops working with YouTube.

## Common Issues

### `No valid YouTube URL in clipboard`

There is no valid YouTube URL in the clipboard.

### `Pyperclip could not find a copy/paste mechanism`

A clipboard backend is missing. Install:

- `wl-clipboard` for Wayland
- or `xclip` for X11

### YouTube is blocking requests / sign-in required

YouTube sometimes asks for sign-in ("confirm you're not a bot"), especially after many requests.
If you get `YouTube requires sign-in`, see [Using cookies](#using-cookies).

### Using cookies

When YouTube asks yt-dlp to "confirm you're not a bot", yt-dlp can use cookies from your browser:

1. Export your YouTube cookies in Netscape format (e.g. with a "cookies.txt" browser extension) while signed in to YouTube.
2. Save the file as `cookies.txt` next to `transcribe.py`.

`cookies.txt` is in `.gitignore`. Never commit or share it, because it gives access to your Google account.

### `bad interpreter: No such file or directory`

This usually means the project directory was moved or renamed, and the existing `venv` still points to the old path.

The simplest fix:

```bash
rm -rf venv
./install.sh
```

## Notes

- This project is intended for Linux.
- Notifications require an active graphical session.
- `install.sh` installs system packages with `sudo`.
