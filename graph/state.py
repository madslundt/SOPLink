from typing import TypedDict


class State(TypedDict):
    document_path: str
    markdown: str
    samples_section: str
    samples_json: dict
    sst_section: str
    sst_json: dict
    final_json: dict