# terminal-ai
This is a simple CLI tool for chatting to an LLM in the terminal.

Currently, only Gemini is supported, but I'll add Ollama support later. 
Nothing else is planned for now.

****

## Command overview
Consider this a simple overview of *some* of the commands. 
The commands have more functions, which can be viewed by typing chat -h or just typing chat.
There are also some additional commands not mentioned here

- `chat start` - Begin a chat
- `chat once <message>`- Send a single message to the LLM
- `chat list` - List all existing chats
- `chat delete <chat name>` - Delete a chat
- `chat systemprompt <...>` - System prompt configuration
- `chat model <...>` - Model configuration (Add models and API keys here)

When in a chat using `chat start`, there are some in-chat commands. These are:

- `quit/bye/exit` to quit (saves your chat)
- `clear` to clear the chat history (asks for confirmation)
- `retry` to regenerate a new AI response to the previous message
- `save` to save the chat so far
- `systemprompt/system` to display and/or change the system prompt
- `help` to display a help message

Enjoy :)