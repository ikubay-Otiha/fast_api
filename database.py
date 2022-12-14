from decouple import config
from fastapi import HTTPException
from typing import Union
import motor.motor_asyncio
from bson import ObjectId
from auth_utils import AuthJwtCsrf
import asyncio

MONGO_API_KEY = config("MONGO_API_KEY")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
client.get_io_loop = asyncio.get_event_loop

database = client.API_DB
collection_todo = database.todo
collection_user = database.user
auth = AuthJwtCsrf()

# todo_serializerで辞書形へ変換
def todo_serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"]
    }

def user_serializer(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
    }


# new_todoが辞書型orBoolean型で返される可能性があるのでUnionを用いる。型が違うとエラーが返される
async def db_create_todo(data: dict) -> Union[dict, bool]: 
    todo = await collection_todo.insert_one(data)
    new_todo = await collection_todo.find_one({"_id": todo.inserted_id})
    if new_todo:
        return todo_serializer(new_todo)
    else:
        return False

async def db_get_todos() -> list:
    todos = []
    # .find()でAsyncIOMotorCursorインスタンスを作成。ここではDBとの同期処理はなされない
    # .to_list()でドキュメントを取得する。
    for todo in await collection_todo.find().to_list(length=100):
        todos.append(todo_serializer(todo))
    return todos

async def db_get_single_todo(id: str) -> Union[dict, bool]:
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        return todo_serializer(todo)
    else:
        return False
    
async def db_update_todo(id: str, data: dict) -> Union[dict, bool]:
    # 引数で受け取ったidのオブジェクトが存在するかfind_oneで検証、なければNoneがセットされる
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        # MongoDBのDB更新をcollection_todo.update_oneで実行,Object(id)をDBのidへ、dataをsetへセット
        update_todo = await collection_todo.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        # .modefied属性には実際に更新することができたドキュメントの数が入っている。これが0以上であれば更新が成功したと判定
        if (update_todo.modified_count > 0):
            new_todo = await collection_todo.find_one({"_id": ObjectId(id)})
            return todo_serializer(new_todo)
        elif (todo == data):
            return HTTPException(status_code=401, detail="Object was not updated.")
    return False

async def db_delete_todo(id: str) -> bool:
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        deleted_todo = await collection_todo.delete_one({"_id": ObjectId(id)})
        if (deleted_todo.deleted_count > 0):
            return True
    return False

async def db_signup(data: dict) -> dict:
    email = data.get("email")
    password = data.get("password")
    overlap_user = await collection_user.find_one({"email": email})
    # すでにユーザーが存在する場合=Trueの場合
    if overlap_user:
        raise HTTPException(status_code=400, detail="Email is already taken.")
    # PWのValidation　not passwordはPWがないことを意味する
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="password too short.")
        # hash化されたPWの登録
    user = await collection_user.insert_one({"email": email, "password": auth.generate_hashed_pw(password)})
    new_user = await collection_user.find_one({"_id": user.inserted_id})
    return user_serializer(new_user)

async def db_login(data: dict) -> str:
    email = data.get("email")
    password = data.get("password")
    user = await collection_user.find_one({"email": email})
    if not user or not auth.verify_pw(password, user["password"]):
        raise HTTPException(
            status_code=401, detail="Invalid email or password."
        )
    token = auth.encode_jwt(user["email"])
    return token