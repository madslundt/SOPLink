from textwrap import dedent
from llm_models.chat_brd import ChatBRD
from graph.state import State
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def extract_section_to_json(state: State, llm: ChatBRD, section_key: str, key: str) -> State:
    prompt = PromptTemplate.from_template(dedent("""
        Convert markdown document to JSON:

        ```md
        {section}
        ```
    """))

    chain = prompt | llm | JsonOutputParser()

    response = chain.invoke({
        "section": state.get(section_key)
    })

    return { key: response }
