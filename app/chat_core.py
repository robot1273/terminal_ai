from ai_core.message import Message, Chat
from ai_core.model import GeminiModel, GeminiModelParameters
from ai_core.util import output_wrapped_stream

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

def start_chat(chat_source):
    chat = Chat()

    chat.load(chat_source, False)

    do_stream = True

    while True:
        prompt = input(">> ")

        if len(prompt) != 0:
            match prompt.lower().strip():
                case "quit" | "q" | "bye" | "exit":
                    chat.export(chat_source)
                    break
                case "clear":
                    chat.clear()
                    print("Chat cleared")
                    continue
                case "retry":
                    print("Regenerating a new response")
                    chat.remove_last_message()
                    continue
                case "save":
                    chat.export(chat_source, confirm_export = True)
                    continue

            chat.add_message(Message("user", prompt))

        if do_stream:
            stream = model.stream_chat(chat)
            response = output_wrapped_stream(stream)
        else:
            response = model.invoke_chat(chat)
            print(response.strip())

        chat.add_message(Message("assistant", response))