"""
Authentication service for OTP and OAuth
"""
import random
import string
import re
from flask import current_app

def generate_otp(length=6):
    """Generate random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def validate_phone_number(phone):
    """Validate Indian phone number format"""
    pattern = r'^(\+91|91|0)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

def send_otp_sms(phone, otp_code):
    """Send OTP via SMS using Twilio"""
    try:
        # Check if Twilio is properly configured
        sid = current_app.config.get("TWILIO_SID")
        auth_token = current_app.config.get("TWILIO_AUTH_TOKEN")
        from_phone = current_app.config.get("TWILIO_PHONE")
        messaging_service_sid = current_app.config.get("TWILIO_MESSAGING_SERVICE_SID")
        
        if not sid or not auth_token:
            current_app.logger.warning("Twilio SID and Auth Token are required for SMS")
            return False
        
        if not from_phone and not messaging_service_sid:
            current_app.logger.warning("Either TWILIO_PHONE or TWILIO_MESSAGING_SERVICE_SID is required")
            return False
        
        # Try to import Twilio with better error handling
        try:
            from twilio.rest import Client as TwilioClient
        except ImportError as import_err:
            current_app.logger.error(f"Twilio library not available: {import_err}")
            current_app.logger.info("Install with: pip install twilio==8.10.0")
            return False
        
        client = TwilioClient(sid, auth_token)
        
        # Build message parameters
        msg_params = {
            "body": f"Your VediSpeak OTP is: {otp_code}. Valid for 10 minutes.",
            "to": phone
        }
        
        # Use messaging service if available, otherwise use from_phone
        if messaging_service_sid:
            msg_params["messaging_service_sid"] = messaging_service_sid
        else:
            msg_params["from_"] = from_phone
        
        message = client.messages.create(**msg_params)
        
        current_app.logger.info(f"SMS sent successfully: {message.sid}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS: {e}")
        return False

def send_otp_email(email, otp_code):
    """Send OTP via email using SendGrid"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        api_key = current_app.config.get("SENDGRID_API_KEY")
        from_email = current_app.config.get("SENDGRID_FROM_EMAIL", "hypersickthe@gmail.com")
        
        if not api_key:
            current_app.logger.warning("SendGrid API key not configured")
            return False
        
        message = Mail(
            from_email='hypersickthe@gmail.com',  # Use verified sender email
            to_emails=email,
            subject='VediSpeak OTP Verification',
            html_content=f'''
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                        <h1 style="color: white; margin: 0;">VediSpeak</h1>
                        <p style="color: white; margin: 5px 0;">Indian Sign Language Platform</p>
                    </div>
                    <div style="padding: 30px; background: #f8f9fa;">
                        <h2 style="color: #333;">OTP Verification</h2>
                        <p style="font-size: 16px; color: #555;">Your verification code is:</p>
                        <div style="background: #e3f2fd; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                            <span style="font-size: 32px; font-weight: bold; color: #1976d2; letter-spacing: 4px;">{otp_code}</span>
                        </div>
                        <p style="color: #666; font-size: 14px;">This code is valid for 10 minutes.</p>
                        <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                    </div>
                    <div style="background: #333; color: white; padding: 15px; text-align: center; font-size: 12px;">
                        <p>© 2024 VediSpeak - Making ISL accessible to everyone</p>
                    </div>
                </body>
            </html>
            '''
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        current_app.logger.info(f"Email sent successfully: {response.status_code}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        return False
