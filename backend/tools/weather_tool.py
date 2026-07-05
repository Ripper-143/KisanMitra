import json
import random
import httpx
from crewai.tools import tool
from config import settings

@tool("Fetch Weather Advisory Tool")
def fetch_weather_advisory(city: str = "Guntur") -> str:
    """
    Fetches the 5-day weather forecast and provides agronomic advisories.
    Inputs:
        city: City name in AP or Telangana (e.g. 'Guntur', 'Warangal', 'Anantapur', 'Adoni', 'Khammam')
    Returns: JSON formatted string containing forecast data and spray/irrigation recommendations.
    """
    city_clean = city.strip()
    
    # Check if a live API key exists for OpenWeatherMap
    if settings.OPENWEATHERMAP_API_KEY:
        try:
            # Live OpenWeatherMap 5-Day/3-Hour Forecast API
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": f"{city_clean},IN",
                "appid": settings.OPENWEATHERMAP_API_KEY,
                "units": "metric"
            }
            response = httpx.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                forecast_list = data.get("list", [])
                
                # Group hourly data into daily forecasts
                daily_forecasts = []
                # Simple extraction of 1 forecast per day (every 8th slot in 3-hour chunks)
                for i in range(0, min(len(forecast_list), 40), 8):
                    slot = forecast_list[i]
                    main_data = slot.get("main", {})
                    weather_desc = slot.get("weather", [{}])[0].get("description", "clear sky")
                    weather_main = slot.get("weather", [{}])[0].get("main", "Clear")
                    wind_speed = slot.get("wind", {}).get("speed", 0.0)
                    humidity = main_data.get("humidity", 50)
                    temp = main_data.get("temp", 30.0)
                    
                    daily_forecasts.append({
                        "date": slot.get("dt_txt").split(" ")[0],
                        "temp_celsius": temp,
                        "humidity_pct": humidity,
                        "wind_speed_kmh": wind_speed * 3.6,  # m/s to km/h
                        "condition": weather_main,
                        "description": weather_desc.capitalize()
                    })
                    
                # Generate advices based on conditions
                return _generate_advisory_payload(city_clean, daily_forecasts, source="OpenWeatherMap API")
        except Exception as e:
            print(f"OpenWeatherMap API Call failed ({e}). Falling back to Simulator Mode.")

    # Simulator Mode:
    # Build a simulated forecast based on location and season
    # Let's say it's July (Monsoon season in AP/Telangana). High chance of rain, warm temps.
    forecasts = []
    conditions = ["Rain", "Heavy Rain", "Cloudy", "Clear", "Partly Cloudy"]
    weights = [0.4, 0.1, 0.2, 0.1, 0.2]  # Monsoon weights
    
    # Let's make Anantapur dry, Guntur humid/wet, Warangal moderate
    base_temp = 32.0
    base_humidity = 70
    if "anantapur" in city_clean.lower():
        base_temp = 35.0
        base_humidity = 45
        weights = [0.1, 0.05, 0.25, 0.4, 0.2]  # Rain is rare in Anantapur
    elif "guntur" in city_clean.lower():
        base_temp = 31.0
        base_humidity = 75
    
    from datetime import datetime, timedelta
    start_date = datetime.now()
    
    for i in range(5):
        day = start_date + timedelta(days=i)
        cond = random.choices(conditions, weights=weights)[0]
        
        # Temp fluctuates around base
        temp = round(base_temp + random.uniform(-3.0, 3.0), 1)
        humidity = min(100, max(20, int(base_humidity + random.uniform(-10, 10))))
        wind = round(random.uniform(5.0, 25.0), 1)
        
        if cond in ["Rain", "Heavy Rain"]:
            humidity = int(random.uniform(85, 98))
            temp = round(temp - 3, 1)
            
        desc_map = {
            "Rain": "Light to moderate rain showers",
            "Heavy Rain": "Heavy downpour with thunderstorm",
            "Cloudy": "Overcast clouds",
            "Clear": "Sunny and clear sky",
            "Partly Cloudy": "Scattered clouds"
        }
        
        forecasts.append({
            "date": day.strftime("%Y-%m-%d"),
            "temp_celsius": temp,
            "humidity_pct": humidity,
            "wind_speed_kmh": wind,
            "condition": cond,
            "description": desc_map[cond]
        })
        
    return _generate_advisory_payload(city_clean, forecasts, source="Agricultural Weather Simulator")


def _generate_advisory_payload(city: str, forecasts: list, source: str) -> str:
    """Helper to analyze forecasts and attach farm action indexes."""
    # Action Index rules:
    # Spraying: Bad if wind > 15 km/h OR Rain forecasted today/tomorrow.
    # Irrigation: Not needed if Rain > 60% probability or heavy rain. Highly needed if temp > 34 and clear.
    # Sowing: Good if moderate soil moisture (some rain in forecast) but not flooding.
    
    advisories = []
    for day in forecasts:
        cond = day["condition"].lower()
        wind = day["wind_speed_kmh"]
        humidity = day["humidity_pct"]
        temp = day["temp_celsius"]
        
        # Determine spraying suitability
        if "rain" in cond:
            spray = "NOT SUITABLE (Rain will wash away pesticide/fertilizer sprays)"
            spray_code = "RED"
            irrigation = "SUSPENDED (Rain provides natural soil moisture)"
            irrigation_code = "GREEN"
        elif wind > 18.0:
            spray = "UNSUITABLE (High wind speed causes chemical drift)"
            spray_code = "AMBER"
            irrigation = "RECOMMENDED (Higher evaporation due to dry winds)"
            irrigation_code = "AMBER"
        else:
            spray = "SUITABLE (Ideal weather for pesticide/fungicide application)"
            spray_code = "GREEN"
            irrigation = "NORMAL SCHEDULE" if temp < 33.0 else "INCREASE VOLUME (High temperature)"
            irrigation_code = "GREEN" if temp < 33.0 else "AMBER"
            
        # Sowing advice (for first 2 days mainly)
        if "heavy rain" in cond:
            sowing = "DELAY SOWING (Risk of seed wash-off and waterlogging)"
            sowing_code = "RED"
        elif "rain" in cond:
            sowing = "GOOD CONDITIONS (Optimal soil moisture for germination)"
            sowing_code = "GREEN"
        elif temp > 36.0:
            sowing = "DELAY SOWING (High soil temperature reduces germination rate)"
            sowing_code = "AMBER"
        else:
            sowing = "MODERATE (Irrigate immediately after sowing)"
            sowing_code = "GREEN"
            
        advisories.append({
            "date": day["date"],
            "temp_celsius": temp,
            "humidity_pct": humidity,
            "wind_speed_kmh": wind,
            "condition": day["condition"],
            "description": day["description"],
            "spraying_suitability": {
                "status": spray,
                "color": spray_code
            },
            "irrigation_advice": {
                "status": irrigation,
                "color": irrigation_code
            },
            "sowing_advice": {
                "status": sowing,
                "color": sowing_code
            }
        })
        
    return json.dumps({
        "city": city,
        "source": source,
        "forecast": advisories
    }, indent=2)
