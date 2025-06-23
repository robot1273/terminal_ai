import datetime
import os
from pathlib import Path

import yaml

from app.constants import data_path, cli_keyword
from app.util import pretty_terminal_table


class ChatManager:
    """
    Manages finding, loading and saving chat data
    """
    def __init__(self):
        self.validate_chats()

    def validate_chats(self) -> None:
        """
        Ensures that the stored data exists and the chats are valid
        Creates a new data directory if it doesn't already exist
        """
        if not os.path.exists(data_path):
            os.makedirs(data_path, exist_ok=True)
            print(f"Chat data directory not found, new directory created at {data_path}")

    def get_chat_paths(self):
        """
        :return: a list of all chat .yaml files in the data directory
        """
        return list(Path(data_path).glob("*.yaml"))

    def get_chat_path(self, chat_name: str):
        """
        Get the chat path for a specific chat
        :param chat_name: the name of the chat get the filepath for
        :return: The path for the chat if it exists, None otherwise
        """
        chat_path = os.path.join(data_path, chat_name + ".yaml")
        if not os.path.exists(chat_path):
            return None
        return chat_path

    def get_most_recent_chat(self):
        """
        :returns The most recent chat path
        :throws ValueError if no chat exists (max([]))
        """
        return max(self.get_chat_paths(), key=lambda f: f.stat().st_mtime)

    def select_chat(self, chat_name : str = None):
        """
        Given a chat name, attempts to find the chat with the given name and returns the path
        If chat name is not an existing chat, creates a new chat with the given name
        If no chat name given, selects the most recently accessed chat
        If no chats found, automatically creates a new empty chat
        :param chat_name: the name of the chat to access
        :return: The path of the chat to access
        """
        if chat_name is None: #No name given
            if len(self.get_chat_paths()) == 0:
                print("No existing chats found, creating a new chat 'chat' ")
                chat_path = os.path.join(data_path, "chat.yaml")

            else:
                print("Selecting most recent chat")
                return self.get_most_recent_chat()
        else: #Name has been given
            chat_path = os.path.join(data_path, chat_name + ".yaml")

        Path(chat_path).touch(exist_ok=True)  # Create an empty yaml chat file

        return chat_path

    def get_chat_data(self, chat_name):
        """
        Gets the yaml data as a dict from a chat
        :param chat_name: the chat name to get the data for
        :return: a dictionary containing the deserialized yaml file, or None if no chat found
        """
        chat_path = self.get_chat_path(chat_name)

        if chat_path is None:
            print(f"No chat with name {chat_name} found. "
                  f"\nCreate the chat first with chat start {chat_name}, or type chat list to list available chats")
            return None

        with open(chat_path, "r") as file:
            data = yaml.safe_load(file)

        return data

    def set_system_prompt(self, chat_name : str, system_prompt : str):
        """
        Sets the system prompt for a chat
        If the chat cannot be found, informs the user
        :param chat_name: the name of the chat to set the prompt for
        :param system_prompt: the system prompt
        """
        chat_path = self.get_chat_path(chat_name)
        data = self.get_chat_data(chat_name)
        if data is None:
            return

        data["system_prompt"] = system_prompt

        with open(chat_path, "w") as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)

        print(f"Successfully updated chat '{chat_name}' with new system prompt ")

    def delete_chat(self, chat_name : str):
        """
        Deletes a chat after user confirmation
        :param chat_name: the name of the chat to delete
        """
        chat_path = self.get_chat_path(chat_name)
        if chat_path is None:
            print(f"No chat with name {chat_name} found.")
            return

        option = input(f"Are you sure you want to delete the chat {chat_name}? "f"\ny/n >> ")
        if option.strip() == "y":
            os.remove(chat_path)
            print(f"Successfully removed chat in {chat_path}")


    def list_chats(self):
        """
        Display all chats and some metadata about them
        """
        chat_paths = self.get_chat_paths()
        if len(chat_paths) == 0:
            print(f"No chats found. Start a new chat with '{cli_keyword} start <chat_name>'")
            return

        #setup table for pretty print
        column_names = ["Chat name", "Last used", "Model"]
        rows = []
        for chat_path in chat_paths:
            with open(chat_path, "r") as file:
                data = yaml.safe_load(file)

            chat_name = chat_path.name.removesuffix(".yaml")
            last_used = chat_path.stat().st_mtime
            last_used_datetime = datetime.datetime.fromtimestamp(last_used).strftime("%d/%m/%Y %H:%M")
            model = data["model"]

            rows.append([chat_name, last_used_datetime, model])

        pretty_terminal_table(rows, column_names, padding = 5)