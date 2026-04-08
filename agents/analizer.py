# agents/analizer.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from loguru import logger
from tools.list_files import list_files
from tools.read_metadata import read_metadata
from graph.state import State
import json
import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM solo para list_files ---
llm = ChatOpenAI(
    api_key=os.getenv("api_groq_key"),
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.3-70b-versatile",
    temperature=0.1
)

tools = [list_files]  # solo list_files — read_metadata lo ejecutas tú
tools_by_name = {"list_files": list_files}
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """You are a file scanner agent. You have one tool:
- list_files: lists all files in a directory, returns absolute paths and sizes

Your job:
1. Call list_files on the directory provided
2. Once you have the file list, stop — do not call any other tools

Return only the file list. Nothing else."""


def _parse_file_paths(file_list_output: str) -> list[str]:
    """Extrae las rutas absolutas del output de list_files."""
    paths = []
    for line in file_list_output.splitlines():
        line = line.strip()
        if line.startswith("/"):
            # El formato es "/ruta/archivo.pdf  (12.3 KB)"
            path = line.split("  ")[0].strip()
            paths.append(path)
    return paths


def analizer_node(state: State) -> dict:
    directory = state["directory"]
    messages = list(state.get("messages", []))
    collected_metadata = []
    errors = []
    file_list_raw = ""
    total_tokens = 0

    # --- Paso 1: El LLM llama list_files ---
    messages.append(HumanMessage(
        content=f"List all files in this directory: {directory}"
    ))

    for step in range(5):  # máximo 5 pasos para el list_files
        logger.info(f"Agent step {step + 1}")

        response = llm_with_tools.invoke(
            [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        )
        messages.append(response)

        usage = response.usage_metadata
        total_tokens += usage["total_tokens"]
        logger.info(f"Step {step+1} tokens: {usage['total_tokens']}")

        if not response.tool_calls:
            logger.info("Agent finished listing files")
            break

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id   = tool_call["id"]

            logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

            try:
                result = list_files.invoke(tool_args)
                file_list_raw = result  # guardamos el output crudo
            except Exception as e:
                logger.error(f"list_files failed: {e}")
                result = f"ERROR: {str(e)}"
                errors.append(str(e))

            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_id
            ))

    # --- Paso 2: Tú ejecutas read_metadata directamente sin pasar por el LLM ---
    file_paths = _parse_file_paths(file_list_raw)
    logger.info(f"Found {len(file_paths)} files — extracting metadata directly")

    for path in file_paths:
        try:
            result = read_metadata.invoke({"source": path})
            collected_metadata.append(json.loads(result))
            logger.info(f"Metadata OK: {path}")
        except Exception as e:
            logger.warning(f"read_metadata failed for {path}: {e}")
            errors.append(f"{path}: {str(e)}")

    logger.info(f"Scanner done — {len(collected_metadata)} files, {len(errors)} errors")

    return {
        "messages": messages,
        "file_list": file_list_raw,
        "metadata": collected_metadata,
        "errors": errors
    }