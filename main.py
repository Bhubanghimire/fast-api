
from fastapi import FastAPI, Query
from models import Item
from typing import Annotated

app = FastAPI()


@app.get('/')
async def root():
    return {"message": "Hello world"}


@app.get('/{item_id}')
async def item_detail(item_id: float):
    return {"item": item_id}


@app.get('/check/')
async def item_detail(item_id: int = 2, q: str | None = None):
    """
    item_id will work as query param
    :param item_id: str
    :return: json
    """
    return {"item": item_id}


@app.post('/item/')
async def create(item: Item):
    return item


@app.post('/create/{item_id}/')
async def create_view(item_id: int, item: Item, q:Annotated[str|None, Query(max_length=5)]=None):
    print(f"item id: {item_id}, item data: {item.dict()}, query data:{q}")
    if q:
        item.name=q
    return item

# /Users/m1user/PycharmProjects/fastapi/.venv/bin/python -m uvicorn main:app --reload
