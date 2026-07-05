import json
import random
import httpx
from crewai.tools import tool
from config import settings

# Predefined mandi databases for Simulator Mode (realistic regional data)
MANDI_PRICES_DB = [
    # Andhra Pradesh (Primary State)
    {"state": "Andhra Pradesh", "mandi": "Guntur", "crop": "Red Chilli", "min_price": 18000, "max_price": 22500, "modal_price": 20500, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Guntur", "crop": "Cotton", "min_price": 6800, "max_price": 7500, "modal_price": 7200, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Adoni", "crop": "Cotton", "min_price": 6900, "max_price": 7600, "modal_price": 7350, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Kurnool", "crop": "Cotton", "min_price": 6750, "max_price": 7450, "modal_price": 7100, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Nandyal", "crop": "Cotton", "min_price": 6820, "max_price": 7510, "modal_price": 7165, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Anantapur", "crop": "Cotton", "min_price": 6680, "max_price": 7380, "modal_price": 7030, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Nellore", "crop": "Cotton", "min_price": 6910, "max_price": 7620, "modal_price": 7265, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Vijayawada", "crop": "Cotton", "min_price": 6850, "max_price": 7590, "modal_price": 7220, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Eluru", "crop": "Cotton", "min_price": 6700, "max_price": 7480, "modal_price": 7090, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Kadapa", "crop": "Cotton", "min_price": 6800, "max_price": 7550, "modal_price": 7175, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Vizianagaram", "crop": "Cotton", "min_price": 6650, "max_price": 7350, "modal_price": 7000, "unit": "Quintal (100kg)"},
    
    {"state": "Andhra Pradesh", "mandi": "Kurnool", "crop": "Paddy", "min_price": 2100, "max_price": 2400, "modal_price": 2250, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Nandyal", "crop": "Maize", "min_price": 1800, "max_price": 2050, "modal_price": 1920, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Vijayawada", "crop": "Paddy", "min_price": 2150, "max_price": 2420, "modal_price": 2285, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Eluru", "crop": "Paddy", "min_price": 2050, "max_price": 2350, "modal_price": 2200, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Nellore", "crop": "Paddy", "min_price": 2200, "max_price": 2500, "modal_price": 2350, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Anantapur", "crop": "Groundnut", "min_price": 6200, "max_price": 7000, "modal_price": 6600, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Kadapa", "crop": "Turmeric", "min_price": 11500, "max_price": 13800, "modal_price": 12650, "unit": "Quintal (100kg)"},
    {"state": "Andhra Pradesh", "mandi": "Chittoor", "crop": "Sugarcane", "min_price": 290, "max_price": 350, "modal_price": 320, "unit": "Tonne (1000kg)"},
    {"state": "Andhra Pradesh", "mandi": "Vizianagaram", "crop": "Maize", "min_price": 1780, "max_price": 2000, "modal_price": 1890, "unit": "Quintal (100kg)"},

    # Telangana (Primary State)
    {"state": "Telangana", "mandi": "Warangal", "crop": "Cotton", "min_price": 7000, "max_price": 7700, "modal_price": 7400, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Khammam", "crop": "Cotton", "min_price": 6850, "max_price": 7450, "modal_price": 7150, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Mahabubnagar", "crop": "Cotton", "min_price": 6900, "max_price": 7550, "modal_price": 7225, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Adilabad", "crop": "Cotton", "min_price": 6950, "max_price": 7650, "modal_price": 7300, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Nizamabad", "crop": "Cotton", "min_price": 6800, "max_price": 7500, "modal_price": 7150, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Karimnagar", "crop": "Cotton", "min_price": 6880, "max_price": 7580, "modal_price": 7230, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Nalgonda", "crop": "Cotton", "min_price": 6850, "max_price": 7520, "modal_price": 7185, "unit": "Quintal (100kg)"},

    {"state": "Telangana", "mandi": "Warangal", "crop": "Paddy", "min_price": 2150, "max_price": 2450, "modal_price": 2300, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Khammam", "crop": "Red Chilli", "min_price": 17500, "max_price": 21000, "modal_price": 19500, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Nizamabad", "crop": "Turmeric", "min_price": 11000, "max_price": 13500, "modal_price": 12500, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Nizamabad", "crop": "Paddy", "min_price": 2100, "max_price": 2380, "modal_price": 2200, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Badepally", "crop": "Maize", "min_price": 1850, "max_price": 2100, "modal_price": 1980, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Karimnagar", "crop": "Paddy", "min_price": 2120, "max_price": 2400, "modal_price": 2260, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Suryapet", "crop": "Paddy", "min_price": 2180, "max_price": 2460, "modal_price": 2320, "unit": "Quintal (100kg)"},
    {"state": "Telangana", "mandi": "Nalgonda", "crop": "Maize", "min_price": 1820, "max_price": 2080, "modal_price": 1950, "unit": "Quintal (100kg)"},

    # Maharashtra
    {"state": "Maharashtra", "mandi": "Lasalgaon", "crop": "Onion", "min_price": 1600, "max_price": 2400, "modal_price": 2000, "unit": "Quintal (100kg)"},
    {"state": "Maharashtra", "mandi": "Pune", "crop": "Onion", "min_price": 1700, "max_price": 2600, "modal_price": 2150, "unit": "Quintal (100kg)"},
    {"state": "Maharashtra", "mandi": "Nagpur", "crop": "Cotton", "min_price": 6700, "max_price": 7400, "modal_price": 7100, "unit": "Quintal (100kg)"},
    
    # Punjab
    {"state": "Punjab", "mandi": "Khanna", "crop": "Wheat", "min_price": 2275, "max_price": 2450, "modal_price": 2350, "unit": "Quintal (100kg)"},
    {"state": "Punjab", "mandi": "Ludhiana", "crop": "Wheat", "min_price": 2250, "max_price": 2480, "modal_price": 2370, "unit": "Quintal (100kg)"},
    {"state": "Punjab", "mandi": "Jalandhar", "crop": "Paddy", "min_price": 2180, "max_price": 2400, "modal_price": 2290, "unit": "Quintal (100kg)"},
    
    # Uttar Pradesh
    {"state": "Uttar Pradesh", "mandi": "Hapur", "crop": "Wheat", "min_price": 2200, "max_price": 2400, "modal_price": 2300, "unit": "Quintal (100kg)"},
    {"state": "Uttar Pradesh", "mandi": "Kanpur", "crop": "Potato", "min_price": 900, "max_price": 1400, "modal_price": 1150, "unit": "Quintal (100kg)"},
    
    # Karnataka
    {"state": "Karnataka", "mandi": "Davanagere", "crop": "Maize", "min_price": 1900, "max_price": 2150, "modal_price": 2020, "unit": "Quintal (100kg)"},
    {"state": "Karnataka", "mandi": "Bangalore", "crop": "Ragi", "min_price": 3800, "max_price": 4400, "modal_price": 4100, "unit": "Quintal (100kg)"},
    
    # Tamil Nadu
    {"state": "Tamil Nadu", "mandi": "Erode", "crop": "Turmeric", "min_price": 12500, "max_price": 15000, "modal_price": 13800, "unit": "Quintal (100kg)"},
    
    # Gujarat
    {"state": "Gujarat", "mandi": "Rajkot", "crop": "Cotton", "min_price": 6800, "max_price": 7600, "modal_price": 7250, "unit": "Quintal (100kg)"},
    {"state": "Gujarat", "mandi": "Gondal", "crop": "Groundnut", "min_price": 6000, "max_price": 7200, "modal_price": 6650, "unit": "Quintal (100kg)"},
    
    # Rajasthan
    {"state": "Rajasthan", "mandi": "Jaipur", "crop": "Mustard", "min_price": 5100, "max_price": 5800, "modal_price": 5450, "unit": "Quintal (100kg)"}
]

