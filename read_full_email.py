#!/usr/bin/env python3
"""
Get full email content
"""
import imaplib
import email
from email.header import decode_header

EMAIL = "charliethebot1@gmail.com"
APP_PASSWORD = "mbxaezedvcxcjopi"
IMAP_SERVER = "imap.gmail.com"

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, APP_PASSWORD)
mail.select("INBOX")

# Search for latest email from Carlo
status, messages = mail.search(None, 'FROM', '"cdamato@rogers.com"')
message_ids = messages[0].split()

if message_ids:
    # Get the latest email
    latest_id = message_ids[-1]
    status, msg_data = mail.fetch(latest_id, "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])
    
    # Get subject
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()
    
    print(f"Subject: {subject}")
    print(f"From: {msg.get('From')}")
    print("="*60)
    
    # Get body
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True)
                if body:
                    print(body.decode('utf-8', errors='ignore'))
    else:
        body = msg.get_payload(decode=True)
        if body:
            print(body.decode('utf-8', errors='ignore'))

mail.logout()
