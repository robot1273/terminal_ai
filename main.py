from typing import Optional

import typer
import yaml
import os

from platformdirs import user_config_dir, user_data_dir
from pathlib import Path

import chat

cli_keyword = "chat" #The command alias the program uses
program_name = "ai_chat" #The directory name for the program

config_path = os.path.join(user_config_dir(program_name), "config.yaml")
data_path = user_data_dir(program_name)

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]},
                  no_args_is_help=True,
                  add_completion=False)

config_app = typer.Typer(no_args_is_help=True, help = "Manage configuration settings")

app.add_typer(config_app, name="config")

def reset_config():
    """Reset config to default values. Ensure config path exists first!"""
    with open(config_path, "w") as f:
        f.write("# Default config\n")
        f.write("current_chat: null\n")

def get_config_data():
    try:
        with open(config_path, "r") as file:
            data = yaml.safe_load(file)

        if data is None:
            return {}
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: config file at path {config_path} not found.")

def get_config_variable(variable_name):
    """Safely get the value of a variable in the config"""
    data = get_config_data()
    if variable_name in data:
        return data[variable_name]
    return None

def get_chat_paths():
    return list(Path(data_path).glob("*.yaml"))

def validate_data():
    """Ensures config and data files are valid"""
    if not os.path.exists(config_path): #Check config file exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        reset_config()
        print(f"Config file not found, new config created at {config_path}")

    current_chat_location = get_config_variable("current_chat")
    if current_chat_location is not None:
        if not os.path.exists(current_chat_location): #Check current chat location is valid
            print(f"Current chat location {current_chat_location} cannot be found. Resetting to null")
            modify_config("current_chat", None)

    if not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)
        print(f"Chat data directory not found, new directory created at {data_path}")

def modify_config(variable, new_value):
    data = get_config_data()
    data[variable] = new_value
    with open(config_path, 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

@config_app.command("find")
def config_find_command():
    """
    Displays the location of the config file and the chat data
    """
    print(f"Config is in {config_path}")
    print(f"Chat data is in {data_path}")

@config_app.command("reset")
def config_reset_command():
    """
    Resets the config file to default
    """
    reset_config()
    print(f"Config successfully reset to default in {config_path}")

@app.command()
def start(chat_name: Optional[str] = typer.Argument(None, help="Optional name of the chat history to start.")):
    """
    Starts the chat, optionally giving the name of the chat history to start.
    """
    if chat_name is None and get_config_variable("current_chat") is None: #No name given, no current
        chat_paths = get_chat_paths()
        if len(chat_paths) == 0:
            print("No existing chats found, creating a new chat 'chat' ")
            chat_path = os.path.join(data_path, "chat.yaml")
        else:
            print("Selecting most recent chat")
            chat_path = max(chat_paths, key=lambda f: f.stat().st_mtime)
    elif chat_name is None: #No name given, but there is a current chat
        chat_path = get_config_variable("current_chat")
    else: #Name of chat has been given
        chat_path = os.path.join(data_path, chat_name+".yaml")

    modify_config("current_chat", str(chat_path)) #Update current_chat to the newly selected chat

    Path(chat_path).touch(exist_ok=True) #Create an empty yaml chat file

    #Now we start up a new chat instance in the chat file
    chat.start_chat(chat_path)

@app.command()
def once(message: list[str]):
    """
    Send a single chat message.
    """
    full_message = " ".join(message)
    print(f"Sending one-time message: {full_message}")

@app.command("list")
def list_chats():
    """
    List all existing chats.
    """
    chat_paths = get_chat_paths()
    if len(chat_paths) == 0:
        print(f"No chats found. Start a new chat with '{cli_keyword} start <chat_name>'")
        return

    print("Existing chats:")
    for chat_path in chat_paths:
        chat_name = chat_path.name.removesuffix(".yaml")
        print(f" - {chat_name}")


if __name__ == "__main__":
    validate_data()
    app()