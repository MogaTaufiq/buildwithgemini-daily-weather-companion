"""Firestore backend integration for Daily Weather & Activity Companion (Indonesia)."""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-7e88f957794e"

# Initialize Firestore Client with hardcoded project ID string
db = firestore.Client(project=PROJECT_ID)


def get_weather_checklist(checklist_id: str) -> Dict[str, Any]:
    """Retrieve a specific weather preparation checklist and gear guide by ID.

    Args:
        checklist_id: The identifier for the checklist (e.g., 'heavy_rain_motor', 'light_rain_transit', 'high_aqi_commute', 'extreme_uv_heat', 'clear_outdoor_sports').

    Returns:
        A dictionary containing the gear checklist, weather condition, risk level, and safety tips.
    """
    doc_ref = db.collection("weather_checklists").document(checklist_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Checklist with ID '{checklist_id}' not found."}
    return doc.to_dict()


def list_weather_checklists(commute_mode: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available weather preparation checklists, optionally filtered by commute mode.

    Args:
        commute_mode: Optional filter for commute mode ('motor', 'transit', 'walking', 'all').

    Returns:
        A list of weather checklist guides matching the criteria.
    """
    col_ref = db.collection("weather_checklists")
    if commute_mode:
        docs = col_ref.where("commute_mode", "in", [commute_mode, "all"]).stream()
    else:
        docs = col_ref.stream()

    return [doc.to_dict() for doc in docs]


def save_weather_checklist(
    checklist_id: str,
    weather_condition: str,
    commute_mode: str,
    risk_level: str,
    must_bring: List[str],
    safety_tips: str,
    recommended_action: str,
) -> Dict[str, Any]:
    """Save or update a weather preparation checklist and gear guide in Firestore.

    Args:
        checklist_id: Unique ID for the checklist (e.g. 'flooding_ojol').
        weather_condition: Weather condition name (e.g. 'Banjir / Genangan').
        commute_mode: Commute mode affected ('motor', 'transit', 'car', 'walking', 'all').
        risk_level: Associated risk level ('low', 'moderate', 'high', 'extreme').
        must_bring: List of items to carry/wear.
        safety_tips: Safety precautions and advice.
        recommended_action: Recommended commuter action.

    Returns:
        Status message with confirmation.
    """
    data = {
        "id": checklist_id,
        "weather_condition": weather_condition,
        "commute_mode": commute_mode,
        "risk_level": risk_level,
        "must_bring": must_bring,
        "safety_tips": safety_tips,
        "recommended_action": recommended_action,
    }
    db.collection("weather_checklists").document(checklist_id).set(data)
    return {"status": "success", "message": f"Checklist '{checklist_id}' saved successfully.", "data": data}


def get_activity_profile(activity_id: str) -> Dict[str, Any]:
    """Retrieve weather & AQI thresholds for a specific outdoor activity.

    Args:
        activity_id: The activity identifier (e.g., 'morning_jogging', 'friday_prayer', 'weekend_futsal', 'daily_commute_motor').

    Returns:
        A dictionary with acceptable AQI, rain probability, temperature, and gear requirements.
    """
    doc_ref = db.collection("outdoor_activity_profiles").document(activity_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Activity profile with ID '{activity_id}' not found."}
    return doc.to_dict()


def list_activity_profiles() -> List[Dict[str, Any]]:
    """List all configured outdoor activity profiles and their weather limits.

    Returns:
        A list of all outdoor activity profiles stored in Firestore.
    """
    docs = db.collection("outdoor_activity_profiles").stream()
    return [doc.to_dict() for doc in docs]


def save_activity_profile(
    activity_id: str,
    activity_name: str,
    preferred_time_window: str,
    max_acceptable_aqi: int,
    max_acceptable_rain_prob: int,
    max_temp_celsius: float,
    ideal_conditions: str,
    gear_needed: List[str],
) -> Dict[str, Any]:
    """Create or update an outdoor activity profile with weather tolerance thresholds.

    Args:
        activity_id: Unique ID for the activity (e.g., 'evening_cycling').
        activity_name: Display name of the activity.
        preferred_time_window: Typical time window (e.g., '19:00 - 21:00 WIB').
        max_acceptable_aqi: Maximum acceptable air quality index before postponing or wearing mask.
        max_acceptable_rain_prob: Maximum rain probability percentage before recommending indoor alternative.
        max_temp_celsius: Maximum comfortable temperature in Celsius.
        ideal_conditions: Description of optimal weather conditions.
        gear_needed: Recommended gear for the activity.

    Returns:
        Status message with confirmation.
    """
    data = {
        "id": activity_id,
        "activity_name": activity_name,
        "preferred_time_window": preferred_time_window,
        "max_acceptable_aqi": max_acceptable_aqi,
        "max_acceptable_rain_prob": max_acceptable_rain_prob,
        "max_temp_celsius": max_temp_celsius,
        "ideal_conditions": ideal_conditions,
        "gear_needed": gear_needed,
    }
    db.collection("outdoor_activity_profiles").document(activity_id).set(data)
    return {"status": "success", "message": f"Activity profile '{activity_id}' saved successfully.", "data": data}
