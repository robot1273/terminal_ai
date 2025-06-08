import logging
import os

import yaml
from .template import Template

valid_roles = ["user", "system", "assistant"]

class Message:
    def __init__(self, role : str, content : str):
        self.role = role.lower().strip()
        self.content = content.strip()

        if self.role not in valid_roles:
            logging.warning(f"Role {self.role} is not a valid role. Ensure roles are one of {valid_roles}")

    def to_dict(self):
        return {"role" : self.role, "content" : self.content}

class FormattedMessage(Message):
    def __init__(self, role : str, content : str, format_data : dict):
        Message.__init__(self, role, Template(content, missing_behaviour = "warn").format(format_data))

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

    def export(self, output_file_path, confirm_export = False):
        data = {"system_prompt" : self.system_prompt,
                "messages" : self._messages}

        with open(output_file_path, "w") as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)

        if confirm_export:
            print(f"Successfully exported messages to {output_file_path}")

    def load(self, path, display_messages = True):
        try:
            with open(path, "r") as file:
                data = yaml.safe_load(file)

            if data is None:
                return

            self._messages = data["messages"]
            self.system_prompt = data["system_prompt"]
            print(f"Successfully loaded messages from {path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: {path} not found.")
        except TypeError:
            raise TypeError(f"Error: {path} contains an invalid format.")

        if display_messages:
            self.display_chat_data()

    def display_chat_data(self):
        chat = ""
        for i,m in enumerate(self._messages):
            chat += f"{m["role"]}: {m["content"]}\n"

        print(f"System prompt: {self.system_prompt}\n")
        print(chat)