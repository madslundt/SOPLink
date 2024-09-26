from graph.state import State


def combine_final_json(state: State) -> State:
    result = {
        **state["samples_json"],
        **state["sst_json"]
    }

    return { "final_json": result }