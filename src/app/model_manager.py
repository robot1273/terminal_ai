from typing import Type

from ai_core.model import Model, LocalModel, InvalidModelException, InvalidAPIKeyException

from app.constants import MODEL_SOURCES, cli_keyword


class ModelManager:
    def __init__(self, config_manager):
        self.model_source_data = config_manager.get_config_variable("model_sources")
        self.saved_models = config_manager.get_config_variable("models")
        self.default_model_name = config_manager.get_config_variable("default_model")

        if self.model_source_data is None or len(self.model_source_data) == 0:
            print("Warning - No model sources found in config. Ensure config file is valid.")
            return


        # Validate all existing saved models
        models = config_manager.get_config_variable("models")
        for model in models:
            result = self.validate_model(model["name"], model["source"], display_errors = False)
            if not result:
                print(f"Warning - an error occurred validating a saved model. ({model})\n"
                      f"Check the config files are up to date and valid, and ensure API keys are valid")
                break

    def validate_model(self, model_name : str, model_source : str, display_errors = True) -> bool:
        """
        Validates a model from a source to see if it exists or not
        :param model_name: the name of the model
        :param model_source: the source of the model
        :param display_errors: whether to display error messages or not
        :return: True if the model exists, False otherwise
        """
        model_source = model_source.strip() #Validate model source
        if model_source not in self.model_source_data:
            if display_errors:
                print(f"{model_source} is not a currently supported model source. Supported sources:")
                for source in self.model_source_data:
                    print(f" - {source}")
            return False

        #Attempt to create model
        model = self.get_model(model_name, model_source, display_errors = display_errors)

        return model is not None

    def is_model_in_config(self, model_name):
        return any(model["name"] == model_name for model in self.saved_models)

    def get_model(self, model_name : str, model_source : str, display_errors = True) -> None | Model | LocalModel:
        """
        Returns a Model class, given name and model source.
        Used for checking if a given model from a source actually can exist
        Used in model add <name> <source>
        :param model_name: the name of the model.
        :param model_source: the api source of the model (e.g. gemini, ollama, etc)
        :param display_errors: whether to display error messages or not
        :return: The Model class corresponding to the saved model name/source, or None on error
        """

        model: Type[Model] = MODEL_SOURCES[model_source]

        try:
            if issubclass(model, LocalModel):
                return model(model_name)
            else:
                api_key = self.model_source_data[model_source]["api_key"]
                return model(model_name, api_key)
        except InvalidAPIKeyException:
            if display_errors:
                print(f"The API key for source {model_source} is invalid.")
                print(f"Set a valid API key for {model_source} with {cli_keyword} model setapi <model_source> <api_key>")
            return None
        except InvalidModelException as e:
            if display_errors:
                print(f"An error occurred validating this model: {e}")
            return None

    def get_model_from_config(self, model_name : str) -> Model | None:
        """
        Returns a Model class, given only the name, from the saved model data
        :param model_name: the name of the model.
        :return: The Model class corresponding to the saved model name/source.
        """
        model_source = None
        for saved_model in self.saved_models:
            if saved_model["name"] == model_name:
                model_source = saved_model["source"]

        if model_source not in MODEL_SOURCES:
            print(f"Model {model_name} has an invalid source ({model_source}). Ensure config is valid")
            return None

        return self.get_model(model_name, model_source)

    def select_new_default_model(self, config_manager):
        """
        Fallback method to select the first model from the saved models
        :return: the name of the model to select, or None if no models can be selected
        """
        if len(self.saved_models) == 0:
            return None
        else:
            self.default_model_name = self.saved_models[0]["name"]
            config_manager.set_config_variable("default_model", self.default_model_name)
            print(f"Auto-selected new default model to {self.default_model_name}")
            return self.default_model_name

    def get_default_model(self, config_manager) -> Model | None:
        if self.default_model_name is None:
            self.default_model_name = self.select_new_default_model(config_manager)

        if self.default_model_name is None: #If  still none after selecting new default, this means no models exist
            print(f"Error! No models exist yet! Create a new model with {cli_keyword} model add <model_name> <model_source>")
            return None

        return self.get_model_from_config(self.default_model_name)

