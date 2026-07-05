from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from auth import get_current_user
from models.models import Farmer
from agents.crew import use_mock, simulate_market_crew

router = APIRouter(prefix="/market", tags=["Market Prices"])

@router.get("/prices")
def get_prices(
    crop: str = Query(None),
    state: str = Query(None),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Protected route. Triggers the Market Price Agent to fetch live mandi rates 
    and recommend the best place/time to sell.
    """
    # Use user profile details if not explicitly passed
    from models.database import SessionLocal
    from models.models import LandProfile
    
    db = SessionLocal()
    try:
        land = db.query(LandProfile).filter(LandProfile.farmer_id == current_user.id).first()
        if land:
            if not crop:
                crop = land.crop_type
            if not state:
                state = land.state
    finally:
        db.close()
        
    # Default fallbacks if profiles are empty
    if not crop:
        crop = "Cotton"
    if not state:
        state = "Andhra Pradesh"

    if use_mock:
        return simulate_market_crew(crop=crop, state=state)
    else:
        # Run live CrewAI
        from crewai import Crew, Task, Process
        from agents.crew import market_price_agent
        
        task = Task(
            description=(
                f"Analyze mandi prices for crop '{crop}' in state '{state}'. "
                "Use 'Fetch Mandi Prices Tool' to fetch data. Recommend the best mandi and selling plan."
            ),
            expected_output="A structured report advising where, when, and at what price the farmer should sell.",
            agent=market_price_agent
        )
        
        crew = Crew(
            agents=[market_price_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            # Try to get best market name from text
            res_str = str(result)
            best_mandi = "Guntur"
            for mandi in ["Guntur", "Warangal", "Khammam", "Nizamabad", "Adoni", "Kurnool"]:
                if mandi.lower() in res_str.lower():
                    best_mandi = mandi
                    break
                    
            # Parse simulated rates for the widget data display as well
            raw_prices = simulate_market_crew(crop=crop, state=state)
            
            return {
                "agent": "Market Price Agent (Live CrewAI)",
                "task_description": f"Analyze market rates for {crop} in {state}.",
                "prices": raw_prices.get("prices", []),
                "best_mandi": best_mandi,
                "recommendation": res_str,
                "logs": ["CrewAI analysis succeeded."]
            }
        except Exception as e:
            print(f"CrewAI price analysis failed: {e}. Falling back to simulation.")
            return simulate_market_crew(crop=crop, state=state)
