import re

class Template:
    def __init__(self, prompt : str,
                prefix : str = "{{",
                suffix : str = "}}",
                missing_behaviour : str = "empty",
                default_arguments : dict = None):
        """
        Generic template class
        :param prompt: The prompt containing tokens to be replaced.
        :param prefix: The string that marks the beginning of a token (default: "{{").
        :param suffix: The string that marks the end of a token (default: "}}").
        :param missing_behaviour: The behaviour to replace missing token
                                  - "empty" replaces missing tokens with empty strings. (default)
                                  - "ignore" does not do anything to the missing tokens.
                                  - "warn" does do anything, but sends a warning message. TODO logging
        :param default_arguments: The default token/values to be replaced. Defaults to None.
        """
        self.prompt = prompt
        self.prefix = prefix
        self.suffix = suffix
        self.missing_behaviour = missing_behaviour
        self.default_arguments = default_arguments

    def add_default(self, token, value) -> None:
        """
        Adds a default token to the template.
        :param token: the token to be added.
        :param value: the value of the default token to replace it
        """
        if self.default_arguments is None:
            self.default_arguments = {}
        self.default_arguments[token] = value

    def format(self, _arguments : dict = None, **kwargs) -> str:
        """
        Formats the template with a given set of tokens.
        Example use: template.format({"token" : "replacement", ...}) and/or template.format(token = "replacement", ...)
        :param _arguments: The values to replace the tokens with as a dictionary. Optional
        :param kwargs: Arbitrary keyword args where each keyword is a token name and its value is the replacement.
        :return: The formatted string.
        """

        arguments = {}
        if _arguments:
            arguments.update(_arguments)
        arguments.update(kwargs)

        tokens_found = re.findall(f"{re.escape(self.prefix)}(.*?){re.escape(self.suffix)}", self.prompt)
        if not tokens_found:  # No tokens to replace
            return self.prompt

        formatted_prompt = self.prompt
        for token in set(tokens_found):
            full_token = f"{self.prefix}{token}{self.suffix}"
            if token in arguments:
                formatted_prompt = formatted_prompt.replace(full_token, str(arguments[token]))
            elif self.default_arguments and token in self.default_arguments:
                formatted_prompt = formatted_prompt.replace(full_token, str(self.default_arguments[token]))
            else:
                match self.missing_behaviour:
                    case "empty": formatted_prompt = formatted_prompt.replace(full_token, "")
                    case "warn" : print(f"WARNING: Token {token} was not be replaced")
                    case "ignore" : pass

        return formatted_prompt

    def partial_format(self, _arguments: dict = None, **kwargs) -> "Template":
        """
        Formats the template with a given set of tokens, but returns a new template with this prompt instead of a string
        :param _arguments: The values to replace the tokens with as a dictionary. Optional
        :param kwargs: Arbitrary keyword args where each keyword is a token name and its value is the replacement.
        :return: The partially formatted template
        """
        formatted_string = format(_arguments, **kwargs)
        return Template(formatted_string, self.prefix, self.suffix, self.missing_behaviour, self.default_arguments)

    def expected_tokens(self) -> set[str]:
        """
        Gets all tokens present in the template.
        :return: A set of all tokens that may be replaced in the template
        """
        return set(re.findall(f"{re.escape(self.prefix)}(.*?){re.escape(self.suffix)}", self.prompt))