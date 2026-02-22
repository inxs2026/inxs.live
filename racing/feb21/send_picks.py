#!/usr/bin/env python3
"""
Send Gulfstream picks via email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# Credentials
FROM_EMAIL = "charliethebot1@gmail.com"
APP_PASSWORD = "mbxaezedvcxcjopi"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email_with_attachment(to_email, subject, body, file_path):
    """Send email with file attachment"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 
                              f'attachment; filename={os.path.basename(file_path)}')
                msg.attach(part)
            print(f"📎 Attached: {os.path.basename(file_path)} ({os.path.getsize(file_path) / 1024:.1f} KB)")
        else:
            print(f"❌ File not found: {file_path}")
            return False
        
        # Connect and send
        print(f"Connecting to {SMTP_SERVER}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(FROM_EMAIL, APP_PASSWORD)
        
        print(f"Sending to {to_email}...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    to_email = "cdamato@rogers.com"
    subject = "Gulfstream Feb 21 - CORRECTED Picks (All 12 Races)"
    
    body = """Attached are the corrected Gulfstream Park picks for February 21, 2026.

CRITICAL CHANGES - SCRATCHES REMOVED:
• Race 1: #13 Mia Familia SCRATCHED (was #1 pick) → New #1: #7 Three to G
• Race 5: #3 Miss Candy Girl SCRATCHED (was #2 pick) → Reanalyzed remaining field
• Race 8: #1 Life's Too Short SCRATCHED → 7-horse field
• Race 9: #4 Siyouni Flash, #8 Afrodita SCRATCHED → Reanalyzed
• Race 11: 4 SCRATCHES including #8 Mi Triguena (was #3 pick) → Completely reanalyzed
• Race 12: 4 SCRATCHES including original contenders → Reanalyzed

METHODOLOGY APPLIED:
✓ Beyer averages calculated for ALL remaining contenders
✓ Post positions verified (#X HORSE NAME format)
✓ Comment lines analyzed for excuses/trouble
✓ Recent form patterns evaluated
✓ Trainer/jockey statistics from DRF
✓ Class analysis (drops, proven at level)
✓ Pace scenarios considered
✓ Surface/distance fit analyzed

ALL 12 RACES ANALYZED - No scratched horses in any selections.

Best Bets highlighted:
• Race 10: Damon's Mound (stakes winner, dominant figures)
• Race 3: Outlaw Country/Gallant Knight exacta box (class drop/hot form)
• Race 6: Ivory and Ebony (best figures by 10+ points)

In Beyers We Trust 🐴📊

- Charlie/Carlo's Racing System
TOP-3-PICKS-METHODOLOGY.md v2.0"""
    
    file_path = "/home/damato/.openclaw/workspace/racing/feb21/gulfstream_feb21_picks_CORRECTED.md"
    
    send_email_with_attachment(to_email, subject, body, file_path)
