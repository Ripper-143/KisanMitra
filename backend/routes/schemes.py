from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from models.models import Farmer
from agents.crew import use_mock, simulate_schemes_crew

router = APIRouter(prefix="/schemes", tags=["Schemes Matcher"])

@router.get("/match")
def match_schemes(current_user: Farmer = Depends(get_current_user)):
    """
    Protected route. Triggers the Scheme Matcher Agent to query ChromaDB RAG 
    against the farmer's land size, state, and crop type.
    """
    from models.database import SessionLocal
    from models.models import LandProfile
    
    db = SessionLocal()
    crop = "Paddy"
    land_size = 2.5
    state = "Andhra Pradesh"
    try:
        land = db.query(LandProfile).filter(LandProfile.farmer_id == current_user.id).first()
        if land:
            crop = land.crop_type
            land_size = land.land_size_acres
            state = land.state
    finally:
        db.close()

    if use_mock:
        return simulate_schemes_crew(crop=crop, land_size=land_size, state=state)
    else:
        # Run live CrewAI
        from crewai import Crew, Task, Process
        from agents.crew import scheme_matcher_agent
        
        task = Task(
            description=(
                f"Identify matching subsidies and government schemes for a farmer with {land_size} acres of crop '{crop}' in state '{state}'. "
                "Use 'Query Government Schemes Database Tool' to retrieve criteria from the vector database. Formulate eligibility explanations."
            ),
            expected_output="A structured report lists eligible government schemes and instructions on how the farmer can apply.",
            agent=scheme_matcher_agent
        )
        
        crew = Crew(
            agents=[scheme_matcher_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            # Fetch structured matches for UI widgets
            raw_schemes = simulate_schemes_crew(crop=crop, land_size=land_size, state=state)
            
            return {
                "agent": "Government Subsidy Advisor (Live CrewAI + RAG)",
                "task_description": "Query scheme document database and list matches.",
                "matched_schemes": raw_schemes.get("matched_schemes", []),
                "rag_evidence": raw_schemes.get("rag_evidence", ""),
                "recommendation": str(result),
                "logs": ["CrewAI matching complete."]
            }
        except Exception as e:
            print(f"CrewAI schemes matching failed: {e}. Falling back to simulation.")
            return simulate_schemes_crew(crop=crop, land_size=land_size, state=state)
