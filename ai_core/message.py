import logging

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