# My agent: Daily Weather & Activity Companion (Indonesia)
One-liner: A conversational agent that helps Indonesian commuters and residents plan daily commutes and outdoor activities safely with a catalog of local weather forecasts, air quality readings, and personalized gear recommendations.

Tool coverage:
- Memory: User locations (home, office, kos at kelurahan level), commute modes (motor/ojol, KRL, car, walking), routine outdoor activities (morning runs, Friday prayers, weekend sports), sensitivities (rain, heat, haze/AQI), and language preference (Bahasa casual / English).
- Tools: Official BMKG & Open-Meteo forecast lookup, AQICN air quality fetch, RainViewer rain radar nowcast, Google Calendar schedule check, and reverse geocoding.
- Catalog/UI: Hourly weather timeline cards with outdoor activity windows, AQI status cards, outfit & gear checklists (raincoat, umbrella, UV protection, mask), and emergency weather/earthquake alert cards rendered via A2UI.
- Image gen: "Today's Sky" skyline postcard (city skyline rendered in today's specific weather conditions) and visual daily outfit/gear recommendation card.
- Sandbox: Commute rain-risk score computation and schedule-to-rain arrival overlap calculation.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): BMKG official API / Open-Meteo integration, RainViewer nowcast radar, code sandbox for commute weather exposure scoring, Google Calendar API for outdoor schedule sync.
