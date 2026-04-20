const CONGESTION_CONFIG = {
  0: { label: "원활", color: "#22c55e", bg: "#dcfce7" },
  1: { label: "서행", color: "#f59e0b", bg: "#fef3c7" },
  2: { label: "정체", color: "#ef4444", bg: "#fee2e2" },
};

export default function CongestionBadge({ level, size = "md" }) {
  const config = CONGESTION_CONFIG[level] ?? CONGESTION_CONFIG[0];
  const padding = size === "sm" ? "2px 8px" : "4px 12px";
  const fontSize = size === "sm" ? "12px" : "14px";

  return (
    <span
      style={{
        backgroundColor: config.bg,
        color: config.color,
        padding,
        borderRadius: "999px",
        fontSize,
        fontWeight: 600,
        border: `1px solid ${config.color}`,
      }}
    >
      {config.label}
    </span>
  );
}