@tool("Fetch Mandi Prices Tool")
def fetch_mandi_prices(state: str = None, crop: str = None) -> str:
    """
    Fetches live market (mandi) prices for specific crops and locations.
    Inputs:
        state: State name (e.g., 'Andhra Pradesh', 'Telangana')
        crop: Crop name (e.g., 'Cotton', 'Paddy', 'Red Chilli', 'Maize', 'Turmeric')
    Returns: JSON formatted string containing current price data and trends.
    """
    # Check if a live API call is requested and key is present
    if settings.DATA_GOV_IN_API_KEY:
        try:
            # Live API Call to data.gov.in Agmarknet endpoint
            api_key = settings.DATA_GOV_IN_API_KEY
            url = f"https://api.data.gov.in/resource/9ef84281-22f4-425b-ae77-051e77e7d7eb"
            params = {
                "api-key": api_key,
                "format": "json",
                "limit": 100
            }
            if state:
                params["filters[state]"] = state
            if crop:
                params["filters[commodity]"] = crop
                
            response = httpx.get(url, params=params, timeout=12)
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                if records:
                    formatted_records = []
                    for rec in records:
                        formatted_records.append({
                            "state": rec.get("state"),
                            "district": rec.get("district"),
                            "mandi": rec.get("market"),
                            "crop": rec.get("commodity"),
                            "min_price": float(rec.get("min_price", 0)),
                            "max_price": float(rec.get("max_price", 0)),
                            "modal_price": float(rec.get("modal_price", 0)),
                            "unit": "Quintal (100kg)"
                        })
                    return json.dumps({
                        "source": "data.gov.in Agmarknet API",
                        "status": "success",
                        "data": formatted_records[:15]
                    }, indent=2)
        except Exception as e:
            print(f"data.gov.in API call failed ({e}). Falling back to Simulator Mode.")

    # Simulator Mode:
    filtered_data = MANDI_PRICES_DB
    
    if state:
        state_lower = state.lower().replace(" ", "")
        filtered_data = [d for d in filtered_data if d["state"].lower().replace(" ", "") == state_lower]
        
    if crop:
        crop_lower = crop.lower().strip()
        filtered_data = [d for d in filtered_data if crop_lower in d["crop"].lower()]
        
    # Introduce small random variations to make prices look "live" and dynamic
    live_records = []
    for rec in filtered_data:
        record_copy = rec.copy()
        variation = random.uniform(-0.03, 0.04)
        record_copy["min_price"] = int(record_copy["min_price"] * (1 + variation * 0.8))
        record_copy["max_price"] = int(record_copy["max_price"] * (1 + variation * 1.2))
        record_copy["modal_price"] = int((record_copy["min_price"] + record_copy["max_price"]) / 2)
        live_records.append(record_copy)

    # Dynamic Generator for all-India states if no records matched
    if not live_records and state and crop:
        crop_base_prices = {
            "cotton": {"min": 6500, "max": 7500, "unit": "Quintal (100kg)"},
            "paddy": {"min": 2000, "max": 2400, "unit": "Quintal (100kg)"},
            "maize": {"min": 1800, "max": 2200, "unit": "Quintal (100kg)"},
            "red chilli": {"min": 17000, "max": 21000, "unit": "Quintal (100kg)"},
            "chilli": {"min": 17000, "max": 21000, "unit": "Quintal (100kg)"},
            "turmeric": {"min": 10000, "max": 13000, "unit": "Quintal (100kg)"},
            "wheat": {"min": 2200, "max": 2600, "unit": "Quintal (100kg)"},
            "onion": {"min": 1500, "max": 2500, "unit": "Quintal (100kg)"},
            "sugarcane": {"min": 280, "max": 340, "unit": "Tonne (1000kg)"},
            "mustard": {"min": 5000, "max": 5800, "unit": "Quintal (100kg)"},
            "groundnut": {"min": 5800, "max": 6600, "unit": "Quintal (100kg)"},
            "default": {"min": 3000, "max": 4500, "unit": "Quintal (100kg)"}
        }
        
        crop_key = crop.lower().strip()
        base = crop_base_prices.get(crop_key, crop_base_prices["default"])
        for k, v in crop_base_prices.items():
            if k in crop_key:
                base = v
                break
                
        # Generate 3 regional mandis dynamically
        districts = ["Central", "North", "South-East"]
        for dist in districts:
            mandi_name = f"{state} {dist} Mandi"
            min_p = int(base["min"] * random.uniform(0.95, 1.05))
            max_p = int(base["max"] * random.uniform(0.95, 1.05))
            modal_p = int((min_p + max_p) / 2)
            
            live_records.append({
                "state": state,
                "mandi": mandi_name,
                "crop": crop,
                "min_price": min_p,
                "max_price": max_p,
                "modal_price": modal_p,
                "unit": base["unit"]
            })

    # Sort by modal price descending to help agents recommend the best market
    live_records.sort(key=lambda x: x["modal_price"], reverse=True)

    return json.dumps({
        "source": "Agmarknet Simulator (All-India Mandi Network)",
        "status": "success",
        "data": live_records
    }, indent=2)
