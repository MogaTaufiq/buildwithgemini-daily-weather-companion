"""Daylight, Sunrise, Sunset, and Twilight calculation tool via Sunrise-Sunset API."""

import datetime
import json
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo
from typing import Any, Dict, Optional

from app.weather_service import resolve_location, unknown_location_error


def fetch_daylight_and_sun_times(
    city_or_location: str = "Jakarta",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    date: Optional[str] = "today",
) -> Dict[str, Any]:
    """Fetch sunrise, sunset, dusk, dawn, and daylight duration for outdoor activity planning.

    Args:
        city_or_location: City name (e.g. 'Jakarta', 'Bandung', 'Surabaya', 'Denpasar', 'Medan').
        latitude: Optional explicit latitude. Required for cities outside the built-in list.
        longitude: Optional explicit longitude. Required for cities outside the built-in list.
        date: Date in YYYY-MM-DD format or 'today' (default: 'today').

    Returns:
        A dictionary with localized sunrise, sunset, golden hour, twilight times, and daylight guidance.
    """
    location = resolve_location(city_or_location, latitude, longitude)
    if location is None:
        return unknown_location_error(city_or_location)
    lat, lon, tz_name = location

    tz = ZoneInfo(tz_name)
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"

    req = urllib.request.Request(url, headers={"User-Agent": "JasHujan-DailyWeatherCompanion/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("status") != "OK":
        return {"error": f"Failed to fetch sun times for {city_or_location}"}

    results = payload.get("results", {})

    def to_local_time(iso_str: Optional[str]) -> Optional[str]:
        if not iso_str:
            return None
        dt_utc = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        dt_local = dt_utc.astimezone(tz)
        return dt_local.strftime("%H:%M:%S %Z")

    day_length_sec = results.get("day_length", 0)
    hours, remainder = divmod(day_length_sec, 3600)
    minutes, _ = divmod(remainder, 60)

    sunrise_local = to_local_time(results.get("sunrise"))
    sunset_local = to_local_time(results.get("sunset"))
    dawn_local = to_local_time(results.get("civil_twilight_begin"))
    dusk_local = to_local_time(results.get("civil_twilight_end"))

    return {
        "location": city_or_location,
        "timezone": tz_name,
        "date": date,
        "sunrise": sunrise_local,
        "sunset": sunset_local,
        "first_light_dawn": dawn_local,
        "last_light_dusk": dusk_local,
        "daylight_duration": f"{hours} hours {minutes} minutes",
        "outdoor_advice": (
            f"Sunrise at {sunrise_local} (ideal for early morning run/cycling before heat). "
            f"Sunset at {sunset_local} with dusk ending at {dusk_local} (turn on bike headlights for evening commutes)."
        ),
    }
