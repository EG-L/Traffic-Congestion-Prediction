export default function StatsBar({ roads }) {
  const total = roads.length;
  const smooth = roads.filter((r) => r.current_congestion === 0).length;
  const slow = roads.filter((r) => r.current_congestion === 1).length;
  const jam = roads.filter((r) => r.current_congestion === 2).length;

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(4, 1fr)",
      gap: "12px",
    }}>
      <StatCard label="모니터링 도로" value={total} color="#3b82f6" />
      <StatCard label="원활" value={smooth} color="#22c55e" />
      <StatCard label="서행" value={slow} color="#f59e0b" />
      <StatCard label="정체" value={jam} color="#ef4444" />
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div style={{
      background: "white",
      borderRadius: "12px",
      padding: "16px",
      boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
      borderTop: `3px solid ${color}`,
    }}>
      <div style={{ fontSize: "24px", fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "4px" }}>{label}</div>
    </div>
  );
}
