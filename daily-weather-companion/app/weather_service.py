"""Weather forecast and Air Quality tools using Open-Meteo & Open Air Quality APIs."""

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

# Quick lookup coordinates for major Indonesian cities
CITY_COORDINATES: Dict[str, tuple[float, float, str]] = {
    "jakarta": (-6.2088, 106.8456, "Asia/Jakarta"),
    "bandung": (-6.9175, 107.6191, "Asia/Jakarta"),
    "surabaya": (-7.2575, 112.7521, "Asia/Jakarta"),
    "yogyakarta": (-7.7956, 110.3695, "Asia/Jakarta"),
    "semarang": (-6.9667, 110.4167, "Asia/Jakarta"),
    "medan": (3.5952, 98.6722, "Asia/Jakarta"),
    "denpasar": (-8.6705, 115.2126, "Asia/Makassar"),
    "bali": (-8.4095, 115.1889, "Asia/Makassar"),
    "makassar": (-5.1477, 119.4327, "Asia/Makassar"),
    "balikpapan": (-1.2379, 116.8529, "Asia/Makassar"),
    "jayapura": (-2.5337, 140.7181, "Asia/Jayapura"),
}

WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky (Cerah)",
    1: "Mainly clear (Cerah Berawan)",
    2: "Partly cloudy (Berawan)",
    3: "Overcast (Mendung)",
    45: "Fog (Kabut)",
    48: "Depositing rime fog",
    51: "Light drizzle (Gerimis Ringan)",
    53: "Moderate drizzle (Gerimis)",
    55: "Dense drizzle (Gerimis Lebat)",
    61: "Slight rain (Hujan Ringan)",
    63: "Moderate rain (Hujan Sedang)",
    65: "Heavy rain (Hujan Lebat)",
    80: "Slight rain showers (Hujan Lokal)",
    81: "Moderate rain showers",
    82: "Violent rain showers (Hujan Lebat Disertai Angin)",
    95: "Thunderstorm (Hujan Badai / Petir)",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _get_aqi_category(us_aqi: int) -> tuple[str, str]:
    """Get Indonesian description and health recommendation based on US AQI standard."""
    if us_aqi <= 50:
        return "Baik (Good)", "Kualitas udara sangat baik. Aman untuk semua aktivitas luar ruangan."
    elif us_aqi <= 100:
        return "Sedang (Moderate)", "Kualitas udara dapat diterima. Kelompok sangat sensitif perlu berhati-hati."
    elif us_aqi <= 150:
        return "Tidak Sehat bagi Kelompok Sensitif (Unhealthy for Sensitive Groups)", "Gunakan masker jika berkendara motor atau memiliki riwayat asma/alergi."
    elif us_aqi <= 200:
        return "Tidak Sehat (Unhealthy)", "Disarankan memakai masker N95/KF94 saat berada di luar ruangan atau commuting."
    elif us_aqi <= 300:
        return "Sangat Tidak Sehat (Very Unhealthy)", "Hindari aktivitas fisik berat di luar ruangan. Wajib gunakan masker berfilter."
    else:
        return "Berbahaya (Hazardous)", "Peringatan darurat: Kualitas udara berbahaya. Tetap di dalam ruangan."


def resolve_location(
    city_or_location: str, latitude: Optional[float], longitude: Optional[float]
) -> Optional[tuple[float, float, str]]:
    """Explicit coordinates win, else the built-in city table. None if the city is unknown."""
    if latitude is not None and longitude is not None:
        return latitude, longitude, "Asia/Jakarta"
    return CITY_COORDINATES.get(city_or_location.lower().strip())


def unknown_location_error(city_or_location: str) -> Dict[str, Any]:
    return {
        "error": f"Unknown location '{city_or_location}'. Retry with explicit latitude and longitude.",
        "known_cities": sorted(CITY_COORDINATES),
    }


