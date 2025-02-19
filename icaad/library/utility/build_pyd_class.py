from pydantic import BaseModel, Field
from typing import Any

def add_field(model: BaseModel, field_name: str, field_type: type, description: str, default_value: Any = None):
    model.__fields__[field_name] = Field(default_value, title=field_name, description=f"{description}",annotation=field_type)
    model.__fields_set__ = set(model.__fields__.keys())
    model.__annotations__[field_name] = field_type

