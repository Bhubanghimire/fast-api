from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {"message":"Hello world"}

@app.get('/{item_id}')
async def item_detail(item_id:float):
    return {"item":item_id}


@app.get('/check/')
async def item_detail(item_id:int=2,q:str |None=None):
    """
    item_id will work as query param
    :param item_id: str
    :return: json
    """
    return {"item":item_id}

# /Users/m1user/PycharmProjects/fastapi/.venv/bin/python -m uvicorn main:app --reload
