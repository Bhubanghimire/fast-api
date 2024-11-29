from pydantic import BaseModel, Field
from typing import Literal


class User(BaseModel):
    username: str
    first_name: str
    last_name: str |None=None


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: int


class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    # tags: list['str'] = []

