from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from schemas import Todo, TodoBody,SuccessMsg
from database import db_create_todo, db_get_single_todo, db_get_todos, db_update_todo, db_delete_todo
from starlette.status import HTTP_201_CREATED
from typing import List

router = APIRouter()

# エンドポイントが返してくれるjsonのデータ型をresponse_model=Todoと定義
@router.post("/api/todo", response_model=Todo)
# エンドポイントにアクセスされた時の関数、引数としてClientからくるhttpのRequest,Response,dataを定義
async def create_todo(request: Request, response: Response, data: TodoBody):
    todo = jsonable_encoder(data)
    # await:非同期処理（並行処理）対応のメソッドを呼び出す時に宣言する。
    res = await db_create_todo(todo)
    # FastAPIの成功した場合のステータスコードが200なので201に変えておく
    response.status_code = HTTP_201_CREATED
    if res:
        return res
    raise HTTPException(
        status_code=404, detail="Create task failed."
    )

@router.get("/api/todo", response_model=List[Todo])
async def get_todos():
    res = await db_get_todos()
    return res

@router.get("/api/todo/{id}", response_model=Todo)
async def get_single_todo(id: str):
    res = await db_get_single_todo(id)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail=f"Task of ID:{id} does not exist."
    )

@router.put("/api/todo/{id}", response_model=Todo)
async def uppate_todo(id: str, data:TodoBody):
    todo = jsonable_encoder(data)
    res= await db_update_todo(id, todo)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail="Updata task failed."
    )

@router.delete("/api/todo/{id}", response_model=SuccessMsg)
async def delete_todo(id: str):
    res = await db_delete_todo(id)
    if res:
        return {"message": "Successfully deleted."}
    raise HTTPException(
        status_code=404, detail="Delete task failed."
    )