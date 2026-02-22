#!/usr/bin/env python3
"""
Check Gmail inbox via IMAP
"""
import imaplib
import email
from email.header import decode_header
import sys

# Credentials
EMAIL = "charliethebot1@gmail.com"
APP_PASSWORD = "mbxaezedvcxcjopi"
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def check_inbox():
    try:
        # Connect to Gmail IMAP
        print(f"Connecting to {IMAP_SERVER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        
        # Login
        print(f"Logging in as {EMAIL}...")
        mail.login(EMAIL, APP_PASSWORD)
        
        # Select inbox
        mail.select("INBOX")
        
        # Search for all emails
        status, messages = mail.search(None, "ALL")
        
        if status != "OK":
            print("Failed to search inbox")
            return
        
        # Get message IDs
        message_ids = messages[0].split()
        total = len(message_ids)
        
        print(f"\n✅ Successfully connected!")
        print(f"📧 Total emails in inbox: {total}")
        
        # Get last 5 emails
        print("\n--- Last 5 emails ---\n")
        for msg_id in message_ids[-5:]:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            
            if status != "OK":
                continue
                
            # Parse email
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Decode subject
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            # Get sender
            from_ = msg.get("From")
            
            # Get date
            date = msg.get("Date")
            
            print(f"From: {from_}")
            print(f"Date: {date}")
            print(f"Subject: {subject}")
            print("-" * 50)
        
        # Logout
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_inbox()
