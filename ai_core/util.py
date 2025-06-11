import urllib.request

from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

def markdown_print(text, end="\n", do_markdown=True):
    console = Console()

    if do_markdown:
        if "\n" not in text.strip():
            console.print(text, markup=True, end=end)
        else:
            console.print(Markdown(text))
            if end != "\n":
                console.print(end, end="")
    else:
        print(text, end=end)

def connected_to_internet() -> bool:
    try:
        urllib.request.urlopen('https://google.com')
        return True
    except urllib.error.URLError:
        return False

def output_stream(stream, do_markdown=True):
    """
    Reads content from a string stream token by token, updating a live
    """
    console = Console()
    capture = ""

    if do_markdown:
        with Live(console=console, refresh_per_second=64) as live:
            for raw_chunk in stream:
                capture += raw_chunk
                markdown_renderable = Markdown(capture)
                live.update(markdown_renderable)
    else:
        for raw_chunk in stream:
            capture += raw_chunk
            print(raw_chunk, end="")

    if not capture.endswith("\n"):
        print("")

    return capture.strip()
