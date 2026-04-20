import os
import httpx
from datetime import datetime
from config import prop


async def fetch_current_weather(nx: int = 60, ny: int = 127) -> dict:
    url = f"{os.environ.get(prop['weather']['base_url'])}/getUltraSrtNcst"
    now = datetime.now()
    params = {
        "serviceKey": os.environ.get(prop['weather']['api_key']),
        "numOfRows": 10,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": now.strftime("%Y%m%d"),
        "base_time": f"{now.hour:02d}00",
        "nx": nx,
        "ny": ny,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return _parse_weather(response.json())
        except Exception:
            return _get_mock_weather()


def _parse_weather(raw: dict) -> dict:
    items = raw.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    weather = {"temperature": 20.0, "precipitation": 0.0, "wind_speed": 2.0, "weather_code": 0}
    for item in items:
        category = item.get("category", "")
        value = float(item.get("obsrValue", 0))
        if category == "T1H":
            weather["temperature"] = value
        elif category == "RN1":
            weather["precipitation"] = value
        elif category == "WSD":
            weather["wind_speed"] = value
        elif category == "PTY":
            weather["weather_code"] = int(value)
    weather["timestamp"] = datetime.now()
    return weather


def _get_mock_weather() -> dict:
    import random
    return {
        "temperature": round(random.uniform(5, 35), 1),
        "precipitation": round(random.uniform(0, 5), 1),
        "wind_speed": round(random.uniform(0, 10), 1),
        "weather_code": random.choice([0, 0, 0, 1, 2]),
        "timestamp": datetime.now(),
    }
