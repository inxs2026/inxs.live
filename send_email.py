#!/usr/bin/env python3
"""
Send email via Gmail SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import sys
import os

# Credentials
FROM_EMAIL = "charliethebot1@gmail.com"
APP_PASSWORD = "mbxaezedvcxcjopi"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(to_email, subject, body, attachment_path=None):
    """Send email with optional attachment"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype="txt")
                attachment.add_header('Content-Disposition', 'attachment', 
                                    filename=os.path.basename(attachment_path))
                msg.attach(attachment)
            print(f"📎 Attached: {os.path.basename(attachment_path)}")
        
        # Connect to SMTP server
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        
        # Login
        print(f"Logging in as {FROM_EMAIL}...")
        server.login(FROM_EMAIL, APP_PASSWORD)
        
        # Send email
        print(f"Sending to {to_email}...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 send_email.py <to_email> <subject> <body> [attachment_path]")
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    attachment = sys.argv[4] if len(sys.argv) > 4 else None
    
    send_email(to_email, subject, body, attachment)
