from fastapi import FastAPI, Query
from models import Item, FilterParams, User
from typing import Annotated

app = FastAPI()


@app.get('/')
async def root():
    return {"message": "Hello world"}


@app.get('/items/{item_id}')
async def item_detail(item_id: int):  # default:async def item_detail(item_id):
    return {"item": item_id}


@app.get('/items/{item_id}')
async def item_detail(item_id: int):  # default:async def item_detail(item_id):
    """this code will not execute as the path matches with above function."""
    return {"item": item_id}


@app.get('/check/')
async def item_detail(item_id: int = 2, q: str | None = None):
    """
    item_id will work as query param
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

# /Users/m1user/PycharmProjects/fastapi/.venv/bin/python -m uvicorn main:app --reload
