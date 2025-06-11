from alias import create_alias, remove_alias
from app.constants import cli_keyword

import os

remove_alias(clear_all=True, confirm = False)

root_dir = os.path.dirname(os.path.dirname(__file__))

script_path = os.path.join(root_dir, "main.py")
command = f"python3 {script_path}"

create_alias(command, cli_keyword)