import configparser
import platform
import subprocess
import os

try:
    from plyer import notification
except:
    notification = None

try:
    from tkinter import messagebox, Tk
except:
    messagebox = None


# Load configuration
config = configparser.ConfigParser()
config.read("settings.conf")

PLATFORM = config["NOTIFY"].get("PLATFORM", "TERMUX").upper()
WIN_NOTIFICATIONS = config.getint("NOTIFY", "WIN_NOTIFICATIONS")
DIALOGBOX_NOTIFICATION = config.getint("NOTIFY", "DIALOGBOX_NOTIFICATION")
TERMUX_NOTIFICATION = config.getint("NOTIFY", "TERMUX_NOTIFICATION")
TERMUX_NOTIFICATION_TONE = config.getint("NOTIFY", "TERMUX_NOTIFICATION_TONE")
TERMUX_VIBRATION = config.getint("NOTIFY", "TERMUX_VIBRATION")


def show_termux_notification(title, message):
    if TERMUX_NOTIFICATION:
        subprocess.run([
            "termux-notification", 
            "--id", "email-receive",
            "--title", title, 
            "--content", message,
            "--button1", "Mark as Read",
            "--button1-action", "python actions.py markAsRead",
            "--action", "python actions.py markAsRead",
            "--channel", "termux-emailApp-info",
            "--priority", "high",
            "--sound",
        ])

def show_termux_error_notification(msg):
    if TERMUX_NOTIFICATION:
        subprocess.run([
            "termux-notification", 
            "--title", "Error",
            "--group", "errors",
            "--content", msg,
            "--button1", "OK",
            "--button1-action", "python actions.py clearErrorNotification",
            "--channel", "termux-emailApp-errors",
            "--vibrate", "pattern", "1000, 2000",
            "--priority", "max",
            "--sound",
        ])

def clear_termux_notifications(channel):
    if TERMUX_NOTIFICATION:
        subprocess.run(["termux-notification", "cancel", "--channel", channel], check=True)

def vibrate_termux_pattern():
    if TERMUX_VIBRATION:
        # Pattern: dot-dot-dot (_._._._)
        for _ in range(4):
            subprocess.run(["termux-vibrate", "-d", "1000"])
            subprocess.run(["sleep", "2"])

def show_tkinter_message(title, message):
    if DIALOGBOX_NOTIFICATION and messagebox:
        root = Tk()
        root.withdraw()
        messagebox.showinfo(title, message)

def show_windows_notification(title, message):
    if WIN_NOTIFICATIONS and notification:
        notification.notify(title=title, message=message, timeout=5)

def notify_all(title, message, id=1):
    if PLATFORM == "TERMUX":
        show_termux_notification(title, message)
        vibrate_termux_pattern()
    elif PLATFORM == "WIN":
        show_windows_notification(title, message)
        show_tkinter_message(title, message)
