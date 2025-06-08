import uuid
from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from .global_utils import time_now


class BaseModel(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    model_config = ConfigDict(from_attributes=True)