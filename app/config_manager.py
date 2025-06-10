import os
import yaml

from .constants import config_path

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

    def reset_config(self) -> None:
        """
        Reset config to default values.
        Creates directory if it doesn't exist yet
        """
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            f.write("# Default config\n")
            #TODO write a default_config.yaml file that is stored in source code to config.yaml instead of hardcoded

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
            yaml.safe_dump(self.data, f, default_flow_style=False, sort_keys=False)
