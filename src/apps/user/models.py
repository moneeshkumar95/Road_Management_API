from typing import Optional
from sqlmodel import Field, Relationship
from datetime import datetime
from enum import Enum

from src.global_models import BaseModel
from src.global_utils import time_now


def load_related_models():
    """
    Load related models to avoid circular dependencies.
    """
    from src.apps.customer.models import CustomerModel  # noqa: F401


class UserType(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserModel(BaseModel, table=True):
    __tablename__ = "user"

    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    type: UserType = Field(default=UserType.USER)
    created_by: Optional[str] = Field(default=None, nullable=True)
    updated_by: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)
    is_active: bool = Field(index=True, default=True)

    customer_id: str = Field(foreign_key="customer.id", index=True)
    customer: "CustomerModel" = Relationship(back_populates="users")  # type: ignore # noqa: F821


# Note: This is not needed in the bottom of the file
load_related_models()