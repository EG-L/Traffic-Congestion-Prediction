from fastapi import APIRouter
from app.services.weather_service import fetch_current_weather

router = APIRouter()


@router.get("/current")
async def get_current_weather(nx: int = 60, ny: int = 127):
    data = await fetch_current_weather(nx, ny)
    return {"success": True, "data": data}
