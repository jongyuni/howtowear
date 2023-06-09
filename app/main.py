from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb
from app.models.book import BookModel
from app.book_scraper import NaverBookScraper

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # book = BookModel(keyword="파이썬", publisher="public", price=1000, image="test.png")
    # await mongodb.engine.save(book)
    return templates.TemplateResponse(
        "./index.html",
        {"request": request, "title": "콜렉터 북북이"},
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    keyword = q

    # 검색어가 없다면 사용자에게 검색어 입력을 요구
    if not keyword:
        return templates.TemplateResponse(
            "./index.html",
            {"request": request, "title": "콜렉터 북북이"},
        )

    # 이미 db에 해당 키워드가 있는지 확인
    if await mongodb.engine.find_one(BookModel, BookModel.keyword==keyword):
        books = await mongodb.engine.find(BookModel, BookModel.keyword==keyword)
        return templates.TemplateResponse(
            "./index.html",
            {"request": request, "title": "콜렉터 북북이", "books": books},
        )

    naver_book_scraper = NaverBookScraper()
    books = await naver_book_scraper.search(keyword, 10)
    book_models = []

    for book in books:
        book_model = BookModel(
            keyword=keyword,
            publisher=book["publisher"],
            price=book["discount"],
            image=book["image"],
        )
        book_models.append(book_model)

    await mongodb.engine.save_all(book_models)

    return templates.TemplateResponse(
        "./index.html",
        {"request": request, "title": "콜렉터 북북이", "books": books},
    )


@app.on_event("startup")
def on_app_start():
    print("hello server")
    mongodb.connect()


@app.on_event("shutdown")
def on_app_shutdown():
    print("goodbye server")
    mongodb.close()
