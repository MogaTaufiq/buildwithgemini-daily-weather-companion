"""Seed script for Daily Weather & Activity Companion (Indonesia) Firestore backend."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-7e88f957794e"


def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore for project: {PROJECT_ID}")

    # 1. Seed weather_checklists collection
    checklists = [
        {
            "id": "heavy_rain_motor",
            "weather_condition": "Hujan Lebat (Heavy Rain)",
            "commute_mode": "motor",
            "risk_level": "high",
            "must_bring": ["Jas hujan setelan (jacket + pants)", "Shoe covers (sarung sepatu)", "Waterproof phone pouch", "Helm visor wiper/anti-fog"],
            "safety_tips": "Avoid underpasses prone to flooding (genangan air). Watch out for slippery road markings and painted lines. Pull over if visibility is below 10m.",
            "recommended_action": "Wear waterproof gear before departing. Consider postponing or switching to MRT/KRL if routes flood."
        },
        {
            "id": "light_rain_transit",
            "weather_condition": "Hujan Ringan / Gerimis (Light Rain / Drizzle)",
            "commute_mode": "transit",
            "risk_level": "moderate",
            "must_bring": ["Payung lipat (folding umbrella)", "Jaket tahan air / windbreaker", "Sandal cadangan"],
            "safety_tips": "Station walkways and stairs can be very slippery. Allow extra 15-20 mins for public transport delays.",
            "recommended_action": "Keep folding umbrella handy in outer backpack compartment."
        },
        {
            "id": "high_aqi_commute",
            "weather_condition": "Polusi Udara Tinggi (High AQI / Haze)",
            "commute_mode": "all",
            "risk_level": "high",
            "must_bring": ["Masker KF94 / N95", "Tetes mata steril", "Botol air minum"],
            "safety_tips": "Avoid intense outdoor cardio/jogging. Keep windows shut and stay indoors during peak traffic hours.",
            "recommended_action": "Wear a fitted N95/KF94 mask for any outdoor or motorbike commute."
        },
        {
            "id": "extreme_uv_heat",
            "weather_condition": "Panas Terik & UV Ekstrem (Extreme Heat & UV)",
            "commute_mode": "all",
            "risk_level": "moderate",
            "must_bring": ["Sunscreen SPF 50+", "Kacamata hitam (sunglasses)", "Topi / payung anti-UV", "Jaket breathable / manset tangan"],
            "safety_tips": "Stay hydrated. Avoid direct sun exposure between 11:00 AM - 02:00 PM.",
            "recommended_action": "Apply sunscreen 15 minutes before leaving and reapply if sweating."
        },
        {
            "id": "clear_outdoor_sports",
            "weather_condition": "Cerah Berawan (Partly Cloudy / Ideal)",
            "commute_mode": "walking",
            "risk_level": "low",
            "must_bring": ["Air minum", "Pakaian olahraga breathable"],
            "safety_tips": "Great weather for outdoor activities (futsal, jogging, walking).",
            "recommended_action": "Optimal window for outdoor runs or commutes."
        }
    ]

    for item in checklists:
        doc_id = item["id"]
        db.collection("weather_checklists").document(doc_id).set(item)
        print(f"Seeded weather_checklists/{doc_id}")

    # 2. Seed outdoor_activity_profiles collection
    activities = [
        {
            "id": "morning_jogging",
            "activity_name": "Morning Jogging / Running",
            "preferred_time_window": "05:30 - 07:00 WIB",
            "max_acceptable_aqi": 100,
            "max_acceptable_rain_prob": 30,
            "max_temp_celsius": 30.0,
            "ideal_conditions": "Cerah, sejuk, AQI < 100, no rain",
            "gear_needed": ["Sepatu lari", "Pakaian lari ringan", "Headlamp / reflektor jika subuh"]
        },
        {
            "id": "friday_prayer",
            "activity_name": "Sholat Jumat (Friday Prayer)",
            "preferred_time_window": "11:30 - 13:00 WIB",
            "max_acceptable_aqi": 200,
            "max_acceptable_rain_prob": 70,
            "max_temp_celsius": 36.0,
            "ideal_conditions": "Indoor / sheltered courtyard",
            "gear_needed": ["Payung lipat (jalan kaki ke masjid)", "Sajadah tipis", "Kantong sandal"]
        },
        {
            "id": "weekend_futsal",
            "activity_name": "Weekend Futsal / Mini Soccer",
            "preferred_time_window": "16:00 - 18:00 WIB",
            "max_acceptable_aqi": 150,
            "max_acceptable_rain_prob": 40,
            "max_temp_celsius": 32.0,
            "ideal_conditions": "Kering, tidak ada genangan / petir",
            "gear_needed": ["Sepatu futsal / mini soccer", "Handuk kecil", "Baju ganti kering", "Minuman elektrolit"]
        },
        {
            "id": "daily_commute_motor",
            "activity_name": "Motorbike / Ojol Commute",
            "preferred_time_window": "07:00 - 09:00 WIB & 17:00 - 19:30 WIB",
            "max_acceptable_aqi": 180,
            "max_acceptable_rain_prob": 50,
            "max_temp_celsius": 35.0,
            "ideal_conditions": "Kering, visibilitas baik",
            "gear_needed": ["Jas hujan setelan", "Cover bag / tas anti-air", "Masker N95", "Sarung tangan"]
        }
    ]

    for act in activities:
        doc_id = act["id"]
        db.collection("outdoor_activity_profiles").document(doc_id).set(act)
        print(f"Seeded outdoor_activity_profiles/{doc_id}")

    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
