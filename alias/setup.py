from alias import create_alias, remove_alias
from app.constants import cli_keyword

import os

remove_alias(clear_all=True, confirm = False)

root_dir = os.path.dirname(os.path.dirname(__file__))



#script_path = os.path.join(root_dir)
command = f"cd {root_dir} && python -m app.main"

create_alias(command, cli_keyword)