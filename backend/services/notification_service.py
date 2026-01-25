import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# Get parent contact info from environment or store in memory
parent_phone = os.getenv("PARENT_PHONE", "")
parent_email = os.getenv("PARENT_EMAIL", "")

# Twilio credentials (optional - for SMS)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE = os.getenv("TWILIO_PHONE", "")

def set_parent_contact(phone: str = "", email: str = ""):
    """Store parent contact info (in-memory for demo)"""
    global parent_phone, parent_email
    if phone:
        parent_phone = phone
    if email:
        parent_email = email
    return {"phone": parent_phone, "email": parent_email}

def send_sms_via_twilio(phone: str, message: str):
    """Send SMS using Twilio API"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE]):
        print("⚠️ Twilio not configured - SMS not sent")
        return False
    
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        data = {
            "From": TWILIO_PHONE,
            "To": phone,
            "Body": message
        }
        
        response = httpx.post(url, auth=auth, data=data, timeout=10.0)
        if response.status_code == 201:
            print(f"✅ SMS sent to {phone}")
            return True
        else:
            print(f"❌ SMS failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ SMS error: {e}")
        return False

def send_email_via_smtp(email: str, subject: str, message: str):
    """Send email notification (simplified - would use SMTP in production)"""
    # For demo: just log it. In production, use smtplib or SendGrid/Mailgun
    print(f"📧 EMAIL TO {email}:")
    print(f"   Subject: {subject}")
    print(f"   Message: {message}")
    print("   (Email service not configured - would send in production)")
    return True

def notify_parent_critical(metric_value: float, status: str, metric_type: str = "glucose"):
    """Automatically notify parent when critical health metric detected"""
    message = f"🚨 ALERT: Your child's {metric_type} is {metric_value}. Status: {status}. Please check immediately!"
    
    sent = False
    
    # Try SMS first
    if parent_phone:
        if TWILIO_ACCOUNT_SID:
            sent = send_sms_via_twilio(parent_phone, message)
        else:
            print(f"📱 SMS would be sent to {parent_phone}: {message}")
            print("   (Add Twilio credentials to .env to enable SMS)")
    
    # Also try email
    if parent_email:
        send_email_via_smtp(
            parent_email,
            f"🚨 Critical {metric_type.title()} Alert",
            message
        )
        sent = True
    
    if not sent and not parent_phone and not parent_email:
        print("⚠️ No parent contact info configured - notification not sent")
    
    return sent
