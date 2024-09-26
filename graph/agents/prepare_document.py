import pathlib

from graph.state import State
from sops.utils.convert_word_to_markdown import convert_word_to_markdown
from sops.utils.reformat_markdown import reformat_markdown


def prepare_document(state: State) -> State:
    document_path = state.get("document_path")
    file_extension = pathlib.Path(document_path).suffix

    if file_extension in ['.doc', '.docx']:
        markdown = convert_word_to_markdown(document_path)
        markdown = reformat_markdown(markdown)

        return { "markdown": markdown }
    
    raise ValueError(f"{file_extension} not supported")