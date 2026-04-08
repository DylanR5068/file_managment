from langchain_core.tools import tool
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import  mimetypes
from datetime import datetime
import json

class ReadMetadataInput(BaseModel):
    source: str = Field(
        ...,
        description= "Path of the file to extract metadata"
    )

    @field_validator("source")
    @classmethod
    def must_be_absolute(cls, v: str) -> str:
        if not Path(v).is_absolute():
            raise ValueError(f"{v} must be absolute")
        return v
    
@tool("read_metadata", args_schema= ReadMetadataInput)
def read_metadata(source: str) -> str:
    """read metadata of a file without opening it
    
    Returns a JSON string with: absolute_path, name, size_kb, 
    mime_type, metadata_changed_at, modified_at and is_redeable"""

    path = Path(source).resolve()

    #validating path
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} doesn't exists")
    
    if not Path(path).is_file():
        raise ValueError(f"{path} doesn't a file")
    
    stat = path.stat()

    mime_type, _ = mimetypes.guess_type(str(path))

    metadata = {
        "path":        str(path),
        "name":        path.name,
        "extension":   path.suffix.lower(),
        "size_kb":     round(stat.st_size / 1024, 2),
        "mime_type":   mime_type or "unknown",
        "metadata_changed_at":  datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_readable": path.stat().st_mode & 0o444 != 0,
    }

    return json.dumps(metadata, indent=2)


        