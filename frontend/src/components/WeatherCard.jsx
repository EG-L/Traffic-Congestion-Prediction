const WEATHER_LABELS = { 0: "맑음", 1: "비", 2: "비/눈", 3: "눈", 4: "소나기" };
const WEATHER_ICONS = { 0: "☀️", 1: "🌧️", 2: "🌨️", 3: "❄️", 4: "⛈️" };

export default function WeatherCard({ weather }) {
  if (!weather) return null;

  return (
    <div style={{
      background: "white",
      borderRadius: "12px",
      padding: "16px",
      boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
      display: "flex",
      gap: "16px",
      alignItems: "center",
      flexWrap: "wrap",
    }}>
      <div style={{ fontSize: "28px" }}>
        {WEATHER_ICONS[weather.weather_code] ?? "☀️"}
      </div>
      <div>
        <div style={{ fontSize: "12px", color: "#6b7280" }}>현재 날씨</div>
        <div style={{ fontWeight: 700, fontSize: "16px" }}>
          {WEATHER_LABELS[weather.weather_code] ?? "맑음"}
        </div>
      </div>
      <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
        <Stat label="기온" value={`${weather.temperature}°C`} />
        <Stat label="강수량" value={`${weather.precipitation}mm`} />
        <Stat label="풍속" value={`${weather.wind_speed}m/s`} />
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div>
      <div style={{ fontSize: "11px", color: "#9ca3af" }}>{label}</div>
      <div style={{ fontSize: "14px", fontWeight: 600 }}>{value}</div>
    </div>
  );
}
