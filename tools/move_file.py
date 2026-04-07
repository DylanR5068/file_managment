from langchain_core.tools import tool
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import shutil


class MoveFileInput(BaseModel):
    source: str = Field(
        ...,
        description = "Absolute path of the file to move"
    )
    destination: str = Field(
        ...,
        description= "Absolute destination of the file to move"
    )
    overwrite: bool = Field(
        False,
        description= "overwrite file if it already exist"
    )

    @field_validator("source", "destination")
    @classmethod
    def must_be_absolute(cls, v: str) -> str:
        if not Path(v).is_absolute():
            raise ValueError(f"{v} must be absolute")
        return v

@tool("move_file", args_schema=MoveFileInput)
def move_file(source: str, destination: str, overwrite = False) -> str:
    """Move files from source to destination
    
    The llm should return a str saying how was the movement"""

    src = Path(source).resolve()
    dst = Path(destination).resolve()

    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")

    if not dst.exists():
        raise FileNotFoundError(f"Source not found: {dst}")
    
    logger.info(f"the source {src} and destination {dst} already exist and found")

    if dst.is_dir():
        dst = dst / src.name

    if dst.exists() and not overwrite:
        raise FileExistsError(
            f"Destination already exists: {dst}. "
            f"Set overwrite=True to replace it."
        )
    
    dst.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(src), str(dst))

    return f"moved: {src} -> {dst}"
    