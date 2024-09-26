from graph.agents.combine_final_json import combine_final_json
from graph.agents.extract_section import extract_section
from graph.agents.extract_section_to_json import extract_section_to_json
from graph.agents.prepare_document import prepare_document
from graph.state import State
from llm_models.chat_brd import ChatBRD
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from utils.env import get_chat_brd_base_url, get_chat_brd_secret_key, get_chat_brd_username

load_dotenv()

chatbot_models = {
    "samples_extract": {
        "chatbot_pk": "chatbot_pk",
        "chatbot_sk": "chatbot_sk1",
    },
    "samples_json": {
        "chatbot_pk": "chatbot_pk",
        "chatbot_sk": "chatbot_sk2",
    },
    "sst_extract": {
        "chatbot_pk": "chatbot_pk",
        "chatbot_sk": "chatbot_sk3",
    },
    "sst_json": {
        "chatbot_pk": "chatbot_pk",
        "chatbot_sk": "chatbot_sk4",
    },
}

def get_llm(chatbot_pk: str, chatbot_sk: str) -> ChatBRD:
    llm = ChatBRD(
        username=get_chat_brd_username(),
        secret_key=get_chat_brd_secret_key(),
        base_url=get_chat_brd_base_url(),
        chatbot_pk=chatbot_pk,
        chatbot_sk=chatbot_sk,
    )

    return llm

def build_graph():
    workflow = StateGraph(State)

    workflow.add_node("prepare_document", prepare_document)


    # SAMPLES
    workflow.add_node("extract_samples_section", lambda state: extract_section(
        state,
        get_llm(**chatbot_models['samples_extract']),
        key="samples_section")
    )
    workflow.add_node("convert_samples_to_json", lambda state: extract_section_to_json(
        state,
        get_llm(**chatbot_models['samples_json']),
        key="samples_json",
        section_key="samples_section")
    )

    # SST
    workflow.add_node("extract_sst_section", lambda state: extract_section(
        state,
        get_llm(**chatbot_models['sst_extract']),
        key="sst_section")
    )
    workflow.add_node("convert_sst_to_json", lambda state: extract_section_to_json(
        state,
        get_llm(**chatbot_models['sst_json']),
        key="sst_json",
        section_key="sst_section")
    )


    workflow.add_node("combine_final_json", combine_final_json)

    workflow.set_entry_point("prepare_document")
    workflow.set_finish_point("combine_final_json")

    workflow.add_edge("prepare_document", "extract_samples_section")
    workflow.add_edge("prepare_document", "extract_sst_section")

    workflow.add_edge("extract_samples_section", "convert_samples_to_json")
    workflow.add_edge("extract_sst_section", "convert_sst_to_json")

    workflow.add_edge("convert_samples_to_json", "combine_final_json")
    workflow.add_edge("convert_sst_to_json", "combine_final_json")

    checkpointer = MemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph

