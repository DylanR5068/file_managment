from langchain_core.tools import tool
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from typing import Optional
import shutil


class ListFilesInput(BaseModel):
    source: str = Field(
        ...,
        description= "source of the directory that we need to modify"
    )
    recursive: bool = Field(
        False,
        description = "if true list the files in subdirectories too"
    )
    include_hide: bool = Field(
        False,
        description= "if true, list the hide files"
    )
    extension_filter: Optional[str] = Field(
        None,
        description= "only returns files with the extension. Example: '.pdf'"
    )
    max_files: int = Field(
        200,
        description= "max files that we will analize, between 1 and 1000"
    )

    @field_validator("source")
    @classmethod
    def must_be_absolute(cls, v: str) -> str:
        if not Path(v).is_absolute():
            raise ValueError(f"Source {v} must be absolute")
        
        return v
    

@tool("list_files", args_schema =ListFilesInput)
def list_files(
    source: str,
    recursive: bool = False,
    include_hide: bool = False,
    extension_filter: Optional[str] = None,
    max_files: int = 200
) -> str:
    
    """list of all the files in a dir
    
    returns plaint-text list the llm can read directly
    each line contains the absolute path an size in Kb"""


    src = Path(source).resolve()
    
    if not Path(src).exists():
        raise FileNotFoundError(f"{src} doesn't exists")
    if not Path(src).is_dir():
        raise ValueError(f"{src} is not a dir")
    
    if not any(Path(src).iterdir()):
        raise ValueError(f"dir {src} is empty")
    
    pattern = "**/*" if recursive else "*"
    files = [
        p for p in src.glob(pattern) if p.is_file()
    ]
    

    #Filters
    if not include_hide:
        files = [
            p for p in files
            if not p.name.startswith(".")
        ]

    if extension_filter:
        ext = extension_filter.lower() if extension_filter.startswith('.') else f".{extension_filter.lower()}"
        files = [p for p in files if p.suffix.lower() == ext]

    #control file quantiti
    truncated = len(files) > max_files
    files = files[:max_files]

    lines = [f"Directory: {src}", f"Files found: {len(files)}", ""]
    for p in sorted(files):
        size_kb = p.stat().st_size / 1024
        lines.append(f"{p}  ({size_kb:.1f} KB)")

    if truncated:
        lines.append(f"\n[Truncated — more files exist beyond {max_files} results]")

    return "\n".join(lines)