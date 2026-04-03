# YouTube Transcript Copier

A simple Linux script that:

- reads a YouTube video URL from the clipboard,
- fetches a transcript in `pl` or `en`,
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

- `youtube-transcript-api`
- `pyperclip`

## Common Issues

### `No valid YouTube URL in clipboard`

There is no valid YouTube URL in the clipboard.

### `Pyperclip could not find a copy/paste mechanism`

A clipboard backend is missing. Install:

- `wl-clipboard` for Wayland
- or `xclip` for X11

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
