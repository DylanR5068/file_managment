from typing import TypedDict, Dict, Any, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    mesagges: Annotated[list, add_messages]
    directory: str
    file_list: str
    metadata: list[str]
    errors: list[str]
