from datetime import datetime
import json
import os
from textwrap import dedent
from graph.graph import build_graph
from langchain_core.runnables.graph import NodeStyles

DOCUMENT_PATH = "sops/reports/A3344- Styrke, dosisvariation og ID af Estradiol og Norethisteronacetat i tabletter granulater.._.docx"


def main() -> None:
    configs = {"configurable": {"thread_id": 42}}
    graph = build_graph()

    update_markdown(graph)

    # result = graph.invoke({
    #     "document_path": DOCUMENT_PATH,
    #     "markdown": "",
    #     "samples_section": "",
    #     "samples_json": {},
    #     "sst_section": "",
    #     "sst_json": {},
    #     "final_json": "",
    # }, configs)

    # add_results(result)

    # return result

def update_markdown(graph) -> None:
    with open("graph/graph.md", "w") as f:
        f.write(dedent(f"""
```mermaid
{graph.get_graph().draw_mermaid(
    node_colors=NodeStyles(first="fill:#222", last="fill:#222", default="fill:#333"),
)}
```
        """))

def add_results(result) -> None:
    sop_results_dir: str = "sop_results/"

    if not os.path.exists(sop_results_dir):
        os.mkdir(sop_results_dir)

    now = datetime.now()
    timestamp = datetime.timestamp(now)

    filtered_dict: dict = {
        k: v for k, v in result.items() if k != "markdown"
    }

    with open(f"{sop_results_dir}{timestamp}.json", "w") as f:
        f.write(json.dumps(filtered_dict, indent=2))


if __name__ == "__main__":
    main()
