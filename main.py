from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import route_todo, route_auth
from schemas import SuccessMsg, CsrfSettings
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

app = FastAPI()

# route_todo.pyにあるrouter = APIRouter()のインスタンスを受け取っている
app.include_router(route_todo.router)
app.include_router(route_auth.router)
# RESTAPIへのアクセスを許可するドメインをホワイトリストへ追加。
origins = ['http://localhost:3000', 'http://localhost:3001']
# CORSの設定
app.add_middleware(
    CORSMiddleware,
    # 上記で作成したホワイトリストのを追加
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message
                }
    )

@app.get("/", response_model=SuccessMsg)
def root():
    return {"message": "welcome to Fast API"}