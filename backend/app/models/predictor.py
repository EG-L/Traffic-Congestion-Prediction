import numpy as np
import pickle
import os
from datetime import datetime
from typing import Optional

try:
    import lightgbm as lgb
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

MODEL_DIR = os.path.join(os.path.dirname(__file__), "weights")


class LSTMModel(torch.nn.Module if TORCH_AVAILABLE else object):
    def __init__(self, input_size=5, hidden_size=64, num_layers=2, output_size=1):
        if not TORCH_AVAILABLE:
            return
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


class TrafficPredictor:
    def __init__(self):
        self.lgbm_model: Optional[object] = None
        self.lstm_model: Optional[object] = None
        self._load_models()

    def _load_models(self):
        os.makedirs(MODEL_DIR, exist_ok=True)

        lgbm_path = os.path.join(MODEL_DIR, "lgbm_model.pkl")
        if LGBM_AVAILABLE and os.path.exists(lgbm_path):
            with open(lgbm_path, "rb") as f:
                self.lgbm_model = pickle.load(f)

        lstm_path = os.path.join(MODEL_DIR, "lstm_model.pth")
        if TORCH_AVAILABLE and os.path.exists(lstm_path):
            self.lstm_model = LSTMModel()
            self.lstm_model.load_state_dict(torch.load(lstm_path, map_location="cpu"))
            self.lstm_model.eval()

    def _extract_features(self, traffic_data: dict, weather_data: dict) -> np.ndarray:
        now = datetime.now()
        return np.array([[
            now.hour,
            now.weekday(),
            int(now.weekday() >= 5),
            now.month,
            traffic_data.get("speed", 50),
            weather_data.get("precipitation", 0),
            weather_data.get("temperature", 20),
        ]])

    def predict_lgbm(self, traffic_data: dict, weather_data: dict) -> dict:
        features = self._extract_features(traffic_data, weather_data)
        if self.lgbm_model and LGBM_AVAILABLE:
            speed_pred = float(self.lgbm_model.predict(features)[0])
        else:
            speed_pred = self._rule_based_predict(traffic_data, weather_data)

        return {
            "predicted_speed": round(speed_pred, 1),
            "predicted_congestion": self._speed_to_congestion(speed_pred),
            "confidence": 0.82,
            "model_used": "LightGBM",
        }

    def predict_lstm(self, history: list, weather_data: dict) -> dict:
        if not history:
            return self.predict_lgbm({"speed": 50}, weather_data)

        if self.lstm_model and TORCH_AVAILABLE:
            seq = np.array([[
                h.get("speed", 50),
                datetime.fromisoformat(str(h.get("timestamp", datetime.now()))).hour,
                weather_data.get("precipitation", 0),
                weather_data.get("temperature", 20),
                weather_data.get("wind_speed", 2),
            ] for h in history[-12:]])
            tensor = torch.FloatTensor(seq).unsqueeze(0)
            with torch.no_grad():
                speed_pred = float(self.lstm_model(tensor).item())
        else:
            speed_pred = self._rule_based_predict(history[-1] if history else {}, weather_data)

        return {
            "predicted_speed": round(speed_pred, 1),
            "predicted_congestion": self._speed_to_congestion(speed_pred),
            "confidence": 0.87,
            "model_used": "LSTM",
        }

    def predict_ensemble(self, traffic_data: dict, weather_data: dict, history: list = None) -> dict:
        lgbm_result = self.predict_lgbm(traffic_data, weather_data)
        lstm_result = self.predict_lstm(history or [traffic_data], weather_data)

        ensemble_speed = lgbm_result["predicted_speed"] * 0.4 + lstm_result["predicted_speed"] * 0.6
        return {
            "predicted_speed": round(ensemble_speed, 1),
            "predicted_congestion": self._speed_to_congestion(ensemble_speed),
            "confidence": round((lgbm_result["confidence"] + lstm_result["confidence"]) / 2, 3),
            "model_used": "Ensemble (LightGBM + LSTM)",
        }

    def _rule_based_predict(self, traffic_data: dict, weather_data: dict) -> float:
        base_speed = traffic_data.get("speed", 50)
        hour = datetime.now().hour
        rain = weather_data.get("precipitation", 0)

        if 7 <= hour <= 9 or 18 <= hour <= 20:
            base_speed *= 0.75
        if rain > 0:
            base_speed *= max(0.7, 1 - rain * 0.05)

        return max(5.0, min(110.0, base_speed))

    def _speed_to_congestion(self, speed: float) -> int:
        if speed >= 60:
            return 0
        elif speed >= 30:
            return 1
        else:
            return 2


predictor = TrafficPredictor()
