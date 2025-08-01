#!/bin/bash
set -e

echo "==============================================================="
echo "               Supermanager Installer"
echo "==============================================================="
echo "This script will install Supermanager on your system."
echo "It will:"
echo "  1. Download the Supermanager source code temporarily"
echo "  2. Install it using pipx (recommended) or pip --user (fallback)"
echo "  3. Make the 'supermanager' command available in your terminal"
echo "==============================================================="
echo ""

# Create a temporary folder for installation
TMP_DIR=$(mktemp -d)

cleanup() {
    echo "Cleaning up temporary files..."
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "Step 1: Downloading Supermanager..."
git clone --depth 1 https://github.com/kayesFerdous/supermanager.git "$TMP_DIR"
cd "$TMP_DIR"

echo "Step 2: Checking installation method..."
if command -v pipx &>/dev/null; then
    echo "Found pipx. Installing Supermanager with pipx..."
    pipx install .
    echo "---------------------------------------------------------------"
    echo "Installation complete!"
    echo "You can now run 'supermanager' from any terminal."
    echo "---------------------------------------------------------------"
else
    echo "pipx not found. Using pip --user as fallback..."
    echo "Note: Make sure ~/.local/bin is in your PATH to run Supermanager."
    echo ""

    if pip install --user .; then
        LOCAL_BIN_PATH="$HOME/.local/bin"
        if [[ ":$PATH:" != *":$LOCAL_BIN_PATH:"* ]]; then
            echo "---------------------------------------------------------------"
            echo "Supermanager is installed, but your PATH does not include:"
            echo "  $LOCAL_BIN_PATH"
            echo ""
            echo "Add this line to your ~/.bashrc or ~/.zshrc to fix it:"
            echo ""
            echo "export PATH=\"$LOCAL_BIN_PATH:\$PATH\""
            echo ""
            echo "Then restart your terminal or run:"
            echo "source ~/.bashrc  (or your shell config)"
            echo "---------------------------------------------------------------"
        else
            echo "---------------------------------------------------------------"
            echo "Installation complete!"
            echo "You can now run 'supermanager' from any terminal."
            echo "---------------------------------------------------------------"
        fi
    else
        echo "---------------------------------------------------------------"
        echo "Installation failed using pip --user."
        echo ""
        echo "We recommend installing pipx and trying again:"
        echo "  - Arch:    sudo pacman -S python-pipx"
        echo "  - Debian:  sudo apt install pipx"
        echo "  - Fedora:  sudo dnf install pipx"
        echo "---------------------------------------------------------------"
        exit 1
    fi
fi

echo ""
echo "All done! Thank you for installing Supermanager."
