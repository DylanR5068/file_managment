from langgraph.graph import StateGraph
from graph.state import State
from agents.analizer import analizer_node

graph = StateGraph(State)

graph.add_node("analizer_node", analizer_node)
graph.set_entry_point("analizer_node")
graph.set_finish_point("analizer_node")

app = graph.compile()