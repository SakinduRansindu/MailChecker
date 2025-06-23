# Updated checkemails.py

import poplib
from email import parser, policy
from notifier import notify_all
import configparser
import time
import ssl
import os

from store import insert_email_check, get_unread_emails_today, get_last_db_record

# Load config
config = configparser.ConfigParser()
config.read("settings.conf")

EMAIL_HOST = config["EMAIL"]["POP_SERVER"]
EMAIL_PORT = int(config["EMAIL"]["POP_PORT"])
EMAIL_USER = config["EMAIL"]["EMAIL_ACCOUNT"]
EMAIL_PASS = config["EMAIL"]["EMAIL_PASSWORD"]
CHECK_INTERVAL = int(config["EMAIL"]["CHECK_INTERVAL"])

def check_mail_pop3():
    try:
        print("connecting to server...")
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT:@SECLEVEL=1')
        pop_conn = poplib.POP3_SSL(EMAIL_HOST, EMAIL_PORT, context=context)
        print("loging to user account", EMAIL_USER)
        pop_conn.user(EMAIL_USER)
        pop_conn.pass_(EMAIL_PASS)
        print("Connected.")

        resp, items, octets = pop_conn.list()
        count = len(items)
        print(f"Total messages: {count}")

        prev_count, prev_sender, prev_subject = get_last_db_record()
        

        if count > 0:
            # Retrieve the most recent email
            resp, lines, octets = pop_conn.retr(count)
            msg_content = b"\r\n".join(lines).decode("utf-8", errors="ignore")
            msg = parser.Parser(policy=policy.default).parsestr(msg_content)

            subject = msg.get("Subject", "(No Subject)")
            sender = msg.get("From", "(Unknown Sender)")
            
            is_changed = (prev_count != count) or (prev_sender != sender) or (prev_subject != subject)
            
            if is_changed:
                # Store in DB
                insert_email_check(email_count=count, last_sender=sender, last_subject=subject)

                # Get unread emails from today
                unread = get_unread_emails_today()
                if unread:
                    message_lines = [f"{s} – {sub}" for s, sub in unread]
                    notify_all("New Emails Today", "\n".join(message_lines))
            else:
                print("No new messages.")
        else:
            print("No messages.")

        pop_conn.quit()
    except Exception as e:
        notify_all("POP3 Error", str(e))
