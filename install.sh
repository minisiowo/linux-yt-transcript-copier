#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

detect_package_manager() {
    if command -v apt >/dev/null 2>&1; then
        echo "apt"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    else
        echo "unsupported"
    fi
}

PKG_MANAGER="$(detect_package_manager)"

if [[ "$PKG_MANAGER" == "unsupported" ]]; then
    echo "Unsupported package manager"
    exit 1
fi

install_system_dependencies() {
    case "$PKG_MANAGER" in
        apt)
            sudo apt update
            sudo apt install -y python3 python3-venv python3-pip libnotify-bin wl-clipboard xclip
            ;;
        pacman)
            sudo pacman -Sy --noconfirm python python-pip libnotify wl-clipboard xclip
            ;;
        dnf)
            sudo dnf install -y python3 python3-pip python3-virtualenv libnotify wl-clipboard xclip
            ;;
    esac
}

create_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
    fi
}

install_python_dependencies() {
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install --upgrade -r "$PROJECT_DIR/requirements.txt"
}

install_desktop_entry() {
    local desktop_dir="$HOME/.local/share/applications"
    local desktop_file="$desktop_dir/youtube-transcript-copier.desktop"
    mkdir -p "$desktop_dir"

    # tutaj blabla
    cat > "$desktop_file" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=YouTube Transcript Copier
Comment=Pobiera transkrypcje filmu z linku w schowku
Exec=$VENV_DIR/bin/python $PROJECT_DIR/transcribe.py
Terminal=false
Categories=Utility;
Icon=$PROJECT_DIR/youtube-transcript-copier.png
StartupNotify=false
EOF

    chmod +x "$desktop_file"

    echo "Desktop entry installed to:"
    echo "$desktop_file"
}

install_system_dependencies 
create_venv 
install_python_dependencies 
install_desktop_entry

echo "Installation complete."
echo "Run the app with:"
echo "$VENV_DIR/bin/python $PROJECT_DIR/transcribe.py"
