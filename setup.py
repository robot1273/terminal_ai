from alias.alias import create_alias, remove_alias
import os

remove_alias(clear_all=True, confirm = False)

alias = "chat"
script_name = "main.py"
script_path = os.path.join(os.getcwd(), script_name)

create_alias(script_path, alias)