# SSH Shortcut Manager

**SSH Shortcut Manager** is a Python-based tool to manage and connect to SSH sessions using shortcuts. It supports both interactive and command-line modes, allowing you to assign shortcuts to SSH commands and use them directly in your terminal. The tool automatically adds these shortcuts as aliases in your shell (`~/.bashrc` and `~/.zshrc`), making them available across sessions.

## Features

- **Interactive Mode**:
  - Search and filter SSH connections.
  - Assign or edit shortcuts for SSH sessions.
  - Directly connect to SSH sessions from the interactive UI.

- **Command-Line Mode**:
  - Use shortcuts directly from the terminal (e.g., `sshmgm --shortcut tp-1`).

- **Shell Alias Management**:
  - Automatically creates or updates aliases in `~/.bashrc` and `~/.zshrc`.
  - Ensures the aliases persist across sessions.

- **Dynamic Management**:
  - Prevents duplicate shortcuts.
  - Replaces existing shortcuts in shell configurations.

## Installation

### Prerequisites

- Python 3.7 or higher
- Pip (Python package manager)
- Bash or Zsh shell

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/htayanloo/SSH-Manager.git
   cd SSH-Manager
   ```

2. Install the package:
   ```bash
   pip install .
   ```

3. Verify the installation:
   ```bash
   sshmgm --help
   ```

## Usage

### Interactive Mode

Run the tool interactively:
```bash
sshmgm
```

#### Features in Interactive Mode
- **Search (s)**: Search for SSH connections by keywords.
- **Select (number)**: Select an SSH connection to connect or edit its shortcut.
- **Shortcut (sc)**: Directly connect using a shortcut.
- **Back (b)**: Return to the full list.
- **Quit (q)**: Exit the tool.

#### Shortcut Options
- **Connect (c)**: Start an SSH session for the selected item.
- **Set Shortcut (ss)**: Assign or update a shortcut for the selected session.

### Command-Line Mode

Run the tool with a shortcut directly from the terminal:
```bash
sshmgm --shortcut <shortcut>
```

Example:
```bash
sshmgm --shortcut tp-1
```

### Shell Alias Management

When you assign a shortcut, the tool automatically creates or updates an alias in your shell configuration files (`~/.bashrc` and `~/.zshrc`).

- Example alias added to `~/.bashrc` and `~/.zshrc`:
  ```bash
  alias tp-1='ssh user@192.168.1.1'
  ```

- Run the alias directly in the terminal:
  ```bash
  tp-1
  ```

The tool ensures existing aliases are replaced and configurations are reloaded, making the shortcuts available immediately.

## Configuration Files

### Session Data
SSH session data is stored in `~/.autossh/ssh_connections.json`. This file is managed automatically by the tool.

Example structure:
```json
[
    {
        "server_ip": "192.168.1.1",
        "user": "root",
        "port": "22",
        "type": "default",
        "raw_command": "ssh root@192.168.1.1",
        "shortcut": "tp-1",
        "source_file": "bash_history"
    },
    {
        "server_ip": "192.168.1.2",
        "user": "admin",
        "port": "22",
        "type": "proxy",
        "raw_command": "ssh admin@192.168.1.2",
        "shortcut": "srv2",
        "source_file": "zsh_history"
    }
]
```

### Shell Configuration
The tool updates your shell configuration files (`~/.bashrc` and `~/.zshrc`) to include aliases for each shortcut.

## Examples

### Setting a Shortcut
1. Assign `tp-1` to `ssh root@192.168.1.1` in interactive mode.
2. Run the alias:
   ```bash
   tp-1
   ```

### Connecting with a Shortcut
1. Use the command-line mode to connect:
   ```bash
   sshmgm --shortcut tp-1
   ```

### Replacing a Shortcut
1. Update the shortcut in interactive mode.
2. The alias in `~/.bashrc` and `~/.zshrc` is automatically replaced.

## Development

### Run Locally
To test and run the project locally:
```bash
python -m autossh.ssh_manager
```

### Add a New Feature
1. Fork and clone the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/new-feature
   ```
3. Make your changes and submit a pull request.

## Requirements

- Python 3.7+
- Bash or Zsh shell
- Dependencies (installed via `pip`):
  - `rich`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Developed by Hadi Tayanloo. Contributions are welcome! 😊
# SSH-Manager
