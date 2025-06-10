from typing import Optional
import typer

from app import chat_core
from .config_manager import ConfigManager
from .chat_manager import ChatManager

from .constants import *


class App:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.chat_manager = ChatManager()

        self.app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]},
                          no_args_is_help=True,
                          add_completion=False)

        self.config_app = typer.Typer(no_args_is_help=True, help = "Manage configuration settings")
        self.app.add_typer(self.config_app, name="config")

        self._register_commands()

    def _register_commands(self):
        # main
        self.app.command(name="start")(self.start)
        self.app.command(name="once")(self.once)
        self.app.command(name="list")(self.list_chats)

        # config
        self.config_app.command(name="find")(self.config_find_command)
        self.config_app.command(name="reset")(self.config_reset_command)

    # -------------- main commands -------------- #

    def start(self, chat_name: Optional[str] = typer.Argument(None, help="Optional name of the chat history to start.")):
        """
        Starts the chat, optionally giving the name of the chat history to start.
        """
        chat_core.start_chat(self.chat_manager.select_chat(chat_name))

    def once(self, message: list[str]):
        """
        Send a single chat message.
        TODO
        """
        full_message = " ".join(message)
        print(f"Sending one-time message: {full_message}")

    def list_chats(self):
        """
        List all existing chats.
        """
        self.chat_manager.list_chats()


    # -------------- config commands -------------- #

    def config_find_command(self):
        """
        Displays the location of the config file and the chat data
        """
        print(f"Config is in {config_path}")
        print(f"Chat data is in {data_path}")

    def config_reset_command(self):
        """
        Resets the config file to default
        """
        self.config_manager.reset_config()
        print(f"Config successfully reset to default in {config_path}")


if __name__ == "__main__":
    app = App()
    app.app()