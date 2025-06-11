from ai_core.message import Message
from ai_core.chat import Chat
from ai_core.model import GeminiModel, GeminiModelParameters
from ai_core.util import output_wrapped_stream, output_stream

import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

api_key = os.getenv("GEMINI_API_KEY")

geminiParameters = GeminiModelParameters(
    temperature = 0.3,
    top_p = 0.75,
    num_predict = 8000
)

model_name = "gemini-2.0-flash"
model = GeminiModel(model_name,
                    api_key,
                    debug = False,
                    parameters=geminiParameters)

help_message = """
type quit/bye/exit to quit (saves your chat)
type clear to clear the chat history (asks for confirmation)
type retry to regenerate the previous AI response
type save to save the chat so far
type help to display this message
"""

def single_message(message : str, chat_source = None, do_stream = True):
    chat = Chat()

    if chat_source is not None:
        chat.load(chat_source, False)

    chat.add_message(Message("user", message))

    if do_stream:
        stream = model.stream_chat(chat.get_gemini_payload())
        response = output_stream(stream)
    else:
        response = model.invoke_chat(chat.get_gemini_payload())
        print(response.strip())

    if chat_source is not None:
        chat.add_message(Message("assistant", response))
        chat.export(chat_source, False)

def start_chat(chat_source, do_stream = True):
    chat = Chat()

    chat.load(chat_source, False)
    while True:
        prompt = input(">> ")

        if len(prompt) != 0:
            match = True
            match prompt.lower().strip():
                case "h" | "help":
                    print(help_message)
                case "quit" | "q" | "bye" | "exit":
                    chat.export(chat_source, model)
                    break
                case "clear":
                    if input("Are you sure you want to clear the chat history? (y/n) > ").lower() == "y":
                        chat.clear()
                        print("Chat history cleared")
                case "retry":
                    print("Regenerating a new response...")
                    chat.remove_last_message()
                    match = False
                case "save":
                    chat.export(chat_source, model, confirm_export = True)
                case "system" | "systemprompt":
                    system_prompt = input("Input the new system prompt for this chat "
                                          "\nType nothing to cancel, type ? to display the current system prompt"
                                          "\n > ").strip()
                    if system_prompt == "?":
                        print(f"Current system prompt:\n\"{chat.system_prompt.strip()}\"\n")
                    elif system_prompt != "":
                        chat.set_system_prompt(system_prompt)
                        print("Successfully set system prompt")
                case _:
                    match = False

            if match:
                continue

            chat.add_message(Message("user", prompt))

        if do_stream:
            stream = model.stream_chat(chat.get_gemini_payload())
            response = output_stream(stream)
        else:
            response = model.invoke_chat(chat.get_gemini_payload())
            print(response.strip())

        chat.add_message(Message("assistant", response))