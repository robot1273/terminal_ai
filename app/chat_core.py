from ai_core.message import Message
from ai_core.chat import Chat
from ai_core.model import Model
from ai_core.util import output_stream, markdown_print

help_message = """
type quit/bye/exit to quit (saves your chat)
type clear to clear the chat history (asks for confirmation)
type retry to regenerate the previous AI response
type save to save the chat so far
type systemprompt/system to display and/or change the system prompt
type help to display this message
"""

def output_response(chat : Chat, model : Model, do_stream : bool, do_markdown : bool):
    if do_stream:
        stream = model.stream_chat(chat.get_gemini_payload())
        response = output_stream(stream, do_markdown=do_markdown)
    else:
        response = model.invoke_chat(chat.get_gemini_payload())
        if do_markdown:
            markdown_print(response.strip())
        else:
            print(response.strip())

    return response

def single_message(message : str, model : Model, chat_source = None, do_stream = True, do_markdown = True):
    chat = Chat()

    if chat_source is not None: #load cha
        chat.load(chat_source, False)

    chat.add_message(Message("user", message))

    response = output_response(chat, model, do_stream, do_markdown)

    if chat_source is not None:
        chat.add_message(Message("assistant", response))
        chat.export(chat_source, model, False)

def start_chat(chat_source : str, model : Model, do_stream = True, do_markdown = True):
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
                    print(f"Current system prompt:\n\"{chat.system_prompt.strip()}\"\n")
                    system_prompt = input("Input the new system prompt for this chat, type nothing to cancel"
                                          "\nprompt >> ").strip()
                    if system_prompt != "":
                        chat.set_system_prompt(system_prompt)
                        print("Successfully set system prompt")
                case _:
                    match = False

            if match:
                continue

            chat.add_message(Message("user", prompt))

        response = output_response(chat, model, do_stream, do_markdown)

        chat.add_message(Message("assistant", response))