def fetch_hourly_weather(
    city_or_location: str = "Jakarta",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """Fetch live current weather and next 12-hour hourly forecast (rain probability, temperature, condition).

    Args:
        city_or_location: Name of the city (e.g. 'Jakarta', 'Bandung', 'Surabaya', 'Denpasar', 'Medan').
        latitude: Optional explicit latitude. If omitted, looked up from city name. Required for cities outside the built-in list.
        longitude: Optional explicit longitude. If omitted, looked up from city name. Required for cities outside the built-in list.

    Returns:
        A dictionary containing current weather, condition text, and the hourly forecast for the next 12 hours.
    """
    location = resolve_location(city_or_location, latitude, longitude)
    if location is None:
        return unknown_location_error(city_or_location)
    lat, lon, tz = location

    encoded_tz = urllib.parse.quote(tz)
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
        f"&hourly=temperature_2m,precipitation_probability,weather_code"
        f"&timezone={encoded_tz}&forecast_days=2"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "JasHujan-DailyWeatherCompanion/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        raw_data = json.loads(response.read().decode("utf-8"))

    current = raw_data.get("current", {})
    weather_code = current.get("weather_code", 0)
    condition_desc = WMO_WEATHER_CODES.get(weather_code, f"Weather code {weather_code}")

    hourly_raw = raw_data.get("hourly", {})
    times = hourly_raw.get("time", [])
    temps = hourly_raw.get("temperature_2m", [])
    rain_probs = hourly_raw.get("precipitation_probability", [])
    codes = hourly_raw.get("weather_code", [])

    current_time_str = current.get("time", "")
    start_idx = 0
    for idx, t in enumerate(times):
        if t >= current_time_str:
            start_idx = idx
            break

    hourly_forecast = []
    for i in range(start_idx, min(start_idx + 12, len(times))):
        code_val = codes[i] if i < len(codes) else 0
        hourly_forecast.append({
            "time": times[i],
            "temperature_celsius": temps[i] if i < len(temps) else None,
            "rain_probability_pct": rain_probs[i] if i < len(rain_probs) else 0,
            "condition": WMO_WEATHER_CODES.get(code_val, f"Code {code_val}"),
        })

    return {
        "location": city_or_location,
        "latitude": lat,
        "longitude": lon,
        "timezone": tz,
        "current_weather": {
            "time": current.get("time"),
            "temperature_celsius": current.get("temperature_2m"),
            "feels_like_celsius": current.get("apparent_temperature"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "condition": condition_desc,
        },
        "next_12_hours_forecast": hourly_forecast,
    }


def fetch_air_quality(
    city_or_location: str = "Jakarta",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """Fetch real-time air quality index (AQI), PM2.5, PM10, and health advice for Indonesian locations.

    Args:
        city_or_location: Name of the city (e.g. 'Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Denpasar').
        latitude: Optional latitude. If omitted, looked up from city name.
        longitude: Optional longitude. If omitted, looked up from city name.

    Returns:
        A dictionary with live AQI indices, particulate matter (PM2.5, PM10), pollution category, and mask/health recommendations.
    """
    location = resolve_location(city_or_location, latitude, longitude)
    if location is None:
        return unknown_location_error(city_or_location)
    lat, lon, tz = location

    encoded_tz = urllib.parse.quote(tz)
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        f"&current=us_aqi,european_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone"
        f"&timezone={encoded_tz}"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "JasHujan-DailyWeatherCompanion/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        raw_data = json.loads(response.read().decode("utf-8"))

    current = raw_data.get("current", {})
    us_aqi = int(current.get("us_aqi") or 0)
    category_id, health_advice = _get_aqi_category(us_aqi)

    return {
        "location": city_or_location,
        "latitude": lat,
        "longitude": lon,
        "timezone": tz,
        "air_quality": {
            "time": current.get("time"),
            "us_aqi": us_aqi,
            "european_aqi": current.get("european_aqi"),
            "category": category_id,
            "pm2_5_ug_m3": current.get("pm2_5"),
            "pm10_ug_m3": current.get("pm10"),
            "ozone_ug_m3": current.get("ozone"),
            "mask_recommended": us_aqi > 100,
            "health_advice": health_advice,
        },
    }
