import os
import json
import subprocess
import argparse
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt

from .parser import Parser


class SSHDataViewer(Parser):
    def __init__(self, data_file='~/.autossh/ssh_connections.json'):
        super().__init__()
        self.process_and_save()
        self.data_file = os.path.expanduser(data_file)
        self.console = Console()
        self.data = self.load_data()
        self.filtered_data = None  # Store search results

    def load_data(self):
        """
        Load SSH connection data from the JSON file.
        """
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    self.console.print("[red]Error: JSON file is corrupted.[/red]")
                    return []
        else:
            self.console.print(f"[yellow]No data found at {self.data_file}. Run the parser first.[/yellow]")
            return []

    def save_data(self):
        """
        Save the SSH connection data back to the JSON file.
        """
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file, indent=4)
        self.console.print("[green]Data saved successfully![/green]")

    def display_table(self, data):
        """
        Display the SSH connection data as a table with row numbers.
        """
        if not data:
            self.console.print("[yellow]No SSH connection data to display.[/yellow]")
            return

        # Create a table
        table = Table(title="SSH Connection Data")

        # Add columns
        table.add_column("#", justify="center", style="bold", no_wrap=True)  # Row number
        table.add_column("Server IP", justify="center", style="cyan", no_wrap=True)
        table.add_column("User", justify="center", style="green")
        table.add_column("Port", justify="center", style="magenta")
        table.add_column("Type", justify="center", style="yellow")
        table.add_column("Raw Command", justify="left", style="white")
        table.add_column("Shortcut", justify="left", style="white")
        table.add_column("Source File", justify="center", style="blue")

        # Add rows from data
        for idx, entry in enumerate(data, start=1):
            table.add_row(
                str(idx),
                entry.get("server_ip", "N/A"),
                entry.get("user", "N/A"),
                entry.get("port", "N/A"),
                entry.get("type", "N/A"),
                entry.get("raw_command", "N/A"),
                entry.get("shortcut", "N/A"),
                entry.get("source_file", "N/A")
            )

        # Render the table
        self.console.print(table)

    def filter_data(self, query):
        """
        Filter the data based on a search query.
        """
        query = query.lower()
        return [
            entry
            for entry in self.data
            if query in entry.get("server_ip", "").lower()
            or query in entry.get("user", "").lower()
            or query in entry.get("port", "").lower()
            or query in entry.get("type", "").lower()
            or query in entry.get("raw_command", "").lower()
            or query in entry.get("shortcut", "").lower()
            or query in entry.get("source_file", "").lower()
        ]

    def set_shortcut(self, index):
        """
        Set a shortcut for a specific connection and create an alias in Bash and Zsh.
        """
        entry = self.data[index]
        current_shortcut = entry.get("shortcut", "N/A")
        self.console.print(f"[yellow]Current Shortcut:[/yellow] {current_shortcut}")
        new_shortcut = Prompt.ask("[green]Enter new shortcut[/green]").strip()

        # Ensure no duplicate shortcuts
        if any(item.get("shortcut") == new_shortcut for item in self.data):
            self.console.print("[red]Shortcut already exists. Please choose a different one.[/red]")
            return

        # Update the shortcut in the connection data
        entry["shortcut"] = new_shortcut
        self.save_data()

        # Add or replace the alias in Bash and Zsh
        raw_command = entry.get("raw_command")
        if raw_command:
            self.add_alias_to_shell(new_shortcut, raw_command)
            self.console.print(f"[green]Shortcut '{new_shortcut}' set successfully![/green]")

    def add_alias_to_shell(self, shortcut, command):
        """
        Add or replace an alias in Bash and Zsh configurations.
        """
        bashrc_path = os.path.expanduser("~/.bashrc")
        zshrc_path = os.path.expanduser("~/.zshrc")
        alias_line = f"alias {shortcut}='{command}'"

        # Update Bash configuration
        self.update_alias_in_file(bashrc_path, shortcut, alias_line)

        # Update Zsh configuration
        self.update_alias_in_file(zshrc_path, shortcut, alias_line)

        # Reload shell configurations
        subprocess.run(f"source {bashrc_path}", shell=True, check=False)
        subprocess.run(f"source {zshrc_path}", shell=True, check=False)

    def update_alias_in_file(self, file_path, shortcut, alias_line):
        """
        Add or replace an alias in a specific shell configuration file.
        """
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write(f"{alias_line}\n")
            return

        updated = False
        with open(file_path, "r") as file:
            lines = file.readlines()

        with open(file_path, "w") as file:
            for line in lines:
                # Replace the existing alias
                if line.startswith(f"alias {shortcut}="):
                    file.write(f"{alias_line}\n")
                    updated = True
                else:
                    file.write(line)

            # Add the new alias if it doesn't already exist
            if not updated:
                file.write(f"{alias_line}\n")


    def open_in_current_shell(self, raw_command):
        """
        Execute the SSH command in the current shell.
        """
        self.console.print(f"[green]Connecting with command:[/green] {raw_command}")
        try:
            subprocess.run(raw_command, shell=True)
        except KeyboardInterrupt:
            self.console.print("[yellow]Connection closed by user.[/yellow]")

    def connect_by_shortcut(self, shortcut):
        """
        Connect to a session using its shortcut.
        """
        entry = next((item for item in self.data if item.get("shortcut") == shortcut), None)
        if not entry:
            self.console.print("[red]Shortcut not found. Please try again.[/red]")
            return

        raw_command = entry.get("raw_command")
        if raw_command:
            self.open_in_current_shell(raw_command)
        else:
            self.console.print("[red]Invalid SSH command.[/red]")

    def interactive_mode(self):
        """
        Main interactive loop.
        """
        current_data = self.data  # Show all data initially
        while True:
            self.console.print("\n")
            self.display_table(current_data)

            # Prompt for user input
            action = Prompt.ask(
                "\n[bold green]Options:[/bold green] [yellow]Search (s), Select (number), Shortcut (sc), Back (b), Quit (q)[/yellow]",
                choices=["s", "b", "q", "sc"] + ['1','2','....'],
                default="s"
            )

            # Handle Quit
            if action == "q":
                self.console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            # Handle Back
            elif action == "b":
                current_data = self.data  # Reset to full data list

            # Handle Search
            elif action == "s":
                query = Prompt.ask("[bold green]Enter your search query[/bold green]")
                filtered_data = self.filter_data(query)
                if not filtered_data:
                    self.console.print("[red]No matching results found.[/red]")
                else:
                    current_data = filtered_data  # Show only filtered results

            # Handle Shortcut
            elif action == "sc":
                shortcut = Prompt.ask("[bold green]Enter shortcut to connect[/bold green]").strip()
                self.connect_by_shortcut(shortcut)

            # Handle Selection
            elif action.isdigit():
                index = int(action) - 1
                if 0 <= index < len(current_data):
                    selected_entry = current_data[index]
                    sub_action = Prompt.ask(
                        "\n[bold green]Options for Selected Item:[/bold green] [yellow]Connect (c), Set Shortcut (ss), Back (b)[/yellow]",
                        choices=["c", "ss", "b"],
                        default="b"
                    )

                    if sub_action == "c":
                        raw_command = selected_entry.get("raw_command")
                        if raw_command:
                            self.open_in_current_shell(raw_command)
                        else:
                            self.console.print("[red]Invalid SSH command.[/red]")

                    elif sub_action == "ss":
                        self.set_shortcut(index)

                else:
                    self.console.print("[red]Invalid selection. Try again.[/red]")


def main():

    parser = argparse.ArgumentParser(description="Manage and connect to SSH sessions interactively or by shortcut.")
    parser.add_argument("--shortcut", "-sc", help="Connect to an SSH session using a shortcut.")
    args = parser.parse_args()

    viewer = SSHDataViewer()

    if args.shortcut:
        # Command-line mode: Connect by shortcut
        viewer.connect_by_shortcut(args.shortcut)
    else:
        # Interactive mode
        viewer.interactive_mode()


if __name__ == "__main__":
    main()
