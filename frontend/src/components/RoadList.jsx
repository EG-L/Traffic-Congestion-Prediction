import CongestionBadge from "./CongestionBadge";

export default function RoadList({ roads, onSelect, selectedId }) {
  if (!roads.length) return (
    <div style={{ padding: "24px", textAlign: "center", color: "#9ca3af" }}>
      데이터 없음
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {roads.map((road) => (
        <div
          key={road.road_id}
          onClick={() => onSelect(road)}
          style={{
            background: selectedId === road.road_id ? "#eff6ff" : "white",
            border: selectedId === road.road_id ? "1px solid #3b82f6" : "1px solid #e5e7eb",
            borderRadius: "10px",
            padding: "12px 16px",
            cursor: "pointer",
            transition: "all 0.15s",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: "14px" }}>{road.road_name}</div>
              <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "2px" }}>
                현재 {road.current_speed} km/h → 예측 {road.predicted_speed} km/h
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "4px", alignItems: "flex-end" }}>
              <CongestionBadge level={road.current_congestion} size="sm" />
              <div style={{ fontSize: "10px", color: "#9ca3af" }}>
                예측 <CongestionBadge level={road.predicted_congestion} size="sm" />
              </div>
            </div>
          </div>
          <div style={{ fontSize: "11px", color: "#9ca3af", marginTop: "6px" }}>
            신뢰도 {Math.round(road.confidence * 100)}% · {road.model_used}
          </div>
        </div>
      ))}
    </div>
  );
}
