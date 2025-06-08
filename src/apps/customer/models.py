from sqlmodel import Field, Relationship
from datetime import datetime

from src.global_models import BaseModel
from src.global_utils import time_now


def load_related_models():
    """
    Load related models to avoid circular dependencies.
    """
    from src.apps.user.models import UserModel  # noqa: F401
    from src.apps.road_network.models import RoadNetworkModel  # noqa: F401


class CustomerModel(BaseModel, table=True):
    __tablename__ = "customer"

    name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    users: list["UserModel"] = Relationship(back_populates="customer")  # type: ignore # noqa: F821
    road_networks: list["RoadNetworkModel"] = Relationship(back_populates="customer")  # type: ignore # noqa: F821


# Note: This is not needed in the bottom of the file
load_related_models()