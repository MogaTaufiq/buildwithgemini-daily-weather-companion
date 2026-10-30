"""Tools must report missing input/config instead of returning wrong-place data."""

from app.aqicn_service import get_air_quality
from app.sun_service import fetch_daylight_and_sun_times
from app.weather_service import fetch_hourly_weather


def test_unknown_city_is_an_error_not_jakarta() -> None:
    for tool in (fetch_hourly_weather, fetch_daylight_and_sun_times):
        result = tool("Pontianak")
        assert "error" in result, tool.__name__
        assert "latitude" not in result


def test_aqicn_without_token_is_an_error(monkeypatch) -> None:
    monkeypatch.delenv("AQICN_TOKEN", raising=False)
    assert "error" in get_air_quality(-6.2088, 106.8456)
