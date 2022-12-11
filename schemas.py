from pydantic import BaseModel
from typing import Optional

# responseで帰ってくるjsonデータをstr型にする
class Todo(BaseModel):
    id: str
    title: str
    description: str

class TodoBody(BaseModel):
    # 変数の型を定義する。
    title: str
    description: str

class SuccessMsg(BaseModel):
    message: str

class UserBody(BaseModel):
    email: str
    password: str

class UserInfo(BaseModel):
    id: Optional[str] = None
    email: str