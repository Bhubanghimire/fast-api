from bson import ObjectId
from fastapi import FastAPI, Query, Path, Body, HTTPException, Form, UploadFile

from form import UserForm
from models import Item, FilterParams, User, Offer
from enum import Enum
from typing import Annotated
from dotenv import load_dotenv
from pymongo import MongoClient
import os

from serializers import serialize_document, serialize_documents

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


@app.get('/', responses={
    200: {"description": "Request was successful",
          "content": {"application/json": {"example": {"message": "Request was successful"}}}},
    400: {"description": "Bad Request",
          "content": {"application/json": {"example": {"message": "There was an error with the request"}}}},
})
async def root(some_condition: bool):
    if some_condition:
        return {"message": "Request was successful"}
    else:
        raise HTTPException(status_code=400, detail="There was an error with the request")


@app.get('/items/{item_id}', status_code=200)
async def item_detail(item_id: str):  # default:async def item_detail(item_id):
    try:
        item_id_obj = ObjectId(item_id)
    except Exception as e:
        return {"error": f"Invalid item_id format: {e}"}

    obj = db.items.find_one({"_id": item_id_obj})
    results = serialize_document(obj)
    return results


@app.get('/users/{user_id}/items/{item_id}')
async def item_detail(user_id: int, item_id: int, needy: str,
                      query: str | None = None):  # default:async def item_detail(item_id):
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
        query = {"name": {"$regex": q, "$options": "i"}}

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
        user: User,
        item_id: Annotated[str, Path(title="The ID of the item to get", max_length=100)],
        body: Annotated[str | None, Body()],
        item: Annotated[Item | None, Body()],
        q: str | None = None,
):
    try:
        item_id_obj = ObjectId(item_id)
    except Exception as e:
        return {"error": f"Invalid item_id format: {e}"}

    obj = db.items.find_one({"_id": item_id_obj})
    results = serialize_document(obj)
    if item:
        update_data = {key: value for key, value in item.dict().items() if value is not None}

        if update_data:
            updated_results = db.items.update_one({"_id": item_id_obj}, {"$set": update_data})
            # Fetch the updated document
            updated_obj = db.items.find_one({"_id": item_id_obj})
            results = serialize_document(updated_obj)
    # if q:
    #     results.update({"q": q})
    # if body:
    #     results.update({"body": body})
    return results


@app.get('/users/')
async def read_users():
    results = db.users.find().to_list(length=100)
    if results:
        results = serialize_documents(results)
    else:
        results = {}  # serialize_document(results)
    return results


@app.post('/offers/')
async def create_offer(offers: list[Offer]):
    # Convert Pydantic models to a list of dictionaries
    offers_dicts = [offer.dict() for offer in offers]

    # Insert into MongoDB
    result = db.offers.insert_many(offers_dicts)

    # Retrieve the inserted documents from MongoDB
    inserted_offers = db.offers.find({"_id": {"$in": result.inserted_ids}}).to_list(length=None)

    # Serialize each document by converting ObjectId to string
    response = [serialize_document(offer) for offer in inserted_offers]

    return response


@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username, "password": password}


@app.post("/form/login/")
async def login_form(form: Annotated[UserForm, Form()], ):
    form = form.dict()
    username = form['username']
    password = form['password']
    user = db.users.find_one({"username": username})
    response = serialize_document(user)
    return response

@app.post("/uploadfiles/")
async def upload_files(file: UploadFile):
    MEDIA_FOLDER = "media"
    # Filepath where the file will be saved
    file_path = os.path.join(MEDIA_FOLDER, file.filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        content = await file.read()  # Read the file content asynchronously
        buffer.write(content)  # Write the content to the media folder

    return {"filename": file.filename, "filepath": file_path}


# /Users/m1user/PycharmProjects/fastapi/.venv/bin/python -m uvicorn main:app --reload
