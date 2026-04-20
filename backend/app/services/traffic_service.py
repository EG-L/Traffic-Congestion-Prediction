import os
import httpx
from datetime import datetime
from typing import List
from config import prop


async def fetch_realtime_traffic(road_ids: List[str] = None) -> List[dict]:
    url = f"{os.environ.get(prop['traffic']['base_url'])}/trafficInfo"
    params = {
        "key": os.environ.get(prop['traffic']['api_key']),
        "type": "json",
        "getType": "1",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return _parse_traffic_data(response.json())
        except Exception:
            return _get_mock_traffic_data()


def _parse_traffic_data(raw: dict) -> List[dict]:
    items = raw.get("body", {}).get("items", {}).get("item", [])
    if isinstance(items, dict):
        items = [items]
    result = []
    for item in items:
        result.append({
            "road_id": item.get("linkId", ""),
            "road_name": item.get("roadName", ""),
            "speed": float(item.get("speed", 0)),
            "congestion_level": _speed_to_congestion(float(item.get("speed", 0))),
            "timestamp": datetime.now(),
            "lat": float(item.get("startLat", 37.5665)),
            "lng": float(item.get("startLng", 126.9780)),
        })
    return result


def _speed_to_congestion(speed: float) -> int:
    if speed >= 60:
        return 0
    elif speed >= 30:
        return 1
    else:
        return 2


def _get_mock_traffic_data() -> List[dict]:
    import random
    roads = [
        ("R001", "강남대로", 37.4979, 127.0276),
        ("R002", "테헤란로", 37.5087, 127.0632),
        ("R003", "올림픽대로", 37.5200, 127.1200),
        ("R004", "경부고속도로", 37.4500, 127.0400),
        ("R005", "서울외곽순환도로", 37.6000, 126.9000),
        ("R006", "강변북로", 37.5400, 126.9700),
        ("R007", "동부간선도로", 37.5800, 127.0800),
        ("R008", "서부간선도로", 37.5200, 126.8700),
    ]
    result = []
    for road_id, road_name, lat, lng in roads:
        speed = random.uniform(10, 100)
        result.append({
            "road_id": road_id,
            "road_name": road_name,
            "speed": round(speed, 1),
            "congestion_level": _speed_to_congestion(speed),
            "timestamp": datetime.now(),
            "lat": lat + random.uniform(-0.01, 0.01),
            "lng": lng + random.uniform(-0.01, 0.01),
        })
    return result
