from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "./index.html",
        {"request": request, "title": "콜렉터 북북이"},
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    return templates.TemplateResponse(
        "./index.html",
        {"request": request, "title": "콜렉터 북북이", "keyword": q},
    )

@app.on_event("startup")
def on_app_start():
    print("hello server")
    mongodb.connect()

@app.on_event("shutdown")
def on_app_shutdown():
    print("goodbye server")
    mongodb.close()