from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from auth import get_current_user
from models.models import Farmer
from agents.crew import use_mock, simulate_weather_crew

router = APIRouter(prefix="/weather", tags=["Weather Advisory"])

@router.get("/advisory")
def get_advisory(
    city: str = Query(None),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Protected route. Triggers the Weather Advisory Agent to get forecast data 
    and output agricultural schedules (spraying, sowing, irrigation).
    """
    # Use user profile details if not explicitly passed
    from models.database import SessionLocal
    from models.models import LandProfile
    
    db = SessionLocal()
    try:
        land = db.query(LandProfile).filter(LandProfile.farmer_id == current_user.id).first()
        if land:
            if not city:
                city = land.district
    finally:
        db.close()
        
    # Default fallbacks
    if not city:
        city = "Guntur"

    if use_mock:
        return simulate_weather_crew(city=city)
    else:
        # Run live CrewAI
        from crewai import Crew, Task, Process
        from agents.crew import weather_advisory_agent
        
        task = Task(
            description=(
                f"Obtain weather forecast for city '{city}' using 'Fetch Weather Advisory Tool'. "
                "Synthesize farm advisories explaining spraying, irrigation, and sowing schedules."
            ),
            expected_output="An agronomic report advising on irrigation, sowing, and spraying parameters over the next 5 days.",
            agent=weather_advisory_agent
        )
        
        crew = Crew(
            agents=[weather_advisory_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            # Fetch raw simulation data for the UI structured tables
            raw_weather = simulate_weather_crew(city=city)
            
            return {
                "city": city,
                "agent": "Weather Advisory Agent (Live CrewAI)",
                "task_description": f"Fetch weather schedules for {city}.",
                "forecast": raw_weather.get("forecast", []),
                "recommendation": str(result),
                "logs": ["CrewAI weather check complete."]
            }
        except Exception as e:
            print(f"CrewAI weather check failed: {e}. Falling back to simulation.")
            return simulate_weather_crew(city=city)
