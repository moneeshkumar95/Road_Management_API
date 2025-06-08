from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict


class PaginationSchema(BaseModel):
    page: int = Query(1, gt=0)
    limit: int = Query(10, gt=0)
    filter: Optional[BaseModel] = None


class CreteadUpdatedBySchema(BaseModel):
    created_by: Optional[str]
    updated_by: Optional[str]


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
