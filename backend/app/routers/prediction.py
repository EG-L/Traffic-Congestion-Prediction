from fastapi import APIRouter
from app.services.traffic_service import fetch_realtime_traffic
from app.services.weather_service import fetch_current_weather
from app.models.predictor import predictor
from datetime import datetime

router = APIRouter()


@router.get("/all")
async def predict_all_roads():
    traffic_list = await fetch_realtime_traffic()
    weather = await fetch_current_weather()

    results = []
    for road in traffic_list:
        prediction = predictor.predict_ensemble(road, weather, history=[road])
        results.append({
            "road_id": road["road_id"],
            "road_name": road["road_name"],
            "lat": road["lat"],
            "lng": road["lng"],
            "current_speed": road["speed"],
            "current_congestion": road["congestion_level"],
            "predicted_speed": prediction["predicted_speed"],
            "predicted_congestion": prediction["predicted_congestion"],
            "confidence": prediction["confidence"],
            "model_used": prediction["model_used"],
            "prediction_time": datetime.now().isoformat(),
        })

    return {"success": True, "data": results, "weather": weather}


@router.get("/{road_id}")
async def predict_road(road_id: str):
    traffic_list = await fetch_realtime_traffic()
    weather = await fetch_current_weather()

    road = next((r for r in traffic_list if r["road_id"] == road_id), None)
    if not road:
        return {"success": False, "message": "도로를 찾을 수 없습니다."}

    prediction = predictor.predict_ensemble(road, weather, history=[road])
    return {
        "success": True,
        "data": {
            **road,
            **prediction,
            "weather": weather,
            "prediction_time": datetime.now().isoformat(),
        }
    }
