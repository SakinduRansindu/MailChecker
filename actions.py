import sys
import subprocess
from datetime import datetime
from store import mark_last_as_read
from notifier import clear_termux_notifications, notify_all
from emailChecker import check_mail_pop3

def markAsRead():
    try:
        mark_last_as_read()
        clear_termux_notifications("termux-emailApp-info")
    except subprocess.CalledProcessError as e:
        print(f"Error clearing notifications: {e}")
    except Exception as e:
        print(f"Error: {e}")

def clearErrorNotification():
    try:
        clear_termux_notifications("termux-emailApp-errors")
    except subprocess.CalledProcessError as e:
        print(f"Error clearing error notifications: {e}")
    except Exception as e:
        print(f"Error: {e}")

def notifyStatus():
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] notifying status.")
        notify_all("Email Checker", "Email checker is started and running")
    except Exception as e:
        print(f"Error in notifyStatus: {e}")

def testNotify():
    print("Scheduler is working")
    notify_all("Test Notification", "This is a test notification from the email checker script.")

def emailCheck():
    """Daily comprehensive email check"""
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running daily email check")
        check_mail_pop3()
        print("Daily email check completed successfully")
    except Exception as e:
        print(f"Error in daily email check: {e}")
        notify_all("Daily Check Error", f"Daily email check failed: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python actions.py <function_name>")
        return
    
    function_name = sys.argv[1]
    
    # Function mapping
    functions = {
        'markAsRead': markAsRead,
        'clearErrorNotification': clearErrorNotification,
        'notifyStatus': notifyStatus,
        'testNotify': testNotify,
        'emailCheck': emailCheck,
    }
    
    if function_name in functions:
        print(f"Executing function: {function_name}")
        functions[function_name]()
        print(f"Function {function_name} completed")
    else:
        print(f"Function '{function_name}' not found")
        print(f"Available functions: {list(functions.keys())}")

if __name__ == "__main__":
    main()