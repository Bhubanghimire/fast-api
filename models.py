from pydantic import BaseModel, Field
from typing import Literal


class User(BaseModel):
    username: str
    first_name: str
    last_name: str | None = None


class Item(BaseModel):
    name: str = Field(
        title="Name of the item",
        max_length=100
    )
    description: str | None = Field(
        title="Description of the item",
        default=None,
        max_length=1000
    )
    price: float = Field(
        description="Price of the item must be greater than 0.",
        gt=0
    )
    tax: float | None = None
    tags: list[str] = Field(default_factory=list)
    added_by: User | None = None


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}  # blocks extra data in query params
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = Field(default_factory=list)


class Offer(BaseModel):
    name: str = Field()
    description: str = Field(examples=['Offer example'])
    price: float = Field(examples=[22.22])
    items: list[Item] = Field(default_factory=list)
    model_config = {
        "json_schema_extra": {
            "examples": [
                  {
                    "name": "dashain offer",
                    "description": "5% discount on any items",
                    "price": 0,
                    "items": [
                      {
                        "name": "test",
                        "description": "ok",
                        "price": 1,
                        "tax": 0,
                        "tags": [
                          "string"
                        ],
                        "added_by": {
                          "username": "bhuban",
                          "first_name": "bhuban",
                          "last_name": "ghimire"
                        }
                      }
                    ]
                  }
                ]
        }
    }