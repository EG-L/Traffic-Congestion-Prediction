from fastapi import APIRouter
from app.services.cctv_service import fetch_cctv_nearby

router = APIRouter()


@router.get("/nearby")
async def get_nearby_cctv(lat: float, lng: float, radius: float = 0.15):
    data = await fetch_cctv_nearby(lat, lng, radius)
    return {"success": True, "data": data, "count": len(data)}
