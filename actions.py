import sys
import subprocess
from store import mark_last_as_read
from notifier import clear_termux_notifications

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

def main():
    if len(sys.argv) < 2:
        print("Usage: python actions.py <function_name>")
        return
    
    function_name = sys.argv[1]
    
    # Function mapping
    functions = {
        'markAsRead': markAsRead,
        "clearErrorNotification": clearErrorNotification,
        # Add more functions here as needed
    }
    
    if function_name in functions:
        functions[function_name]()
    else:
        print(f"Function '{function_name}' not found")
        print(f"Available functions: {list(functions.keys())}")

if __name__ == "__main__":
    main()