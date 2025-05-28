"""
메인 페이지 라우터
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def main():
    """메인 페이지"""
    with open("web/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
