from pydantic import BaseModel, EmailStr, field_validator

from src.apps.user.models import UserType


class UserLoginSchema(BaseModel):
    username: str
    password: str

    @field_validator("username", mode="before")
    def convert_username_to_lowercase(cls, value: str) -> str:
        if value:
            return value.lower()
        return value


class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    conform_password: str
    customer_id: str
    type: UserType = UserType.USER
    customer_id: str

    @field_validator("username", mode="before")
    def convert_username_to_lowercase(cls, value: str) -> str:
        if value:
            return value.lower()
        return value