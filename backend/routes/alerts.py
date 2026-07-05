from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from auth import get_current_user
from models.database import get_db
from models.models import Farmer, AlertLog
from agents.crew import use_mock, simulate_alert_crew

router = APIRouter(prefix="/alerts", tags=["Alerts & Notifications"])

# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class AlertCreateSchema(BaseModel):
    alert_type: str  # Weather, Market Price, Scheme, custom
    message: str
    channel: str = "SMS" # SMS or WhatsApp

class AlertResponseSchema(BaseModel):
    id: int
    farmer_id: int
    alert_type: str
    message: str
    status: str
    sent_at: str

# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("", response_model=List[AlertResponseSchema])
def get_alerts(
    current_user: Farmer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch the notification alert history log for the current farmer."""
    logs = db.query(AlertLog).filter(AlertLog.farmer_id == current_user.id).order_by(AlertLog.sent_at.desc()).all()
    
    # Format dates to string
    res = []
    for log in logs:
        res.append(AlertResponseSchema(
            id=log.id,
            farmer_id=log.farmer_id,
            alert_type=log.alert_type,
            message=log.message,
            status=log.status,
            sent_at=log.sent_at.strftime("%Y-%m-%d %H:%M:%S")
        ))
    return res

@router.post("/send")
def send_alert(
    body: AlertCreateSchema,
    current_user: Farmer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Protected route. Triggers the Alert & Notification Agent (CrewAI/Simulated) 
    to send an SMS or WhatsApp alert and logs the history.
    """
    phone = current_user.phone_number or "+919999999999"
    if body.channel.lower() == "whatsapp":
        phone = f"whatsapp:{phone}"
    
    if use_mock:
        res = simulate_alert_crew(
            farmer_id=current_user.id,
            phone_number=phone,
            alert_type=body.alert_type,
            message=body.message
        )
        return {
            "status": "success",
            "message": "Alert processed (Simulated)",
            "details": res
        }
    else:
        # Run live CrewAI task
        from crewai import Crew, Task, Process
        from agents.crew import alert_notification_agent
        
        task = Task(
            description=(
                f"Send an SMS alert to farmer ID {current_user.id} at phone number '{phone}'. "
                f"Alert Type: '{body.alert_type}'. Message Content: '{body.message}'. "
                "Use the 'Dispatch Farmer SMS Notification Tool' to complete this and record log."
            ),
            expected_output="An dispatch confirmation detailing target phone, status, and message.",
            agent=alert_notification_agent
        )
        
        crew = Crew(
            agents=[alert_notification_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            return {
                "status": "success",
                "message": "Alert dispatched via CrewAI",
                "details": str(result)
            }
        except Exception as e:
            print(f"CrewAI alert dispatch failed: {e}. Falling back to simulation.")
            res = simulate_alert_crew(
                farmer_id=current_user.id,
                phone_number=phone,
                alert_type=body.alert_type,
                message=body.message
            )
            return {
                "status": "success",
                "message": "Alert processed (Simulated Fallback)",
                "details": res
            }
