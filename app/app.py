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
        self.system_prompt_app = typer.Typer(no_args_is_help=True, help="Manage system prompts for chats ")

        self.app.add_typer(self.config_app, name="config")
        self.app.add_typer(self.system_prompt_app, name = "systemprompt")

        self._register_commands()

    def _register_commands(self):
        # main
        self.app.command(name="start")(self.start)
        self.app.command(name="once")(self.once)
        self.app.command(name="list")(self.list_chats)
        self.app.command(name="delete")(self.delete_chat)

        # config
        self.config_app.command(name="find")(self.config_find_command)
        self.config_app.command(name="reset")(self.config_reset_command)

        #system prompt
        self.system_prompt_app.command(name="set")(self.set_system_prompt)
        self.system_prompt_app.command(name="show")(self.show_system_prompt)
        self.system_prompt_app.command(name="load")(self.load_system_prompt)

    # -------------- main commands -------------- #

    def start(self,
              chat_name: Optional[str] = typer.Argument(None, help="Optional name of the chat history to start."),
              stream: bool = typer.Option(True, "--nostream", is_flag=True, help = "Disable streaming"),
              markdown: bool = typer.Option(True, "--nomarkdown", is_flag=True, help = "Disable markdown printing")):
        """
        Starts the chat, optionally giving the name of the chat history to start.
        """
        chat_core.start_chat(self.chat_manager.select_chat(chat_name), do_stream = stream, do_markdown=markdown)

    def once(self,
             message: Optional[list[str]] = typer.Argument(None, help = "The message to send to the LLM"),
             chat_name: Optional[str] = typer.Option(None, "--chat", help="Specify the chat history name to export"),
             stream: bool = typer.Option(True, "--nostream", is_flag=True, help="Disable streaming"),
             markdown: bool = typer.Option(True, "--nomarkdown", is_flag=True, help="Disable markdown printing")):
        """
        Send a single chat message.
        """
        if message is None:
            full_message = input("Enter a chat message >> ")
        else:
            full_message = " ".join(message)

        chat_source = None
        if chat_name is not None:
            chat_source = self.chat_manager.select_chat(chat_name)

        chat_core.single_message(full_message, chat_source, stream, markdown)

    def list_chats(self):
        """
        List all existing chats.
        """
        self.chat_manager.list_chats()

    def delete_chat(self, chat_name: str = typer.Argument(help="The name of the chat to delete"),):
        """
        Deletes a given chat
        """
        self.chat_manager.delete_chat(chat_name)

    # -------------- system prompt commands -------------- #

    def set_system_prompt(self,
                          system_prompt: list[str] = typer.Argument(help="The system prompt to set"),
                          chat_name: Optional[str] = typer.Option(None, "--chat", help="Specify the chat history name to load the system prompt.")):
        """
        Sets the system prompt for the given chat history.
        """
        if chat_name is None:
            print(f"Error: The --chat option is required to specify which chat history to modify.")
            raise typer.Exit(code=1)

        # Join the list of strings into a single system prompt string
        full_system_prompt = " ".join(system_prompt)
        self.chat_manager.set_system_prompt(chat_name, full_system_prompt)

    def show_system_prompt(self, chat_name: str = typer.Argument(help="Specify the chat history name to display the system prompt of.")):
        """
        Displays the system prompt for a given chat
        """
        chat_data = self.chat_manager.get_chat_data(chat_name)
        if chat_data is not None:
            print(f"System prompt for chat '{chat_name}':\n\"{chat_data["system_prompt"].strip()}\"")

    def load_system_prompt(self,
                          path: str = typer.Argument(help="Filepath for the system prompt to load"),
                          chat_name: Optional[str] = typer.Option(None, "--chat", help="Specify the chat history name to load the system prompt.")):
        """
        Sets the system prompt for the given chat history.
        """
        if chat_name is None:
            print(f"Error: The --chat option is required to specify which chat history to modify.")
            raise typer.Exit(code=1)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()

        except FileNotFoundError:
            print(f"Error: The file '{path}' was not found.")
        except Exception as e:
            print(f"An error occurred reading the data: {e}")

        self.chat_manager.set_system_prompt(chat_name, system_prompt)

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

