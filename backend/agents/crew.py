import os
import json
from crewai import Agent, Task, Crew, Process, LLM
from config import settings

# Import our tools
from tools.crop_tool import diagnose_crop_disease
from tools.price_tool import fetch_mandi_prices
from tools.weather_tool import fetch_weather_advisory
from tools.rag_tool import query_government_schemes
from tools.sms_tool import dispatch_sms_alert

# Setup LLM configuration dynamically
provider = (settings.LLM_PROVIDER or "groq").lower().strip()

llm = None
use_mock = True

if provider == "gemini":
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            llm = LLM(
                model="gemini/gemini-2.5-flash",
                api_key=api_key,
                temperature=0.2
            )
            use_mock = False
            print("AI Integration: Live Gemini model successfully initialized.")
        except Exception as e:
            print(f"Error configuring Gemini LLM ({e}). Switching to Mock Mode.")
elif provider == "openai":
    api_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            llm = LLM(
                model="openai/gpt-4o-mini",
                api_key=api_key,
                temperature=0.2
            )
            use_mock = False
            print("AI Integration: Live OpenAI model successfully initialized.")
        except Exception as e:
            print(f"Error configuring OpenAI LLM ({e}). Switching to Mock Mode.")
else: # Default is Groq
    api_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
    if api_key:
        try:
            llm = LLM(
                model=settings.LLM_MODEL or "groq/llama-3.3-70b-versatile",
                api_key=api_key,
                temperature=0.2
            )
            use_mock = False
            print("AI Integration: Live Groq model successfully initialized.")
        except Exception as e:
            print(f"Error configuring Groq LLM ({e}). Switching to Mock Mode.")

# ── Agent Definitions ────────────────────────────────────────────────────────

# 1. Crop Health Agent
crop_health_agent = Agent(
    role="Crop Pathologist and Health Advisor",
    goal="Diagnose crop diseases from leaf/crop photo analysis and suggest biological and chemical treatments.",
    backstory="You are an expert plant pathologist with 20 years of experience in agronomy. You specialize in diagnosing diseases in crops like paddy, cotton, maize, chilli, and turmeric, and recommending organic and chemical controls.",
    tools=[diagnose_crop_disease],
    llm=llm,
    verbose=True
)

# 2. Market Price Agent
market_price_agent = Agent(
    role="Mandi Price Analyst & Marketing Advisor",
    goal="Fetch live mandi rates for crops, analyze the best marketplace and timing to sell for maximum profit.",
    backstory="You are an agricultural economist specializing in Indian crop marketing. You analyze mandi prices across Guntur, Khammam, Nizamabad, Warangal, and Adoni to help farmers avoid middle-men exploitation.",
    tools=[fetch_mandi_prices],
    llm=llm,
    verbose=True
)

# 3. Weather Advisory Agent
weather_advisory_agent = Agent(
    role="Agricultural Meteorology Advisor",
    goal="Provide actionable weather-based sowing, spraying, and irrigation recommendations.",
    backstory="You are a micro-climate expert. You analyze weather forecasts (temperature, humidity, wind, precipitation) and compile crop-specific daily farm action plans.",
    tools=[fetch_weather_advisory],
    llm=llm,
    verbose=True
)

# 4. Scheme Matcher Agent
scheme_matcher_agent = Agent(
    role="Government Subsidy & Policy Advisor",
    goal="Match farmer profiles with eligible schemes, crop insurance policies, and subsidies.",
    backstory="You are a social welfare officer. You query local databases of agricultural welfare policies (like PM-Kisan, PMFBY, YSR Rythu Bharosa, and Rythu Bandhu) to find matches for small and marginal landholders.",
    tools=[query_government_schemes],
    llm=llm,
    verbose=True
)

# 5. Alert & Notification Agent
alert_notification_agent = Agent(
    role="Alert Dispatcher & Communication Specialist",
    goal="Send critical SMS notifications to farmers and log alert history in the database.",
    backstory="You are a digital advisory system dispatcher. You format crop reports, price alerts, and storm warnings into concise SMS texts and dispatch them using SMS tools.",
    tools=[dispatch_sms_alert],
    llm=llm,
    verbose=True
)


# ── Simulated Runner Fallbacks (For Evaluation without LLM Keys) ─────────────

