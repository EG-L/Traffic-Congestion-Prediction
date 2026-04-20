import { useState, useEffect, useCallback } from "react";
import { predictionAPI, weatherAPI } from "../services/api";

export function useTrafficData(refreshInterval = 30000) {
  const [roads, setRoads] = useState([]);
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [predRes, weatherRes] = await Promise.all([
        predictionAPI.getAll(),
        weatherAPI.getCurrent(),
      ]);
      setRoads(predRes.data.data || []);
      setWeather(predRes.data.weather || weatherRes.data.data);
      setLastUpdated(new Date());
    } catch (err) {
      setError("데이터를 불러오는 데 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, refreshInterval);
    return () => clearInterval(timer);
  }, [fetchData, refreshInterval]);

  return { roads, weather, loading, error, refetch: fetchData, lastUpdated };
}
