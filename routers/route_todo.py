from fastapi import APIRouter, Response, Request, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from schemas import Todo, TodoBody,SuccessMsg
from database import db_create_todo, db_get_single_todo, db_get_todos, db_update_todo, db_delete_todo
from starlette.status import HTTP_201_CREATED
from typing import List
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()

# エンドポイントが返してくれるjsonのデータ型をresponse_model=Todoと定義
@router.post("/api/todo", response_model=Todo)
# エンドポイントにアクセスされた時の関数、引数としてClientからくるhttpのRequest,Response,dataを定義
async def create_todo(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    # auth_utilsで作成したメソッドの実行をしCSRFの検証とアップデートを実施、new_tokenを返す。
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers
    )
    todo = jsonable_encoder(data)
    # await:非同期処理（並行処理）対応のメソッドを呼び出す時に宣言する。
    res = await db_create_todo(todo)
    # FastAPIの成功した場合のステータスコードが200なので201に変えておく
    response.status_code = HTTP_201_CREATED
    # 新しく生成されたtokenでcookieの内容を書き換える
    response.set_cookie(
        key="access_token", value="Bearer {new_token}", httponly=True, samesite="none", secure=True
    )

    if res:
        return res
    raise HTTPException(
        status_code=404, detail="Create task failed."
    )

@router.get("/api/todo", response_model=List[Todo])
async def get_todos(request: Request):
    # verify_jwtでJWTの検証を行う
    # auth.verify_jwt(request)
    res = await db_get_todos()
    return res

@router.get("/api/todo/{id}", response_model=Todo)
async def get_single_todo(request: Request, response: Response, id: str):
    #JWTの検証と更新を実行。payloadは使用しないので、_で受け取る
    new_token, _ = auth.verify_update_jwt(request)
    res = await db_get_single_todo(id)
    # 生成されたnew_tokenをcookieへ書き換えておく
    response.set_cookie(
        key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True
    )
    if res:
        return res
    raise HTTPException(
        status_code=404, detail=f"Task of ID:{id} does not exist."
    )

@router.put("/api/todo/{id}", response_model=Todo)
async def uppate_todo(request: Request, response: Response, id: str, data:TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers
    )
    todo = jsonable_encoder(data)
    response.set_cookie(
        key="access_token", value="Bearer {new_token}", httponly=True, samesite="none", secure=True
    )
    res= await db_update_todo(id, todo)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail="Updata task failed."
    )

@router.delete("/api/todo/{id}", response_model=SuccessMsg)
async def delete_todo(request: Request, response: Response, id: str, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers
    )
    res = await db_delete_todo(id)
    response.set_cookie(
        key="access_token", value="Bearer {new_token}", httponly=True, samesite="none", secure=True
    )
    if res:
        return {"message": "Successfully deleted."}
    raise HTTPException(
        status_code=404, detail="Delete task failed."
    )