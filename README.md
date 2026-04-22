# ConfigManager

A terminal-based config file manager built with `Textual`.

It lets you register config files by name, open and edit them, and save changes safely.

## Features

- Browse saved config entries in a list
- Open selected config content in the built-in editor
- Save changes
- Add new config entries using a modal form
- Remove config entries using delete mode
- Open a config in an external terminal editor (`nano`)

## Tech Stack

- Python 3.10+
- `textual`
- Standard library modules: `json`, `os`, `subprocess`, `shlex`, `shutil`

## Project Structure

- `main.py` - main TUI app and screens
- `configs.json` - saved config name/path mappings (created at runtime)

## Installation

```bash
git clone https://github.com/KilianDiescher/ConfigManager.git
cd ConfigManager
pipx install .
```

## Run

```bash
config-manager
```

## Keybindings

- `Enter` - Select current config
- `Ctrl+A` - Add new config
- `Ctrl+D` - Toggle delete mode
- `Ctrl+O` - Save current config
- `Ctrl+E` - Open current config in external terminal editor

## How It Works

1. On startup, the app loads mappings from `configs.json` in the project directory.
2. Selecting a config loads its file content into the editor pane.
3. Saving writes editor content back to the selected file after confirmation.
4. Any list change is persisted atomically via temp file replacement.

## Notes

- External editor support checks for one of: `kitty`, `foot`, `alacritty`, `wezterm`, `konsole`.
- If no supported terminal is found, opening external editor will fail with a runtime error/notification.
- Ensure file paths in entries are valid on the target machine.