def simulate_crop_crew(crop_type: str, image_name: str) -> dict:
    """Mock execution mimicking Crop Health Agent CrewAI logs and final report."""
    print("AGENT: Starting Crop Diagnosis Crew (Simulated)...")
    diag_result = diagnose_crop_disease.func(image_path=image_name, crop_type=crop_type)
    
    # Generate structured output
    disease_info = "Healthy Leaf"
    severity = "None"
    if "blast" in diag_result.lower():
        disease_info = "Rice Blast (Pyricularia oryzae)"
        severity = "High"
    elif "curl" in diag_result.lower():
        disease_info = "Cotton Leaf Curl Virus (CLCuV)"
        severity = "Moderate"
    elif "blight" in diag_result.lower():
        disease_info = "Northern Corn Leaf Blight (Exserohilum turcicum)"
        severity = "Moderate"
    elif "anthracnose" in diag_result.lower():
        disease_info = "Chilli Anthracnose (Colletotrichum capsici)"
        severity = "High"

    report = {
        "agent": "Crop Pathologist and Health Advisor",
        "task_description": f"Diagnose crop health from leaf photo for {crop_type}.",
        "diagnosis_details": diag_result,
        "disease_detected": disease_info,
        "severity": severity,
        "logs": [
            "Executing 'Diagnose Crop Disease Tool' with parameters: image_path='" + image_name + "'",
            "Tool Output: " + diag_result.replace("\n", " "),
            "Formulating crop diagnosis report and outlining active treatment plans."
        ]
    }
    return report

def simulate_market_crew(crop: str, state: str) -> dict:
    print("AGENT: Starting Market Price Crew (Simulated)...")
    prices_raw = fetch_mandi_prices.func(state=state, crop=crop)
    prices_data = json.loads(prices_raw)
    
    # Formulate recommendations
    records = prices_data.get("data", [])
    recommendation = "Hold selling. Wait for price stabilization."
    best_mandi = "N/A"
    
    if records:
        best_rec = records[0]  # First record is sorted as highest modal price
        best_mandi = best_rec["mandi"]
        recommendation = (
            f"Recommend selling your {crop} at the {best_mandi} Mandi (in {best_rec['state']}) "
            f"where the modal price is currently at a peak of Rs. {best_rec['modal_price']} per {best_rec['unit']}. "
            f"Prices are expected to remain steady for the next 4 days."
        )

    return {
        "agent": "Mandi Price Analyst",
        "task_description": f"Analyze market rates for {crop} in {state}.",
        "prices": records,
        "best_mandi": best_mandi,
        "recommendation": recommendation,
        "logs": [
            f"Calling 'Fetch Mandi Prices Tool' with query state={state}, crop={crop}",
            "Comparing prices across regional mandis...",
            "Selecting highest modal rate and formulating economic recommendation."
        ]
    }

def simulate_weather_crew(city: str) -> dict:
    print("AGENT: Starting Weather Advisory Crew (Simulated)...")
    weather_raw = fetch_weather_advisory.func(city=city)
    weather_data = json.loads(weather_raw)
    
    forecast = weather_data.get("forecast", [])
    today = forecast[0] if forecast else {}
    
    recommendation = "Proceed with scheduled agricultural practices."
    if today:
        spray_status = today.get("spraying_suitability", {}).get("status", "")
        irrigation_status = today.get("irrigation_advice", {}).get("status", "")
        
        recommendation = (
            f"Weather update for {city}: Today is {today.get('condition')} ({today.get('temp_celsius')}°C). "
            f"Spraying Advice: {spray_status}. Irrigation Advice: {irrigation_status}."
        )

    return {
        "city": city,
        "agent": "Agricultural Meteorology Advisor",
        "task_description": f"Fetch 5-day forecast and agronomic schedule for {city}.",
        "forecast": forecast,
        "recommendation": recommendation,
        "logs": [
            f"Calling 'Fetch Weather Advisory Tool' for location={city}",
            "Parsing temperature, precipitation probabilities, and wind speeds...",
            "Computing spraying suitability index and irrigation adjustments."
        ]
    }

