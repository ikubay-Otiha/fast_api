from fastapi import FastAPI
from routers import route_todo, route_auth
from schemas import SuccessMsg
import uvicorn

app = FastAPI()
# route_todo.pyにあるrouter = APIRouter()のインスタンスを受け取っている
app.include_router(route_todo.router)
app.include_router(route_auth.router)

@app.get("/", response_model=SuccessMsg)
def root():
    return {"message": "welcome to Fast API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)