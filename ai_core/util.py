import urllib.request
def connected_to_internet() -> bool:
    try:
        urllib.request.urlopen('https://google.com')
        return True
    except urllib.error.URLError:
        return False

def output_wrapped_stream(stream, max_chars = 90):
    current_line, capture = "", ""
    for raw_chunk in stream:
        chunk = raw_chunk
        capture += chunk
        print(chunk, end="")

        for word in chunk.split():
            if "\n" in word:
               current_line = word
            else:
                current_line += word.strip()

        if len(current_line) > max_chars:
            current_line = ""
            print("")

    return capture

def output_stream(stream):
    capture = ""
    for raw_chunk in stream:
        capture += raw_chunk
        print(raw_chunk, end = "")

    return capture