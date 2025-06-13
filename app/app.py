from typing import Optional
import typer

from ai_core.model import InvalidModelException
from app import chat_core
from .config_manager import ConfigManager
from .chat_manager import ChatManager
from .model_manager import ModelManager
from .constants import *
from .util import pretty_terminal_table


class App:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.chat_manager = ChatManager()
        self.model_manager = ModelManager(self.config_manager)

        self.app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]},
                          no_args_is_help=True,
                          add_completion=False)

        self.config_app = typer.Typer(no_args_is_help=True, help = "Manage configuration settings")
        self.system_prompt_app = typer.Typer(no_args_is_help=True, help="Manage system prompts for chats ")
        self.model_app = typer.Typer(no_args_is_help=True, help="Manage the settings for the current model ")

        self.app.add_typer(self.config_app, name="config")
        self.app.add_typer(self.system_prompt_app, name = "systemprompt")
        self.app.add_typer(self.model_app, name="model")

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

        # system prompt
        self.system_prompt_app.command(name="set")(self.set_system_prompt)
        self.system_prompt_app.command(name="show")(self.show_system_prompt)
        self.system_prompt_app.command(name="load")(self.load_system_prompt)

        # model settings
        self.model_app.command(name="select")(self.select_model)
        self.model_app.command(name="add")(self.add_model)
        self.model_app.command(name="remove")(self.remove_model)
        self.model_app.command(name="setapi")(self.set_api_key)
        self.model_app.command(name="list")(self.list_models)

    # -------------- main commands -------------- #

    def start(self,
              chat_name: Optional[str] = typer.Argument(None, help="Optional name of the chat history to start."),
              no_stream: bool = typer.Option(False, "--nostream", is_flag=True, help = "Disable streaming"),
              no_markdown: bool = typer.Option(False, "--nomarkdown", is_flag=True, help = "Disable markdown printing")):
        """
        Starts the chat, optionally giving the name of the chat history to start.
        """
        model = self.model_manager.get_default_model(self.config_manager)
        if model is not None:
            chat_path = self.chat_manager.select_chat(chat_name)
            chat_core.start_chat(chat_path, model, not no_stream, not no_markdown)

    def once(self,
             message: Optional[list[str]] = typer.Argument(None, help = "The message to send to the LLM"),
             chat_name: Optional[str] = typer.Option(None, "--chat", help="Specify the chat history name to export"),
             no_stream: bool = typer.Option(False, "--nostream", is_flag=True, help="Disable streaming"),
             no_markdown: bool = typer.Option(False, "--nomarkdown", is_flag=True, help="Disable markdown printing")):
        """
        Send a single chat message.
        """
        model = self.model_manager.get_default_model(self.config_manager)
        if model is None:
            return

        if message is None:
            full_message = input("Enter a chat message >> ")
        else:
            full_message = " ".join(message)

        chat_source = None
        if chat_name is not None:
            chat_source = self.chat_manager.select_chat(chat_name)

        chat_core.single_message(full_message, model, chat_source, not no_stream, not no_markdown)

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

    def config_reset_command(self, preset_config: bool = typer.Option(False, "--default", "-d", is_flag=True,
                             help = "Use an alternative config that attempts to find a .env file in the main.py location for api keys. Really only exists for debugging, feel free to ignore.")):
        """
        Resets the config file to default
        """
        self.config_manager.reset_config(preset_config)
        print(f"Config successfully reset to default in {config_path}")

    # -------------- model commands -------------- #

    def select_model(self, model_name: str = typer.Argument(help="The name of the model to use")):
        """
        Sets the given model to be the default model
        """
        if self.model_manager.is_model_in_config(model_name):
            self.config_manager.set_config_variable("default_model", model_name)
            print(f"Set default model to {model_name}")
        else:
            print(f"{model_name} is not a valid model name")
            print(f"Check models with {cli_keyword} model list, "
                  f"or add a model with {cli_keyword} model add <model_name> <model_source>")


    def add_model(self,
                  model_name: str = typer.Argument(help="The name of the model to use"),
                  model_source: str = typer.Argument(help=f"The source of the model. Type {cli_keyword} model to list all model sources")):
        """
        Add a model to the collection of models
        """
        if self.model_manager.validate_model(model_name, model_source):
            models = self.config_manager.get_config_variable("models")
            model = {"name" : model_name, "source" : model_source}
            if model not in models:
                models.append(model)
                self.config_manager.set_config_variable("models", models)
                print(f"Successfully created new model {model_name}")
            else:
                print(f"Model {model_name} from {model_source} already exists")

    def remove_model(self, model_name: str = typer.Argument(help="The name of the model to remove")):
        """
        Removes a given model from the selection.
        """
        if self.model_manager.is_model_in_config(model_name):
            default = self.config_manager.get_config_variable("default_model")
            if default == model_name:
                print(f"Failed to delete. {model_name} is the selected model.")
                print(f"Select a different model with {cli_keyword} model select <model_name> before deleting model {model_name}")
            else:
                models = self.config_manager.get_config_variable("models")
                new_models = []
                for model in models:
                    if model["name"] != model_name:
                        new_models.append(model)
                        break
                self.config_manager.set_config_variable("models", new_models)
                print(f"Removed model {model_name}")
        else:
            print(f"{model_name} is not a valid model name")
            print(f"Check models with {cli_keyword} model list, "
                  f"or add a model with {cli_keyword} model add <model_name> <model_source>")

    def set_api_key(self,
                  model_source: str = typer.Argument(help=f"The source to add the API for. Type {cli_keyword} model to list all model sources"),
                  api_key: str = typer.Argument(help="The api key to set for this source")):
        """
        Set the API key for a model source
        """
        sources = self.config_manager.get_config_variable("model_sources")
        if model_source not in sources:
            print(f"The source {model_source} is not in the list of supported model sources")
            print(f"Type '{cli_keyword} model' to find a list of supported model sources")
            return

        sources[model_source]["api_key"] = api_key
        self.config_manager.set_config_variable("model_sources", sources)

        print(f"Successfully set new api key for source {model_source}")

    def list_models(self):
        """
        List all current created model data, and model sources
        """
        models = self.config_manager.get_config_variable("models")
        model_sources = self.config_manager.get_config_variable("model_sources")
        if len(model_sources) > 0:
            print("\nSupported model sources:")
            for source in model_sources:
                print(f" - {source}")
            print()
        else:
            print(f"No model sources. (Reset your config with {cli_keyword} config reset)\n")

        if len(models) > 0:
            default_model = self.config_manager.get_config_variable("default_model")

            rows = [[model["name"], model["source"]] for model in models]
            print(f"Default model : {default_model}\n")
            pretty_terminal_table(rows, ["Model name", "Model source"])
            print()
        else:
            print("No models found.")