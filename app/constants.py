from platformdirs import user_config_dir, user_data_dir
import os

cli_keyword = "chat" #The command alias the program uses
program_name = "ai_chat" #The directory name for the program

config_path = os.path.join(user_config_dir(program_name), "config.yaml")
data_path = user_data_dir(program_name)