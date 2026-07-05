import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from auth import get_current_user
from models.database import get_db
from models.models import Farmer, CropDiagnosis, LandProfile
from agents.crew import use_mock, simulate_crop_crew
from tools.pdf_generator import generate_crop_pdf
from tools.sms_tool import dispatch_sms_alert

router = APIRouter(prefix="/crop", tags=["Crop Health"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/diagnose")
async def diagnose_crop(
    image: UploadFile = File(...),
    crop_type: str = Form("paddy"),
    current_user: Farmer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Protected route. Uploads a plant/leaf image, triggers the Crop Health Agent, 
    saves the result to the database, and returns the diagnostic report.
    """
    # Verify file extension
    ext = os.path.splitext(image.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, or WEBP images are supported.")
        
    # Save file locally
    file_path = os.path.join(UPLOAD_DIR, f"farmer_{current_user.id}_{image.filename}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")
        
    report = {}
    
    # Trigger diagnosis
    if use_mock:
        # Run simulator
        report = simulate_crop_crew(crop_type=crop_type, image_name=file_path)
    else:
        # Actual CrewAI execution
        from crewai import Crew, Task, Process
        from agents.crew import crop_health_agent
        
        task = Task(
            description=(
                f"Analyze the crop leaf image located at '{file_path}' for crop type '{crop_type}'. "
                "Determine the crop disease, severity, organic treatment, and chemical treatment."
            ),
            expected_output="A structured diagnosis text report containing crop type, disease, severity, organic control, and chemical control.",
            agent=crop_health_agent
        )
        
        crew = Crew(
            agents=[crop_health_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            res_str = str(result)
            disease_detected = "Healthy Leaf"
            for possible_disease in ["Blast", "Curl", "Blight", "Anthracnose"]:
                if possible_disease.lower() in res_str.lower():
                    disease_detected = f"{crop_type.capitalize()} {possible_disease}"
                    break
                    
            report = {
                "agent": "Crop Pathologist and Health Advisor (Live CrewAI)",
                "task_description": "Diagnose crop health from leaf photo.",
                "diagnosis_details": res_str,
                "disease_detected": disease_detected,
                "severity": "High" if "high" in res_str.lower() else "Moderate",
            }
        except Exception as crew_err:
            print(f"CrewAI execution failed: {crew_err}. Falling back to simulation.")
            report = simulate_crop_crew(crop_type=crop_type, image_name=file_path)
            
    # Set uploaded image URL reference
    report["uploaded_image_url"] = f"/uploads/{os.path.basename(file_path)}"
    
    # Save the record in the database for future RAG / PDF report generations
    try:
        db_diag = CropDiagnosis(
            farmer_id=current_user.id,
            crop_type=crop_type,
            disease_detected=report.get("disease_detected", "Healthy"),
            severity=report.get("severity", "None"),
            diagnosis_details=report.get("diagnosis_details", ""),
            image_path=file_path
        )
        db.add(db_diag)
        db.commit()
        db.refresh(db_diag)
        report["id"] = db_diag.id
        
        # Automatically send a crop health WhatsApp advisory alert to the farmer!
        disease_name = report.get("disease_detected", "Healthy Leaf")
        severity = report.get("severity", "None")
        
        if disease_name and "healthy" not in disease_name.lower():
            farmer_phone = current_user.phone_number or "+919999999999"
            wa_phone = f"whatsapp:{farmer_phone}"
            
            warning_msg = (
                f"🌾 KisanMitra Crop Health Alert: Scanning detected '{disease_name}' "
                f"({severity} severity) in your crop. Treatment guidelines are loaded in your Schemes & Subsidy workspace."
            )
            
            try:
                dispatch_sms_alert.func(
                    farmer_id=current_user.id,
                    phone_number=wa_phone,
                    alert_type="Weather",  # Categorized as Weather warning / Crop Health advisory
                    message=warning_msg
                )
                print(f"AUTOMATED ALERT: Sent WhatsApp advisory for '{disease_name}' to {wa_phone}.")
            except Exception as alert_err:
                print(f"AUTOMATED ALERT ERROR: Failed to send auto-alert: {alert_err}")
                
    except Exception as db_err:
        db.rollback()
        print(f"Database logging failed for diagnosis report: {db_err}")
        # Attach dummy ID for UI fallback
        report["id"] = 1

    return report


@router.get("/diagnose/{diagnosis_id}/pdf")
def download_diagnosis_pdf(
    diagnosis_id: int,
    current_user: Farmer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streams a beautifully rendered ReportLab PDF document for a specific crop health diagnosis.
    """
    # Fetch diagnosis
    diag = db.query(CropDiagnosis).filter(
        CropDiagnosis.id == diagnosis_id,
        CropDiagnosis.farmer_id == current_user.id
    ).first()
    
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis report not found.")
        
    # Fetch land profile details
    land = db.query(LandProfile).filter(LandProfile.farmer_id == current_user.id).first()
    land_details = {}
    if land:
        land_details = {
            "state": land.state,
            "district": land.district,
            "village": land.village,
            "crop_type": land.crop_type,
            "land_size_acres": land.land_size_acres,
            "soil_type": land.soil_type
        }
    else:
        land_details = {
            "state": "Andhra Pradesh",
            "district": "Guntur",
            "village": "Amaravati",
            "crop_type": diag.crop_type,
            "land_size_acres": 1.0,
            "soil_type": "N/A"
        }
        
    # PDF output path
    pdf_filename = f"crop_report_{diagnosis_id}.pdf"
    pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
    
    # Prepare details payload for generator
    diag_details = {
        "disease_detected": diag.disease_detected,
        "severity": diag.severity,
        "diagnosis_details": diag.diagnosis_details,
        "simulated": "Simulator" in diag.diagnosis_details or "Simulated" in diag.diagnosis_details or "AGENT" in diag.diagnosis_details
    }
    
    try:
        generate_crop_pdf(
            dest_path=pdf_path,
            farmer_name=current_user.full_name or "Farmer",
            land_details=land_details,
            diagnosis_details=diag_details,
            image_path=diag.image_path
        )
    except Exception as pdf_err:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF document: {pdf_err}")
        
    # Generate user-friendly file name
    display_filename = f"KisanMitra_Report_{diag.crop_type}_{diag.disease_detected.replace(' ', '_')}.pdf"
    
    return FileResponse(
        path=pdf_path,
        filename=display_filename,
        media_type="application/pdf"
    )
