import os
import yaml

from .constants import config_path, data_path

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

def generate_default_config(do_default = False):
    #there is a design issue - no two models can have the same name, or this doesn't work
    #but im not fixing that, who cares, your fault for importing two different models with the same name lol

    if do_default:
        return {
                "model_sources" : {
                    "gemini" : { "api_key" : os.getenv("GEMINI_API_KEY") }
                },
                "models" : [
                    {
                        "name" : "gemini-2.0-flash",
                        "source" : "gemini"
                     }
                ],
                "default_model": "gemini-2.0-flash"
                }
    else:
        return {
                "model_sources": {  # API hosters (gemini, ollama, openai etc)
                    "gemini": {"api_key": None}
                },
                "models": [],  # Specific models (llama3, gemini flash 2.0, etc)
                "default_model": None  # The model to use by default
                }

class ConfigManager:
    """
    Handles the configuration file, safely reading and writing to the config file
    TODO actually use, is currently kinda useless
    """

    def __init__(self):
        self.validate_config()

        # Load data after config is known to be OK
        try:
            with open(config_path, "r") as file:
                self.data = yaml.safe_load(file)

            if self.data is None:
                self.data = {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: config file at path {config_path} not found.")

    def validate_config(self):
        """
        Ensures that the config file exists and is valid
        Automatically sets the config to the default config if invalidated
        """
        if not os.path.exists(config_path):  # Check config file exists
            self.reset_config()
            print(f"Config file not found, new config created at {config_path}")

    def reset_config(self, do_default_config = False) -> None:
        """
        Reset config to default values.
        Creates directory if it doesn't exist yet
        """
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(generate_default_config(do_default_config), f, sort_keys=False)

    def get_config_variable(self, variable_name) -> any:
        """
        Safely get the value of a variable in the config
        :param variable_name: the variable of the config to access
        :return: the value of the variable, or None if not found
        """
        if variable_name in self.data:
            return self.data[variable_name]
        return None

    def set_config_variable(self, variable, new_value) -> None:
        """
        Writes a new value to the config file, overwriting an existing one or creating a new value
        :param variable: the name of the variable to set
        :param new_value: the value to set the variable to
        """
        self.data[variable] = new_value
        with open(config_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, Dumper=yaml.Dumper)