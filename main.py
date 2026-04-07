from typing import Dict, TypedDict
from langgraph.graph import StateGraph

class State(TypedDict):
    name : str
    message : str

def compliment_node(state : State) -> State:

    state['message'] = state['name'] + ' you are doing an excellent job!!'

    return state

graph = StateGraph(State)

graph.add_node("greeder", compliment_node)

graph.set_entry_point("greeder")
graph.set_finish_point("greeder")

app = graph.compile()

result = app.invoke({'name': 'bob'})

print(result['message'])
