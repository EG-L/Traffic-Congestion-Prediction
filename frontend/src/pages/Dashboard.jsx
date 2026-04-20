import { useState } from "react";
import { useTrafficData } from "../hooks/useTrafficData";
import TrafficMap from "../components/TrafficMap";
import RoadList from "../components/RoadList";
import WeatherCard from "../components/WeatherCard";
import StatsBar from "../components/StatsBar";
import CongestionBadge from "../components/CongestionBadge";
import CctvModal from "../components/CctvModal";

export default function Dashboard() {
  const { roads, weather, loading, error, refetch, lastUpdated } = useTrafficData(30000);
  const [selectedRoad, setSelectedRoad] = useState(null);
  const [cctvRoad, setCctvRoad] = useState(null);

  return (
    <div style={{ minHeight: "100vh", background: "#f3f4f6", fontFamily: "Pretendard, sans-serif" }}>
      {/* 헤더 */}
      <header style={{
        background: "white",
        borderBottom: "1px solid #e5e7eb",
        padding: "0 24px",
        height: "60px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontSize: "22px" }}>🚦</span>
          <span style={{ fontWeight: 700, fontSize: "18px" }}>실시간 교통 혼잡 예측</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {lastUpdated && (
            <span style={{ fontSize: "12px", color: "#9ca3af" }}>
              마지막 업데이트: {lastUpdated.toLocaleTimeString("ko-KR")}
            </span>
          )}
          <button
            onClick={refetch}
            style={{
              background: "#3b82f6",
              color: "white",
              border: "none",
              borderRadius: "8px",
              padding: "8px 16px",
              fontSize: "13px",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            새로고침
          </button>
        </div>
      </header>

      <main style={{ padding: "20px 24px", maxWidth: "1400px", margin: "0 auto" }}>
        {error && (
          <div style={{
            background: "#fee2e2",
            color: "#ef4444",
            padding: "12px 16px",
            borderRadius: "8px",
            marginBottom: "16px",
            fontSize: "14px",
          }}>
            {error}
          </div>
        )}

        <div style={{ marginBottom: "16px" }}>
          <WeatherCard weather={weather} />
        </div>

        {!loading && (
          <div style={{ marginBottom: "16px" }}>
            <StatsBar roads={roads} />
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: "16px" }}>
          {/* 지도 */}
          <div style={{ background: "white", borderRadius: "12px", overflow: "hidden", height: "520px", boxShadow: "0 1px 4px rgba(0,0,0,0.1)" }}>
            {loading ? (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "#9ca3af" }}>
                데이터 로딩 중...
              </div>
            ) : (
              <TrafficMap
                roads={roads}
                onSelect={setSelectedRoad}
                onCctvOpen={setCctvRoad}
              />
            )}
          </div>

          {/* 사이드바 */}
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {selectedRoad && (
              <div style={{ background: "white", borderRadius: "12px", padding: "16px", boxShadow: "0 1px 4px rgba(0,0,0,0.1)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                  <div style={{ fontWeight: 700, fontSize: "15px" }}>
                    📍 {selectedRoad.road_name}
                  </div>
                  <button
                    onClick={() => setCctvRoad(selectedRoad)}
                    style={{
                      background: "#1d4ed8",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      padding: "5px 10px",
                      fontSize: "12px",
                      cursor: "pointer",
                      fontWeight: 600,
                      whiteSpace: "nowrap",
                    }}
                  >
                    📹 CCTV
                  </button>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
                  <InfoItem label="현재 속도" value={`${selectedRoad.current_speed} km/h`} />
                  <InfoItem label="예측 속도" value={`${selectedRoad.predicted_speed} km/h`} />
                  <InfoItem label="현재 상태" value={<CongestionBadge level={selectedRoad.current_congestion} size="sm" />} />
                  <InfoItem label="30분 후 예측" value={<CongestionBadge level={selectedRoad.predicted_congestion} size="sm" />} />
                </div>
                <div style={{ fontSize: "12px", color: "#9ca3af" }}>
                  신뢰도 {Math.round(selectedRoad.confidence * 100)}% · {selectedRoad.model_used}
                </div>
              </div>
            )}

            <div style={{
              background: "white",
              borderRadius: "12px",
              padding: "16px",
              boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
              flex: 1,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}>
              <div style={{ fontWeight: 700, marginBottom: "12px", fontSize: "15px" }}>도로 목록</div>
              <div style={{ overflowY: "auto", flex: 1 }}>
                {loading ? (
                  <div style={{ textAlign: "center", color: "#9ca3af", padding: "24px" }}>로딩 중...</div>
                ) : (
                  <RoadList
                    roads={roads}
                    onSelect={setSelectedRoad}
                    selectedId={selectedRoad?.road_id}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      <CctvModal road={cctvRoad} onClose={() => setCctvRoad(null)} />
    </div>
  );
}

function InfoItem({ label, value }) {
  return (
    <div style={{ background: "#f9fafb", borderRadius: "8px", padding: "8px 10px" }}>
      <div style={{ fontSize: "11px", color: "#9ca3af", marginBottom: "2px" }}>{label}</div>
      <div style={{ fontSize: "13px", fontWeight: 600 }}>{value}</div>
    </div>
  );
}
