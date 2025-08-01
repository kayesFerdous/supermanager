# Supermanager

A powerful and simple file manager for your terminal.

Supermanager helps you manage files quickly without leaving your terminal.  
It provides a clean interface and useful features for everyday file operations.

---

## Installation

Supermanager can be installed in one line.  
It will automatically try to use **pipx** (recommended) and fall back to **pip --user** if pipx is not available.

```bash
curl -sSL https://raw.githubusercontent.com/kayesFerdous/supermanager/main/install.sh | bash
```

### How it works

1. Downloads the Supermanager source code temporarily
2. Installs using pipx or pip --user
3. Makes the `supermanager` command available in your terminal

**Tip:** If pip is used as a fallback, make sure `~/.local/bin` is in your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add this line to your shell configuration file (e.g., `~/.bashrc` or `~/.zshrc`) to make it permanent.

## Usage

After installation, run:

```bash
supermanager
```

This will start the terminal file manager.

## Uninstallation

If you installed with **pipx**:

```bash
pipx uninstall supermanager
```

If you installed with **pip --user**:

```bash
pip uninstall supermanager
```

## Features

- Clean and modern TUI (Text-based User Interface)
- Browse directories quickly
- Preview files and folders
- Easy to install and uninstall
- Works on Linux, macOS, and any system with Python 3

---

Supermanager is ready to use. Enjoy a fast and convenient file manager right in your terminal!
