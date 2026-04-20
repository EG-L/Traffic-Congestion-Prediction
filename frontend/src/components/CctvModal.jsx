import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";
import { cctvAPI } from "../services/api";

export default function CctvModal({ road, onClose }) {
  const [cctvList, setCctvList] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const videoRef = useRef(null);
  const hlsRef = useRef(null);

  useEffect(() => {
    if (!road) return;
    setLoading(true);
    cctvAPI.getNearby(road.lat, road.lng).then((res) => {
      const list = res.data.data || [];
      setCctvList(list);
      if (list.length > 0) setSelected(list[0]);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [road]);

  useEffect(() => {
    if (!selected?.url || !videoRef.current) return;

    if (hlsRef.current) {
      hlsRef.current.destroy();
      hlsRef.current = null;
    }

    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(selected.url);
      hls.attachMedia(videoRef.current);
      hlsRef.current = hls;
    } else if (videoRef.current.canPlayType("application/vnd.apple.mpegurl")) {
      videoRef.current.src = selected.url;
    }

    return () => {
      hlsRef.current?.destroy();
    };
  }, [selected]);

  if (!road) return null;

  return (
    <div style={{
      position: "fixed", inset: 0,
      background: "rgba(0,0,0,0.6)",
      zIndex: 9999,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }} onClick={onClose}>
      <div style={{
        background: "white",
        borderRadius: "16px",
        width: "860px",
        maxWidth: "95vw",
        maxHeight: "90vh",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
      }} onClick={(e) => e.stopPropagation()}>

        {/* 헤더 */}
        <div style={{
          padding: "16px 20px",
          borderBottom: "1px solid #e5e7eb",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: "16px" }}>📹 {road.road_name} CCTV</div>
            <div style={{ fontSize: "12px", color: "#9ca3af", marginTop: "2px" }}>
              인근 CCTV {cctvList.length}개
            </div>
          </div>
          <button onClick={onClose} style={{
            background: "none", border: "none",
            fontSize: "22px", cursor: "pointer", color: "#6b7280",
          }}>✕</button>
        </div>

        <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
          {/* CCTV 목록 */}
          <div style={{
            width: "220px",
            borderRight: "1px solid #e5e7eb",
            overflowY: "auto",
            padding: "12px",
            display: "flex",
            flexDirection: "column",
            gap: "8px",
          }}>
            {loading ? (
              <div style={{ color: "#9ca3af", fontSize: "13px", padding: "8px" }}>로딩 중...</div>
            ) : cctvList.length === 0 ? (
              <div style={{ color: "#9ca3af", fontSize: "13px", padding: "8px" }}>인근 CCTV 없음</div>
            ) : (
              cctvList.map((cctv) => (
                <div key={cctv.cctv_id} onClick={() => setSelected(cctv)} style={{
                  padding: "10px 12px",
                  borderRadius: "8px",
                  cursor: "pointer",
                  background: selected?.cctv_id === cctv.cctv_id ? "#eff6ff" : "#f9fafb",
                  border: selected?.cctv_id === cctv.cctv_id ? "1px solid #3b82f6" : "1px solid transparent",
                }}>
                  <div style={{ fontSize: "13px", fontWeight: 600 }}>{cctv.name}</div>
                  <div style={{ fontSize: "11px", color: "#9ca3af", marginTop: "2px" }}>
                    {cctv.resolution}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* 영상 영역 */}
          <div style={{
            flex: 1,
            background: "#000",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "400px",
          }}>
            {!selected ? (
              <div style={{ color: "#6b7280", fontSize: "14px" }}>CCTV를 선택하세요</div>
            ) : !selected.url ? (
              <div style={{ color: "#6b7280", fontSize: "14px", textAlign: "center" }}>
                <div style={{ fontSize: "40px", marginBottom: "12px" }}>📡</div>
                <div>API 키를 등록하면</div>
                <div>실시간 영상이 표시됩니다</div>
                <div style={{ marginTop: "8px", fontSize: "12px", color: "#4b5563" }}>
                  {selected.name}
                </div>
              </div>
            ) : (
              <video
                ref={videoRef}
                autoPlay
                muted
                controls
                style={{ width: "100%", height: "100%", objectFit: "contain" }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
