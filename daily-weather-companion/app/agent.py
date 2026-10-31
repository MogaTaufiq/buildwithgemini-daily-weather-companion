# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

# Load .env before the service modules below read env vars at import time.
load_dotenv()

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.genai import types

from app.firestore_service import (
    get_weather_checklist,
    list_weather_checklists,
    save_weather_checklist,
    get_activity_profile,
    list_activity_profiles,
    save_activity_profile,
)
from app.weather_service import fetch_hourly_weather
from app.sun_service import fetch_daylight_and_sun_times
from app.aqicn_service import get_air_quality
from app.openuv_service import get_uv_index

MODEL = "gemini-3.8-flash"
# Existing Agent Engine sandbox; code execution is disabled when unset, because
# ADK would otherwise create a new Agent Engine on first use.
SANDBOX_RESOURCE_NAME = os.environ.get("SANDBOX_RESOURCE_NAME")


def get_current_time(query: str = "Jakarta") -> str:
    """Gets the current time for Indonesian timezones (WIB, WITA, WIT) or other queries.

    Args:
        query: City or timezone query (e.g. 'Jakarta', 'WIB', 'Bali', 'Jayapura', 'San Francisco').

    Returns:
        A string with the current time information.
    """
    q = query.lower()
    if any(k in q for k in ["jakarta", "wib", "bandung", "surabaya", "semarang", "yogyakarta", "medan"]):
        tz_identifier = "Asia/Jakarta"
    elif any(k in q for k in ["bali", "denpasar", "wita", "makassar", "balikpapan"]):
        tz_identifier = "Asia/Makassar"
    elif any(k in q for k in ["wit", "jayapura", "ambon"]):
        tz_identifier = "Asia/Jayapura"
    elif "sf" in q or "san francisco" in q:
        tz_identifier = "America/Los_Angeles"
    else:
        tz_identifier = "Asia/Jakarta"

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for {query} ({tz_identifier}) is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


INSTRUCTION = """You are Sedia (Daily Weather & Activity Companion for Indonesia), an intelligent assistant that helps Indonesian commuters and residents plan daily commutes and outdoor activities safely.

Capabilities:
1. Live Weather Forecast (`fetch_hourly_weather`): Hourly rain probability %, temperatures, and conditions for Indonesian cities or coordinates.
2. Official AQICN Air Quality (`get_air_quality`): Geo-feed real-time AQI, dominant pollutant, PM2.5, nearest station, and Indonesian category labels (Baik, Sedang, Tidak Sehat untuk Kelompok Sensitif, Tidak Sehat, Sangat Tidak Sehat, Berbahaya).
3. OpenUV Solar Radiation (`get_uv_index`): Current UV index, maximum UV today with peak time (WIB), and hours when UV >= 6 with sunscreen recommendations (cached for 1 hour).
4. Daylight & Sun Times (`fetch_daylight_and_sun_times`): Sunrise, sunset, dusk (twilight), and daylight duration.
5. Weather Checklists & Activity Profiles (Firestore): `get_weather_checklist`, `list_weather_checklists`, `get_activity_profile`, `list_activity_profiles` to advise commuters on what gear to pack (jas hujan setelan, folding umbrella, shoe covers, N95 masks) based on their commute mode and weather severity.
6. Safe Code Execution Sandbox: You can safely execute Python calculations, statistical data processing, or custom scripts in the Agent Engine Sandbox environment whenever complex computing, data aggregation, or formatting is needed.

Always provide practical, friendly, and localized advice (using Indonesian context and time zones like WIB/WITA/WIT).
"""

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(
            attempts=5,
            initial_delay=2.0,
            http_status_codes=[429, 500, 503],
        ),
    ),
    instruction=INSTRUCTION,
    code_executor=(
        AgentEngineSandboxCodeExecutor(sandbox_resource_name=SANDBOX_RESOURCE_NAME)
        if SANDBOX_RESOURCE_NAME
        else None
    ),
    tools=[
        fetch_hourly_weather,
        get_air_quality,
        get_uv_index,
        fetch_daylight_and_sun_times,
        get_current_time,
        get_weather_checklist,
        list_weather_checklists,
        save_weather_checklist,
        get_activity_profile,
        list_activity_profiles,
        save_activity_profile,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