def simulate_schemes_crew(crop: str, land_size: float, state: str) -> dict:
    print("AGENT: Starting Scheme Matcher Crew (Simulated)...")
    
    # Query database using RAG
    query = f"Schemes for {crop} in {state} with land size {land_size} acres"
    rag_context = query_government_schemes.func(query=query)
    
    matched_schemes = []
    
    # Rule-based matching for structure
    if "Andhra Pradesh" in state:
        matched_schemes.append({
            "name": "YSR Rythu Bharosa",
            "benefit": "Rs. 13,500/year investment support in 3 installments",
            "eligibility": "Landowners & tenant farmers in AP, integrated with PM-Kisan",
            "source_doc": "ysr_rythu_bharosa.txt"
        })
        matched_schemes.append({
            "name": "AP Micro Irrigation Project (APMIP)",
            "benefit": "Up to 90% subsidy for drip and sprinkler irrigation installations",
            "eligibility": "Small and marginal farmers in AP holding under 5 acres (70% for others)",
            "source_doc": "ysr_ap_micro_irrigation.txt"
        })
    elif "Telangana" in state:
        matched_schemes.append({
            "name": "Rythu Bandhu",
            "benefit": f"Rs. 5,000 per acre/season (Total Rs. {land_size * 10000:.0f}/year for {land_size} acres)",
            "eligibility": "Landowners in Telangana registered in Dharani portal",
            "source_doc": "rythu_bandhu.txt"
        })
        
    # Standard Central Schemes
    matched_schemes.append({
        "name": "PM-KISAN",
        "benefit": "Rs. 6,000/year income support in 3 equal installments",
        "eligibility": "All landholding farmer families in India (any land size)",
        "source_doc": "pm_kisan.txt"
    })
    
    matched_schemes.append({
        "name": "PMFBY (Crop Insurance)",
        "benefit": f"Comprehensive crop insurance cover for {crop} with capped premium of 1.5% - 2.0%",
        "eligibility": "All farmers growing notified crops in notified areas",
        "source_doc": "pmfby.txt"
    })

    # PM Kisan Maan-Dhan Yojana
    if land_size <= 5:
        matched_schemes.append({
            "name": "PM Kisan Maan-Dhan Yojana (PM-KMY)",
            "benefit": "Assured monthly pension of Rs. 3,000 after attaining 60 years of age",
            "eligibility": "Small and marginal farmers aged 18-40 with cultivable land under 5 acres",
            "source_doc": "pm_kmy.txt"
        })

    # Soil Health Card Scheme
    matched_schemes.append({
        "name": "Soil Health Card Scheme",
        "benefit": "Free soil nutrient testing and tailored fertilizer recommendation cards every two years",
        "eligibility": "All landholding farmers across India",
        "source_doc": "soil_health_card.txt"
    })

    # Compile dynamic advisor recommendation summary
    recs = [
        f"Based on your profile of {land_size} acres of {crop} in {state}, here is your AI Subsidy advisory:"
    ]
    if "Andhra Pradesh" in state:
        recs.append(
            f"• In Andhra Pradesh, you are eligible for the YSR Rythu Bharosa input support (Rs. 13,500/yr). "
            f"Additionally, you qualify for the AP Micro Irrigation Project (APMIP) with up to 90% subsidy for installing drip systems."
        )
    elif "Telangana" in state:
        recs.append(
            f"• In Telangana, you qualify for Rythu Bandhu input support, providing Rs. 5,000 per acre/season."
        )
    
    recs.append("• You qualify for PM-KISAN, granting Rs. 6,000/year direct cash transfer.")
    
    if land_size <= 5:
        recs.append(
            "• Since your land size is <= 5 acres, you are eligible to enroll in the PM-KMY pension scheme to secure Rs. 3,000/month after retirement."
        )
    recs.append(
        "• We recommend submitting soil samples to your local laboratory for a free Soil Health Card to optimize fertilizer application."
    )
    
    recommendation = "\n\n".join(recs)

    return {
        "agent": "Government Subsidy & Policy Advisor",
        "task_description": f"Match schemes for {land_size} acres of {crop} in {state}.",
        "matched_schemes": matched_schemes,
        "rag_evidence": rag_context,
        "recommendation": recommendation,
        "logs": [
            f"Calling 'Query Government Schemes Database Tool' with query='{query}'",
            "Evaluating retrieved eligibility criteria against farmer land size and crop...",
            "Filtering schemes and compiling matching list."
        ]
    }

def simulate_alert_crew(farmer_id: int, phone_number: str, alert_type: str, message: str) -> dict:
    print("AGENT: Starting Alert Dispatch Crew (Simulated)...")
    sms_res = dispatch_sms_alert.func(
        farmer_id=farmer_id,
        phone_number=phone_number,
        alert_type=alert_type,
        message=message
    )
    
    return {
        "agent": "Alert Dispatcher & Communication Specialist",
        "task_description": f"Send {alert_type} alert to {phone_number}.",
        "status": "Simulated" if "Simulated" in sms_res else "Sent",
        "details": sms_res,
        "logs": [
            f"Calling 'Dispatch Farmer SMS Notification Tool' for farmer={farmer_id}",
            "Composing message content and establishing gateway connection...",
            "Alert dispatched and logged in PostgreSQL/SQLite."
        ]
    }
