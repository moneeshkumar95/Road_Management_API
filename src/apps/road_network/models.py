from typing import Optional
from datetime import datetime

from sqlalchemy import Column
from sqlmodel import Field, Relationship, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement

from src.global_models import BaseModel
from src.global_utils import time_now


def load_related_models():
    """
    Load related models to avoid circular dependencies.
    """
    from src.apps.customer.models import CustomerModel  # noqa: F401


class RoadNetworkModel(BaseModel, table=True):
    __tablename__ = "roadnetwork"
    __table_args__ = (
        UniqueConstraint("customer_id", "name", "version", name="uq_network_customer_name_version"),
    )

    name: str
    version: float
    created_at: datetime = Field(default_factory=time_now)
    customer_id: str = Field(foreign_key="customer.id", index=True)

    customer: "CustomerModel" = Relationship(back_populates="road_networks") # type: ignore # noqa: F821
    edges: list["EdgeModel"] = Relationship(back_populates="network")


class EdgeModel(BaseModel, table=True):
    __tablename__ = "edge"

    network_id: str = Field(foreign_key="roadnetwork.id", index=True)
    is_active: bool = Field(default=True)
    properties: dict = Field(
        sa_column=Column(JSONB)
    )
    geometry: Optional[WKBElement] = Field(
        sa_column=Column(Geometry("LINESTRING", srid=4326))
    )

    network: "RoadNetworkModel" = Relationship(back_populates="edges")

    model_config = {
        "arbitrary_types_allowed": True,
    }


# Note: This is not needed in the bottom of the file
load_related_models()
