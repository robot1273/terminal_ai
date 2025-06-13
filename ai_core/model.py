import json
import requests

from typing import Iterator
from .util import connected_to_internet

class ModelError(Exception):
    """Base exception class for errors related to model output"""
    pass

class InvalidModelException(Exception):
    """Exception raised when an invalid model is requested"""
    pass

class NoInternetException(InvalidModelException):
    """Exception raised when an attempting to request a model with no internet connection"""
    pass

class InvalidAPIKeyException(InvalidModelException):
    """Exception raised when an invalid api key is given"""
    pass

class ModelParameters:
    """
    A class to store and manage parameters
    """
    def __init__(
        self,
        temperature: float,
        top_k: int,
        top_p: float,
        num_predict : int
    ):
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.num_predict = num_predict

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the parameters
        """
        return {}

class GeminiModelParameters(ModelParameters):
    """
    A class to store and manage parameters for Ollama model generation.
    """
    def __init__(
        self,
        temperature: float = 0.8,
        top_k: int = 40,
        top_p: float = 0.9,
        num_predict: int = 128
    ):
        """
        Initialize the parameters. Default is the ollama defaults
        :param temperature: Controls randomness. Higher is more creative, lower is more deterministic.  Default: 0.8.
        :param num_predict: Maximum number of tokens to generate.
                     Default: 128. Use -1 for infinite, -2 to fill context.
        :param top_k: Samples from the k most likely next tokens.   Default: 40.
        :param top_p: Samples from the smallest set of tokens whose cumulative probability exceeds p.   Default: 0.9.
        """
        super().__init__(temperature, top_k, top_p, num_predict)

    def to_dict(self) -> dict:
        """
        Returns the parameters as a JSON dictionary for generationConfig for gemini
        Specific to requests/curl api system
        """
        return {
            "temperature": self.temperature,
            "topP": self.top_p,
            "topK": self.top_k,
            "maxOutputTokens": self.num_predict
        }

class Model:
    """
    Generic model to host LLM
    """
    def __init__(self, model_name: str, api_key : str, debug: bool = False, parameters: ModelParameters = None):
        """
        :param model_name: The name of the model to use.
        :param api_key : The api key to use for this model
        :param debug: Display debug messages or not. Defaults to False
        :param parameters: The model parameters to use
        :raises InvalidModelException: Raised when an error occurs retrieving model
        """
        self.model_name = model_name
        self.api_key = api_key
        self.debug = debug
        self.parameters = parameters

    def raise_model_exists(self):
        """
        Checks if model name exists from API
        Also checks if no internet connection found
        :raises InvalidModelException: Raised when an invalid model name is given.
        :raises NoInternetException: Raised when no internet connection is found while attempting to retrieve model
        :raises InvalidAPIKeyException: Raised when an invalid API key is given.
        """
        pass

    def invoke(self, prompt : str = None) -> str:
        """
        Invoke the LLM with the given prompt
        :param prompt: The prompt to invoke
        :return: The output message
        :raises ModelError: when an error occurs
        """
        pass

class LocalModel(Model):
    """Model specifically for local models (mainly, and probably exclusively, ollama)"""
    def __init__(self, model_name: str, debug: bool = False, parameters: ModelParameters = None):
        super().__init__(model_name, None, debug, parameters)

class GeminiModel(Model):
    """
    Interface to send prompts to Gemini models with Google API. Uses REST API over python SDK for finer-grained control
    """
    def __init__(self, model_name: str, api_key : str, debug: bool = False, parameters: GeminiModelParameters = None):
        """
        :param model_name: The name of the model to use. Should be existing ollama model
        :param api_key: The API key for accessing the model
        :param debug: Display debug messages or not. Defaults to False
        :param parameters: The model parameters to use
        :raises InvalidModelException: Raised when an error occurs retrieving model
        """
        super().__init__(model_name, api_key, debug, parameters)
        self.raise_model_exists()

    def get_response(self, prompt : str = None, payload : dict = None, stream : bool = False, timeout : int = 60):
        """
        Gets the response from the model
        :param prompt: An optional parameter for the current message being sent
        :param payload: A dictionary representing the JSON payload to be sent.
                        Contains data like chat history
        :param stream: If True, the response body will not be downloaded immediately.
                       Will not handle streaming-related errors. Defaults to False.
        :param timeout: The timeout in seconds for the request. Defaults to 60.
        :return: The requests.Response object on a successful call.
        :raises ModelError: Raised for any network-level errors (e.g., connection, timeout) or for non-2xx HTTP status codes.
        """
        if stream: #Pick the URL for streaming or not streaming
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:streamGenerateContent?alt=sse&key={self.api_key}"
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        if payload is None:
            prompt = "" if prompt is None else prompt
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

        # Add custom parameters if they exist
        if self.parameters is not None:
            payload["generationConfig"] = self.parameters.to_dict()

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), stream=stream, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise ModelError(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise ModelError(f"Error calling Gemini API: {e}")

        return response

    def raise_model_exists(self):
        """
        Checks if model name exists in gemini API
        :raises InvalidModelException: Raised when an invalid model name is given. Also raised when there is no internet.
        :raises NoInternetException: Raised when no internet connection is found while attempting to retrieve model
        :raises InvalidAPIKeyException: Raised when an invalid API key is given.
        """

        if not connected_to_internet():
            raise NoInternetException(f"Error fetching model : Not connected to the internet")

        try:
            models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
            response = requests.get(models_url)
            response.raise_for_status()

            models_data = response.json()

            available_model_ids = []
            if "models" in models_data:
                for model in models_data["models"]:
                    model_id = model.get("name", "").split("/")[-1]
                    if model_id:
                        available_model_ids.append(model_id)

            if self.model_name not in available_model_ids:
                raise InvalidModelException(f"Model {self.model_name} is not a valid model name.\n"
                                            f"Valid model names are: {", ".join(available_model_ids)}")

        except requests.exceptions.RequestException as e:
            raise InvalidAPIKeyException(f"Error fetching model: {e}\n"
                                        f"Check your API key is correct")
        except Exception as e:
            raise InvalidModelException(f"An unexpected error occurred while fetching models: {e}")

    def invoke(self, prompt : str = None, payload : dict = None) -> str:
        """
        Invoke the LLM with the given prompt
        :param prompt: The prompt to invoke
        :param payload: The payload containing any extra data (e.g. chat history)
        :return: The output message
        :raises ModelError: when an error occurs
        """
        response = self.get_response(prompt = prompt, payload = payload, stream = False)
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as e:
             raise ModelError(f"Error formatting the json response {e}")

    def stream(self, prompt : str = None, payload : dict = None) -> Iterator[str]:
        """
        Streamed the LLM output with the given prompt
        :param prompt: The prompt to invoke, optional
        :param payload: The payload containing any extra data (e.g. chat history)
        :return: The output message
        :raises ModelError: when an error occurs
        """
        response = self.get_response(prompt = prompt, payload = payload, stream = True)
        try:
            for chunk in response.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode("utf-8")
                    if decoded_chunk.startswith('data: '):
                        parsed_chunk = decoded_chunk[len('data: '):]
                        json_chunk = json.loads(parsed_chunk)
                        yield json_chunk['candidates'][0]['content']['parts'][0].get('text', '')
        except Exception as e:
            raise ModelError(f"An unexpected error occurred: {e}")

    def invoke_chat(self, chat_payload : dict[str, dict[str, list]]):
        """
        Get a single LLM output from a given Chat history
        :param chat_payload: the chat data formatted for usage with the gemini API (chat.get_gemini_payload())
        :return: a stream of the output message
        TODO Error messsage when invalid payload for debug, also include in stream
        TODO better yet, refactor this silly code
        """
        return self.invoke(payload = chat_payload)

    def stream_chat(self, chat_payload : dict[str, dict[str, list]]):
        """
        Get a streamed LLM output from a given Chat history
        :param chat_payload: the chat data formatted for usage with the gemini API (chat.get_gemini_payload())
        :return: Text stream for the LLM
        """
        return self.stream(payload = chat_payload)