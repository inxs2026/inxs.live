#!/usr/bin/env python3
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# Email configuration
sender = "openclaw@localhost"
recipient = "cdamato@rogers.com"
subject = "Gulfstream Picks - February 19, 2026"

# Create message
msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = recipient
msg['Subject'] = subject
msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

# Email body
body = """Hi Carlo,

Your Gulfstream Park picks for today (February 19, 2026) are attached.

Scratches implemented as of 12:15 PM EST:
- Race 1: #9 River Blossom

Analysis includes:
✓ All 10 races with detailed top 3 picks per race
✓ Beyer averages calculated from last 3 races  
✓ Class analysis, trainer angles, pace scenarios
✓ Best bets and value plays highlighted

Best Bets of the Day:
- Race 1: Mi Amada (consistent turf form)
- Race 6: Rocketeer (class edge)
- Race 9: Royal Poppy (allowance drop, speed)

Good luck today!

Chi 🐾
OpenClaw Racing Analysis
"""

msg.attach(MIMEText(body, 'plain'))

# Attach PDF
pdf_path = "Gulfstream_Picks_Feb19_2026.pdf"
if os.path.exists(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                 filename='Gulfstream_Picks_Feb19_2026.pdf')
        msg.attach(pdf_attachment)
    print(f"PDF attached: {pdf_path}")
else:
    print(f"ERROR: PDF not found: {pdf_path}")
    exit(1)

# Send email
try:
    # Try localhost SMTP first
    server = smtplib.SMTP('localhost', 25, timeout=10)
    server.send_message(msg)
    server.quit()
    print(f"Email sent successfully to {recipient}")
except Exception as e:
    print(f"SMTP error: {e}")
    # Save email to file as backup
    with open('email_backup.eml', 'w') as f:
        f.write(msg.as_string())
    print("Email saved to email_backup.eml (SMTP unavailable)")
    exit(1)

