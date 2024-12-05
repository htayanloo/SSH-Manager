import os
import re
import json

class Parser(object):
    def __init__(self, bash_history_path='~/.bash_history', zsh_history_path='~/.zsh_history'):
        self.bash_history_path = os.path.expanduser(bash_history_path)
        self.zsh_history_path = os.path.expanduser(zsh_history_path)
        self.output_dir = os.path.expanduser('~/.autossh/')
        self.output_file = os.path.join(self.output_dir, 'ssh_connections.json')

    def _parse_ssh_command(self, line):
        """
        Parse a line for SSH command, extract details, and categorize the type of connection.
        """
        # Update the regex to handle `-p` both before and after the user@host pattern
        ssh_pattern = re.compile(
            r'^\s*ssh(?:\s+-p\s+(\d+))?\s+(?:([^@]+)@)?((?:\d{1,3}\.){3}\d{1,3}|\w[\w\.-]*)(?:\s+-p\s+(\d+))?'
        )
        match = ssh_pattern.search(line)
        if match:
            # Match groups:
            # Group 1: Port if specified before the user@host
            # Group 2: Username
            # Group 3: IP address or hostname
            # Group 4: Port if specified after the user@host
            port = match.group(1) or match.group(4) or '22'  # Default port is 22
            username = match.group(2) or 'root'  # Default username is root
            ip = match.group(3)
            connection_type = self._categorize_connection(line)
            return username, ip, port, connection_type, line  # Include raw command
        return None

    def _categorize_connection(self, line):
        """
        Determine the type of SSH connection based on the command.
        """
        if '-L' in line:
            return 'local port forwarding'
        elif '-R' in line:
            return 'remote port forwarding'
        elif '-D' in line:
            return 'dynamic port forwarding (SOCKS)'
        elif '-N' in line:
            return 'proxy (no commands executed)'
        elif 'scp ' in line:
            return 'file transfer (SCP)'
        elif 'sftp' in line:
            return 'file transfer (SFTP)'
        elif '-X' in line:
            return 'X11 forwarding'
        elif '-w' in line:
            return 'VPN over SSH'
        elif '-J' in line:
            return 'jump host (proxy jump)'
        elif '-A' in line:
            return 'agent forwarding'
        elif '-M' in line and '-S' in line:
            return 'multiplexing'
        elif 'bash' in line or 'shell' in line:
            return 'shell access'
        elif '@' in line and not any(opt in line for opt in ['-L', '-R', '-D', '-N', '-X', '-w', '-J', '-A']):
            return 'default (interactive shell)'
        else:
            return 'unknown'

    def _load_history(self, file_path, source_file, is_zsh=False):
        """
        Load and parse a history file to extract SSH commands.
        """
        result = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if is_zsh:
                        # Zsh history includes timestamp; extract the command after `;`
                        parts = line.split(';', 1)
                        if len(parts) == 2:
                            command = parts[1].strip()
                        else:
                            continue
                    else:
                        # Bash history is plain commands
                        command = line.strip()

                    parsed = self._parse_ssh_command(command)
                    if parsed:
                        username, ip, port, connection_type, raw_command = parsed
                        result.append({
                            "server_ip": ip,
                            "user": username,
                            "port": port,
                            "type": connection_type,
                            "raw_command": raw_command,
                            "shortcut": "",
                            "source_file": source_file
                        })
        except FileNotFoundError:
            print(f"History file not found: {file_path}")
        return result

    def load_from_bash(self):
        """
        Load SSH commands from bash history.
        """
        return self._load_history(self.bash_history_path, "bash_history")

    def load_from_zsh(self):
        """
        Load SSH commands from zsh history.
        """
        return self._load_history(self.zsh_history_path, "zsh_history", is_zsh=True)

    def load_all(self):
        """
        Load SSH commands from both bash and zsh history files.
        """
        bash_data = self.load_from_bash()
        zsh_data = self.load_from_zsh()

        # Combine and remove duplicates
        combined_data = {tuple(item.items()): item for item in bash_data + zsh_data}
        return list(combined_data.values())

    def load_existing_data(self):
        """
        Load existing data from the .autossh/ssh_connections.json file.
        """
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    print("Error reading existing data. Starting fresh.")
                    return []
        return []

    def merge_data(self, existing_data, new_data):
        """
        Merge new data with existing data, avoiding duplicates.
        """
        combined = {tuple(item.items()): item for item in existing_data + new_data}
        return list(combined.values())

    def save_to_file(self, data):
        """
        Save the combined SSH connections to a file in the .autossh directory.
        """
        # Ensure the directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Save as JSON
        with open(self.output_file, 'w') as file:
            json.dump(data, file, indent=4)

        # print(f"SSH connection data saved to {self.output_file}")

    def process_and_save(self):
        """
        Main method to process history, merge with existing data, and save.
        """
        # Load existing data
        existing_data = self.load_existing_data()

        # Load new data from history files
        new_data = self.load_all()

        # Merge and remove duplicates
        merged_data = self.merge_data(existing_data, new_data)

        # Save merged data to file
        self.save_to_file(merged_data)


# Usage Example
def main():
    parser = Parser()
    parser.process_and_save()

if __name__ == "__main__":
    main()
