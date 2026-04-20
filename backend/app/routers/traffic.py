from fastapi import APIRouter
from app.services.traffic_service import fetch_realtime_traffic

router = APIRouter()


@router.get("/realtime")
async def get_realtime_traffic():
    data = await fetch_realtime_traffic()
    return {"success": True, "data": data, "count": len(data)}


@router.get("/realtime/{road_id}")
async def get_road_traffic(road_id: str):
    data = await fetch_realtime_traffic()
    road = next((r for r in data if r["road_id"] == road_id), None)
    if not road:
        return {"success": False, "message": "도로를 찾을 수 없습니다."}
    return {"success": True, "data": road}
