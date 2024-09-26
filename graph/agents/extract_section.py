from textwrap import dedent
from llm_models.chat_brd import ChatBRD
from graph.state import State
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate


def extract_section(state: State, llm: ChatBRD, key: str) -> State:
    prompt = PromptTemplate.from_template(dedent("""
        Extract the relevant section from markdown document:

        ```md
        {document}
        ```
    """))

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "document": state['markdown']
    })

    return { key: response }
