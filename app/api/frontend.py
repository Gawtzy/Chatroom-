from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

@router.get("/")
async def get():
    return HTMLResponse(html)