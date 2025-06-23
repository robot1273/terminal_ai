import yaml

from .message import Message
from .model import Model


class Chat:
    """
    Stores all messages sent by the user or LLM agents
    """
    def __init__(self):
        self._messages = []
        self.system_prompt = ""

    def add_message(self, message : Message):
        if len(message.content.strip()) != 0:
            self._messages.append(message.to_dict())

    def remove_last_message(self):
        self._messages.pop()

    def clear(self):
        self._messages = []

    def get_gemini_payload(self):
        """
        :return: Returns the messages formatted for gemini usage. Does not work for older models due to system instruction TODO
        """
        if len(self._messages) == 0:
            return None

        content = []
        system_message_parts = [{"text" : self.system_prompt}]
        for m in self._messages:
            if m["role"] != "system":
                role = "model" if m["role"] == "assistant" else m["role"]
                content.append({"role": role, "parts": [{"text": m["content"]}]})
            else:
                system_message_parts.append({"text" : m["content"]})

        if len(system_message_parts) != 0:
            return {"system_instruction" : {"parts" : system_message_parts}, "contents" : content}
        else:
            return {"contents" : content}

    def load(self, path: str, display_messages: bool = False, confirm_load=False) ->  None:
        """
        Loads in chat data from a given chat .yaml file
        :param path: the path to the chat .yaml file
        :param display_messages: whether to display a list of all messages after loading
        :param confirm_load: whether to print a confirmation message of loading or not
        """
        try:
            with open(path, "r") as file:
                data = yaml.safe_load(file)

            if data is None:
                return

            self._messages = data["messages"]
            self.system_prompt = data["system_prompt"]

            if confirm_load:
                print(f"Successfully loaded messages from {path}")

            if display_messages:
                self.display_chat_data()
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: {path} not found.")
        except TypeError:
            raise TypeError(f"Error: {path} contains an invalid format.")

    def export(self, chat_source : str, model : Model, confirm_export : bool = False) -> None:
        """
        Save a Chat class into a .yaml file
        :param chat_source: the path to the .yaml file to save the chat into
        :param model: the model that is currently being used for this chat
        :param confirm_export: whether to print a confirmation message of exporting or not
        """
        data = {
                "model" : model.model_name,
                "system_prompt": self.system_prompt,
                "messages": self._messages
                }

        with open(chat_source, "w") as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)

        if confirm_export:
            print(f"Successfully exported messages to {chat_source}")

    def display_chat_data(self):
        chat = ""
        for i,m in enumerate(self._messages):
            chat += f"{m["role"]}: {m["content"]}\n"

        print(f"System prompt: {self.system_prompt}\n")
        print(chat)

    def set_system_prompt(self, system_prompt : str):
        self.system_prompt = system_prompt