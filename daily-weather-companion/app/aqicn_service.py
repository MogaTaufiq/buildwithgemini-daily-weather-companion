"""AQICN Geo Feed Air Quality Tool."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict


def _get_aqi_category_indonesian(aqi: int) -> str:
    """Map AQI value to official Indonesian category label."""
    if aqi <= 50:
        return "Baik"
    elif aqi <= 100:
        return "Sedang"
    elif aqi <= 150:
        return "Tidak Sehat untuk Kelompok Sensitif"
    elif aqi <= 200:
        return "Tidak Sehat"
    elif aqi <= 300:
        return "Sangat Tidak Sehat"
    else:
        return "Berbahaya"


def get_air_quality(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch real-time air quality data for given coordinates using the AQICN geo feed endpoint.

    Args:
        lat: Latitude of the location (e.g., -6.2088 for Jakarta).
        lon: Longitude of the location (e.g., 106.8456 for Jakarta).

    Returns:
        A dictionary containing AQI, dominant pollutant, PM2.5, nearest station name, and Indonesian category label.
    """
    token = os.environ.get("AQICN_TOKEN", "").strip()
    if not token or token == "PASTE_AQICN_TOKEN":
        # Fallback to demo or inform caller if not configured
        token = "demo"

    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={urllib.parse.quote(token)}"
    req = urllib.request.Request(url, headers={"User-Agent": "JasHujan-DailyWeatherCompanion/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"Failed to connect to AQICN: {str(e)}"}

    if payload.get("status") != "ok":
        return {
            "error": payload.get("data", "Unknown AQICN API error"),
            "status": payload.get("status"),
        }

    data = payload.get("data", {})
    aqi_val = data.get("aqi")
    if isinstance(aqi_val, (int, float)):
        aqi_int = int(aqi_val)
        category = _get_aqi_category_indonesian(aqi_int)
    else:
        aqi_int = None
        category = "Data Tidak Tersedia"

    dominant_pollutant = data.get("dominentpol", "unknown")
    iaqi = data.get("iaqi", {})
    pm25_val = iaqi.get("pm25", {}).get("v")
    station_name = data.get("city", {}).get("name", "Unknown Station")

    return {
        "aqi": aqi_int,
        "dominant_pollutant": dominant_pollutant,
        "pm2_5": pm25_val,
        "nearest_station_name": station_name,
        "category_label": category,
        "coordinates": {"latitude": lat, "longitude": lon},
    }
