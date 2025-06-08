import os
import pwd
import re

def get_shell_config_location():
    shell_path = pwd.getpwuid(os.getuid()).pw_shell
    home = os.path.expanduser("~")
    shell = os.path.basename(shell_path)

    known_config = {
        "bash": ".bashrc",
        "zsh": ".zshrc"
    }

    if shell in known_config:
        config_name = known_config[shell]
    else:
        print("Shell config file not known. Please give the config file of your shell (usually ~/bashrc or ~/.profile)")
        print("Just give the name of it, case sensitive. (do not include ~/.)")
        config_name = input(">> ").strip()

    return os.path.join(home, config_name)

shell_config_location = get_shell_config_location()

def create_alias(script_location, alias):
    alias_line = f"alias {alias}=\"python3 {script_location}\""

    pattern = re.compile(rf"\s*alias\s+({alias})\s*=")
    if os.path.exists(shell_config_location):
        with open(shell_config_location, "r") as f:
            for i, line in enumerate(f.readlines()):
                line = line.strip()
                if line.startswith("#"):
                    continue
                if pattern.match(line):
                    print(f"The alias {alias} already exists (line {i + 1} : {line}). Exiting.")
                    return
    else:
        print(f"The config file {shell_config_location} does not exist. Creating it now.")

    with open(shell_config_location, "a") as f:
        f.write(alias_line + "\n")

    print(f"Successfully created alias {alias} for {script_location} in {shell_config_location}")

def remove_alias(alias=None, clear_all=False, confirm=True):
    if not os.path.exists(shell_config_location):
        print(f"The config file {shell_config_location} does not exist. No aliases to remove.")
        return

    if alias is None and not clear_all:
        print(f"Please provide an alias to attempt to remove.")

    if clear_all and confirm:
        print(f"Are you sure you want to remove all aliases?")
        if input("y/n ").lower().strip() != "y":
            return

    lines_to_keep = []
    regex = r"\s*alias\s+(\w+)\s*=" if clear_all else rf"\s*alias\s+({alias})\s*="
    pattern = re.compile(regex)
    total_lines = 0

    with open(shell_config_location, "r") as f:
        lines = f.readlines()
        total_lines = len(lines)
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("#"):
                continue
            if not pattern.match(line):
                lines_to_keep.append(line + "\n")

    if len(lines_to_keep) == total_lines:
        print(f"No alias found.")
        return

    with open(shell_config_location, "w") as f:
        f.writelines(lines_to_keep)

    if clear_all:
        print(f"\nAll aliases have been successfully removed from {shell_config_location}.")
    else:
        print(f"\nAlias \"{alias}\" has been successfully removed from {shell_config_location}.")

    #print(f"Restart your terminal session or run \"source {shell_config_location}\" to see the changes.")

def alias_exists(alias) -> bool:
    pattern = re.compile(rf"\s*alias\s+({alias})\s*=")

    with open(shell_config_location, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("#"):
                continue
            if pattern.match(line):
                return True

    return False
