"""OpenUV Real-Time & Forecast UV Index Tool with 1-Hour Caching."""

import datetime
import json
import os
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional

# In-memory cache: (rounded_lat, rounded_lon) -> (timestamp, data)
_UV_CACHE: Dict[tuple[float, float], tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour cache


def get_uv_index(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch current UV index, maximum UV today with peak time, and hours with UV >= 6 in Asia/Jakarta time.

    Results are cached for 1 hour to respect daily request limits.

    Args:
        lat: Latitude of the location (e.g., -6.2088 for Jakarta).
        lon: Longitude of the location (e.g., 106.8456 for Jakarta).

    Returns:
        A dictionary containing current_uv, max_uv_today, max_uv_time_wib, and hours_uv_ge_6 in Asia/Jakarta time.
    """
    api_key = os.environ.get("OPENUV_API_KEY", "").strip()
    cache_key = (round(lat, 2), round(lon, 2))
    current_time = time.time()

    # Check cache first
    if cache_key in _UV_CACHE:
        cached_ts, cached_result = _UV_CACHE[cache_key]
        if current_time - cached_ts < CACHE_TTL_SECONDS:
            return {**cached_result, "cached": True}

    if not api_key or api_key == "PASTE_OPENUV_KEY":
        return {
            "error": "OPENUV_API_KEY is not configured in .env. Please set a valid OpenUV API key.",
            "current_uv": None,
            "max_uv_today": None,
            "max_uv_time_wib": None,
            "hours_uv_ge_6": [],
        }

    tz = ZoneInfo("Asia/Jakarta")
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json",
        "User-Agent": "Sedia-DailyWeatherCompanion/1.0",
    }

    # 1. Fetch current UV and daily max from /api/v1/uv
    uv_url = f"https://api.openuv.io/api/v1/uv?lat={lat}&lng={lon}"
    req_uv = urllib.request.Request(uv_url, headers=headers)

    try:
        with urllib.request.urlopen(req_uv, timeout=10) as resp:
            uv_data = json.loads(resp.read().decode("utf-8")).get("result", {})
    except Exception as e:
        return {"error": f"Failed to fetch OpenUV data: {str(e)}"}

    current_uv = uv_data.get("uv")
    max_uv = uv_data.get("uv_max")
    max_uv_time_utc = uv_data.get("uv_max_time")

    max_uv_time_wib = None
    if max_uv_time_utc:
        try:
            dt_utc = datetime.datetime.fromisoformat(max_uv_time_utc.replace("Z", "+00:00"))
            dt_wib = dt_utc.astimezone(tz)
            max_uv_time_wib = dt_wib.strftime("%H:%M WIB")
        except Exception:
            max_uv_time_wib = max_uv_time_utc

    # 2. Fetch forecast timeline to identify hours where UV >= 6 from /api/v1/forecast
    hours_ge_6: List[str] = []
    forecast_url = f"https://api.openuv.io/api/v1/forecast?lat={lat}&lng={lon}"
    req_fc = urllib.request.Request(forecast_url, headers=headers)

    try:
        with urllib.request.urlopen(req_fc, timeout=10) as resp_fc:
            fc_list = json.loads(resp_fc.read().decode("utf-8")).get("result", [])
            for item in fc_list:
                uv_val = item.get("uv", 0)
                uv_time_str = item.get("uv_time")
                if uv_val >= 6.0 and uv_time_str:
                    dt_item_utc = datetime.datetime.fromisoformat(uv_time_str.replace("Z", "+00:00"))
                    dt_item_wib = dt_item_utc.astimezone(tz)
                    time_label = dt_item_wib.strftime("%H:%M WIB")
                    if time_label not in hours_ge_6:
                        hours_ge_6.append(f"{time_label} (UV: {round(uv_val, 1)})")
    except Exception:
        # If forecast call fails or rate limited, provide estimate based on solar noon / max UV
        if max_uv and max_uv >= 6.0 and max_uv_time_wib:
            hours_ge_6.append(f"Estimated around peak {max_uv_time_wib} (Peak UV: {round(max_uv, 1)})")

    result = {
        "current_uv": current_uv,
        "max_uv_today": max_uv,
        "max_uv_time_wib": max_uv_time_wib,
        "hours_uv_ge_6": hours_ge_6,
        "high_uv_alert": bool(max_uv and max_uv >= 6.0),
        "sun_protection_advice": (
            "UV Index >= 6 (Tinggi/Ekstrem). Disarankan gunakan sunscreen SPF 30+, kacamata hitam, atau payung anti-UV saat keluar ruangan."
            if (max_uv and max_uv >= 6.0)
            else "Tingkat radiasi UV terpantau aman/sedang."
        ),
        "cached": False,
    }

    _UV_CACHE[cache_key] = (current_time, result)
    return result
