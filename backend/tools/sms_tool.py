import os
import httpx
from crewai.tools import tool
from config import settings
from models.database import SessionLocal
from models.models import AlertLog

@tool("Dispatch Farmer SMS Notification Tool")
def dispatch_sms_alert(farmer_id: int, phone_number: str, alert_type: str, message: str) -> str:
    """
    Sends an SMS or WhatsApp alert to a farmer using the Twilio API.
    Inputs:
        farmer_id: Database ID of the farmer receiving the alert.
        phone_number: Mobile number of the farmer with country code (e.g. +91XXXXXXXXXX)
        alert_type: Category of the alert (e.g. 'Weather', 'Market Price', 'Scheme')
        message: The actual SMS text content to send.
    Returns: Dispatch status report.
    """
    sid = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    from_num = settings.TWILIO_FROM_NUMBER
    
    is_whatsapp = phone_number.startswith("whatsapp:")
    status = "WhatsApp Simulated" if is_whatsapp else "Simulated"
    
    # Check if Twilio keys are present
    if sid and token and from_num:
        try:
            # Twilio API request via HTTP Basic Auth
            url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
            
            # Twilio WhatsApp requires prefixing From with whatsapp:
            from_param = f"whatsapp:{from_num}" if is_whatsapp else from_num
            
            data = {
                "From": from_param,
                "To": phone_number,
                "Body": message
            }
            auth = (sid, token)
            
            # Synchronous request
            with httpx.Client() as client:
                response = client.post(url, data=data, auth=auth, timeout=8)
                if response.status_code == 201:
                    status = "WhatsApp Sent" if is_whatsapp else "Sent"
                    print(f"Twilio message sent successfully to {phone_number}.")
                else:
                    status = "WhatsApp Failed" if is_whatsapp else "Failed"
                    print(f"Twilio message failed with status {response.status_code}: {response.text}")
        except Exception as e:
            status = f"WhatsApp Failed ({str(e)})" if is_whatsapp else f"Failed ({str(e)})"
            print(f"Twilio message invocation failed: {e}")
            
    # Save log to Database
    db = SessionLocal()
    try:
        log = AlertLog(
            farmer_id=int(farmer_id),
            alert_type=alert_type,
            message=message,
            status=status
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        print(f"DB Logged alert ID {log.id} with status: {status}")
    except Exception as db_err:
        print(f"Database logging failed for SMS tool: {db_err}")
    finally:
        db.close()
        
    return f"SMS status: {status} | Target: {phone_number} | Type: {alert_type} | Msg: {message}"
