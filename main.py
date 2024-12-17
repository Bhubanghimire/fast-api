from fastapi import FastAPI, Query, Path, Body
from models import Item, FilterParams, User
from enum import Enum
from typing import Annotated
from dotenv import load_dotenv
from pymongo import MongoClient
import os

from serializers import serialize_document

# Load environment variables
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet18 = "resnet18"
    lenet = "lenet"


app = FastAPI()


@app.get('/')
async def root():
    return {"message": "Hello world"}


@app.get('/items/{item_id}')
async def item_detail(item_id: int):  # default:async def item_detail(item_id):
    return {"item": item_id}


@app.get('/users/{user_id}/items/{item_id}')
async def item_detail(user_id: int, item_id: int, needy:str, query: str | None = None):  # default:async def item_detail(item_id):
    """this code will not execute as the path matches with above function."""
    if query is None:
        return {"item": item_id, "user": user_id}
    else:
        return {"item": item_id, "user": user_id, "query": query}


@app.get("/models/{model_name}")
async def model_detail(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model": "alexnet", "mesage": "AlexNet model"}

    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model": model_name}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


fake_item_db = [
    {"item_name": "apple"},
    {"item_name": "banana"},
    {"item_name": "baz"},
]


@app.get('/items/')
async def read_item(skip: int = 0, limit: int = 10, q: str | None = None, short: bool = False):
    # fake_item_db = db.items.find()
    query = {}
    if q:
        query = {"name":{"$regex": q, "$options":"i"}}

    fake_item_db = db.items.find(query)
    items = [serialize_document(item) for item in fake_item_db]
    return items


@app.get('/check/')
async def item_detail(item_id: int = 2, q: str | None = None):
    """
    item_id,q will work as query param
    :param q:
    :param item_id: str
    :return: json
    """
    response = {"item": item_id}
    if q:
        response.update({"q": q})

    return response


@app.post('/item/')
async def create(item: Item):
    item_dict = item.dict()
    if item.tax:
        item_dict.update({"price_with_tax": item.tax + item.price})
    results = db.items.insert_one(item_dict)
    item_dict["_id"] = str(results.inserted_id)
    return item_dict


@app.post('/create/{item_id}/')
async def create_view(item_id: int, item: Item, user: User, q: Annotated[str | None, Query(
    title="Query string",
    description="Query string for the items to search in the database that have a good match",
    min_length=5)] = None):
    if q:
        item.name = q
    item_dict = item.dict()
    item_dict.update({"item_id": item_id, "user": user})
    return item_dict


@app.get('/filter/')
async def filteritem(item: Annotated[FilterParams, Query()]):
    return item


@app.put('/items/{item_id}')
async def update(
                user:User,
                item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
                body:Annotated[str | None, Body()],
                item: Annotated[Item | None, Body()],
                q: str | None = None,
                 ):
    results = {"item_id": item_id, "user": user}
    if item:
        results.update({"item": item})

    if q:
        results.update({"q": q})
    if body:
        results.update({"body": body})

    return results

# /Users/m1user/PycharmProjects/fastapi/.venv/bin/python -m uvicorn main:app --reload
