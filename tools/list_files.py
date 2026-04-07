from langchain_core.tools import tool
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import shutil


class ListFilesInput(BaseModel):
    source: str = Field(
        ...,
        description= "source of the directory that we need to modify"
    )

    @field_validator("source")
    @classmethod
    def must_be_absolute(cls, v: str) -> str:
        if not Path(v).is_absolute():
            raise ValueError(f"Source {v} must be absolute")
        
        return v
    

@tool("list_files", ListFilesInput)
def list_files(source -> str) -> list:
    """See all the files in a dir"""
    src = Path(source).resolve()
    
    if not Path(src).is_dir():
        raise ValueError(f"{src} is not a dir")
    
    if not any(Path(src).iterdir()):
        raise ValueError(f"dir {src} is empty")
    
    files = []
    for file in Path(src).iterdir():
        files.append(file)

    return files