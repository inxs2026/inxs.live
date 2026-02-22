#!/usr/bin/env python3
"""
Email Gulfstream picks PDF to Carlo
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Email configuration
FROM_EMAIL = "openclaw@system.local"  # Placeholder
TO_EMAIL = "cdamato@rogers.com"
SUBJECT = "Gulfstream Picks - Thursday Feb 19, 2026"
BODY = """Carlo,

Your Gulfstream Park picks for Thursday, February 19, 2026 are attached.

Scratches implemented as of 12:15 PM EST.

BEST BET: Race 4 - ETON (Highest Beyers on card, class advantage)

All 10 races analyzed with top 3 picks per race using the TOP-3-PICKS-CRITERIA methodology.

Good luck!

- Your Racing Analysis System
"""

PDF_PATH = "Gulfstream_Picks_Feb19_2026.pdf"

# Create message
msg = MIMEMultipart()
msg['From'] = FROM_EMAIL
msg['To'] = TO_EMAIL
msg['Subject'] = SUBJECT

# Add body
msg.attach(MIMEText(BODY, 'plain'))

# Attach PDF
try:
    with open(PDF_PATH, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(PDF_PATH)}')
        msg.attach(part)
    
    print(f"✅ Email prepared successfully")
    print(f"To: {TO_EMAIL}")
    print(f"Subject: {SUBJECT}")
    print(f"Attachment: {PDF_PATH} ({os.path.getsize(PDF_PATH)} bytes)")
    
    # Note: Actual sending would require SMTP configuration
    # For now, save the email content
    with open('email_content.txt', 'w') as f:
        f.write(f"To: {TO_EMAIL}\n")
        f.write(f"Subject: {SUBJECT}\n")
        f.write(f"Attachment: {PDF_PATH}\n\n")
        f.write(BODY)
    
    print("\n📧 Email content saved to email_content.txt")
    print("\n⚠️ NOTE: Actual SMTP sending requires server configuration.")
    print("PDF is ready at: ./Gulfstream_Picks_Feb19_2026.pdf")
    
except Exception as e:
    print(f"❌ Error: {e}")

