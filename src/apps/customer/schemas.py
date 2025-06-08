from pydantic import BaseModel, field_validator


class CreateCustomerSchema(BaseModel):
    name: str

    @field_validator("name", mode="before")
    def convert_name_to_lowercase(cls, value: str) -> str:
        if value:
            return value.lower()
        return value