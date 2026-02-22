#!/usr/bin/env python3
"""
Send email with PDF attachment via Gmail SMTP
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

def send_email_with_pdf(to_email, subject, body, pdf_path):
    """Send email with PDF attachment"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add PDF attachment
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
                pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=os.path.basename(pdf_path))
                msg.attach(pdf_attachment)
            print(f"📎 Attached PDF: {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path) / 1024:.1f} KB)")
        else:
            print(f"❌ PDF file not found: {pdf_path}")
            return False
        
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
        print("Usage: python3 send_email_pdf.py <to_email> <subject> <body> <pdf_path>")
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    pdf_path = sys.argv[4]
    
    send_email_with_pdf(to_email, subject, body, pdf_path)
