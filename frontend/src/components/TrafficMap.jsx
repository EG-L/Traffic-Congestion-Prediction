import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import CongestionBadge from "./CongestionBadge";

const CONGESTION_COLORS = { 0: "#22c55e", 1: "#f59e0b", 2: "#ef4444" };

export default function TrafficMap({ roads, onSelect, onCctvOpen }) {
  return (
    <MapContainer
      center={[37.5665, 126.978]}
      zoom={11}
      style={{ height: "100%", width: "100%", borderRadius: "12px" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {roads.map((road) => (
        <CircleMarker
          key={road.road_id}
          center={[road.lat, road.lng]}
          radius={14}
          pathOptions={{
            color: CONGESTION_COLORS[road.current_congestion] ?? "#6b7280",
            fillColor: CONGESTION_COLORS[road.current_congestion] ?? "#6b7280",
            fillOpacity: 0.7,
            weight: 2,
          }}
          eventHandlers={{ click: () => onSelect(road) }}
        >
          <Popup>
            <div style={{ minWidth: "190px" }}>
              <div style={{ fontWeight: 700, marginBottom: "8px" }}>{road.road_name}</div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                <span>현재 상태</span>
                <CongestionBadge level={road.current_congestion} size="sm" />
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <span>30분 후 예측</span>
                <CongestionBadge level={road.predicted_congestion} size="sm" />
              </div>
              <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: "10px" }}>
                현재 {road.current_speed} km/h → 예측 {road.predicted_speed} km/h
              </div>
              <button
                onClick={() => onCctvOpen(road)}
                style={{
                  width: "100%",
                  background: "#1d4ed8",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  padding: "7px 0",
                  fontSize: "13px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                📹 CCTV 보기
              </button>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
