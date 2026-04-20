import os
import httpx
from config import prop


async def fetch_cctv_nearby(lat: float, lng: float, radius: float = 0.15) -> list:
    url = os.environ.get(prop['cctv']['base_url'])
    params = {
        "key": os.environ.get(prop['cctv']['api_key']),
        "type": "ex",        # 고속도로
        "cctvType": "1",     # 실시간 스트리밍(HLS)
        "minX": lng - radius,
        "maxX": lng + radius,
        "minY": lat - radius,
        "maxY": lat + radius,
        "getType": "json",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return _parse_cctv(response.json())
        except Exception:
            return _get_mock_cctv(lat, lng)


def _parse_cctv(raw: dict) -> list:
    items = raw.get("response", {}).get("data", [])
    if isinstance(items, dict):
        items = [items]
    result = []
    for item in items:
        result.append({
            "cctv_id": item.get("roadsectionid", ""),
            "name": item.get("cctvname", ""),
            "url": item.get("cctvurl", ""),
            "lat": float(item.get("coordy", 0)),
            "lng": float(item.get("coordx", 0)),
            "resolution": item.get("cctvresolution", ""),
            "format": item.get("cctvformat", "HLS"),
        })
    return result


def _get_mock_cctv(lat: float, lng: float) -> list:
    import random
    names = ["상행 1km", "하행 2km", "분기점", "진입로", "터널 입구"]
    return [
        {
            "cctv_id": f"MOCK_{i}",
            "name": f"고속도로 CCTV {names[i]}",
            "url": "",
            "lat": lat + random.uniform(-0.05, 0.05),
            "lng": lng + random.uniform(-0.05, 0.05),
            "resolution": "1920*1080",
            "format": "HLS",
        }
        for i in range(min(3, len(names)))
    ]
