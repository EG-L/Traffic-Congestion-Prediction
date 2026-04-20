from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TrafficData(BaseModel):
    road_id: str
    road_name: str
    speed: float
    congestion_level: int  # 0:원활 1:서행 2:정체
    timestamp: datetime
    lat: float
    lng: float


class WeatherData(BaseModel):
    temperature: float
    precipitation: float
    wind_speed: float
    weather_code: int
    timestamp: datetime


class PredictionRequest(BaseModel):
    road_id: str
    hours_ahead: int = 1


class PredictionResult(BaseModel):
    road_id: str
    road_name: str
    current_congestion: int
    predicted_congestion: int
    predicted_speed: float
    confidence: float
    prediction_time: datetime
    model_used: str
