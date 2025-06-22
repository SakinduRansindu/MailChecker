import configparser
import subprocess
import sys
import os
from datetime import datetime

def load_config():
    if not os.path.exists("settings.conf"):
        print("ERROR: settings.conf not found. Please copy from settings.conf.example")
        return None
    
    config = configparser.ConfigParser()
    config.read("settings.conf")
    print("Configuration loaded successfully")
    return config

def parse_cron_tasks(config):
    """Parse the TASKS configuration and return list of cron entries"""
    if not config.has_section("SCHEDULES"):
        print("No [SCHEDULES] section found in settings.conf")
        return []
    
    enabled = config.getboolean("SCHEDULES", "ENABLED", fallback=False)
    if not enabled:
        print("Scheduled tasks are disabled in configuration")
        return []
    
    tasks_str = config.get("SCHEDULES", "TASKS", fallback="")
    if not tasks_str.strip():
        print("No tasks defined in SCHEDULES.TASKS")
        return []
    
    tasks = []
    for task in tasks_str.split(","):
        task = task.strip()
        if not task:
            continue
            
        # Expected format: "20 9 * * * scheduledTask5"
        parts = task.split()
        if len(parts) < 6:
            print(f"Invalid task format: {task}")
            print("Expected format: 'minute hour day month weekday functionName'")
            continue
        
        # Cron schedule (first 5 parts) + function name (last part)
        cron_schedule = " ".join(parts[:5])
        function_name = parts[5]
        
        tasks.append((cron_schedule, function_name))
        print(f"Parsed task: {cron_schedule} -> {function_name}")
    
    return tasks

def add_cronjob(cron_schedule, function_name):
    try:
        # Get current working directory
        work_dir = os.path.dirname(os.path.abspath(__file__))
          # Create the command to run
        command = f"cd {work_dir} && python actions.py {function_name}"
        
        # Create unique identifier comment (replace spaces with underscores for safety)
        safe_schedule = cron_schedule.replace(' ', '_')
        unique_id = f"# MailChecker-{function_name}-{safe_schedule}"
        
        # Full cron entry with unique identifier
        cron_entry = f"{cron_schedule} {command} {unique_id}"
        
        print(f"Adding cron job: {cron_entry}")
        
        # Get current crontab
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current_crontab = result.stdout if result.returncode == 0 else ""        # Check if job already exists using unique identifier
        safe_schedule = cron_schedule.replace(' ', '_')
        if f"MailChecker-{function_name}-{safe_schedule}" in current_crontab:
            print(f"Cron job for {function_name} already exists. Removing old one first...")
            if not remove_cronjob(function_name, cron_schedule):
                print(f"Failed to remove existing cron job for {function_name}")
                return False
            print(f"Old cron job removed. Adding new one...")
            # Get updated crontab after removal
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""
        
        # Add new job
        new_crontab = current_crontab + cron_entry + "\n"
        
        # Write to crontab
        process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            print(f"Successfully added cron job for {function_name}")
            return True
        else:
            print(f"Failed to add cron job for {function_name}")
            return False
            
    except Exception as e:
        print(f"Error adding cron job: {e}")
        return False

def remove_cronjob(function_name, cron_schedule=None):
    try:
        print(f"Removing cron job for: {function_name}")
        
        # Get current crontab
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode != 0:
            print("No existing crontab found")
            return True
        
        current_crontab = result.stdout
        
        # Create unique identifier to match
        if cron_schedule:
            safe_schedule = cron_schedule.replace(' ', '_')
            unique_id = f"MailChecker-{function_name}-{safe_schedule}"
        else:
            # Fallback: remove any job with this function name
            unique_id = f"MailChecker-{function_name}"
        
        new_lines = []
        removed = False
        for line in current_crontab.split('\n'):
            if unique_id not in line:
                new_lines.append(line)
            else:
                print(f"Removing: {line.strip()}")
                removed = True
        
        if not removed:
            print(f"No cron job found for {function_name}")
            return True
        
        # Write new crontab
        new_crontab = '\n'.join(new_lines)
        process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            print(f"Successfully removed cron job for {function_name}")
            return True
        else:
            print(f"Failed to remove cron job for {function_name}")
            return False
            
    except Exception as e:
        print(f"Error removing cron job: {e}")
        return False

def list_cronjobs():
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode == 0:
            print("=== Current Cron Jobs ===")
            if result.stdout.strip():
                print(result.stdout)
            else:
                print("No cron jobs found")
        else:
            print("No crontab found or error accessing crontab")
    except Exception as e:
        print(f"Error listing cron jobs: {e}")

def setup_all_jobs():
    config = load_config()
    if not config:
        return False
    
    tasks = parse_cron_tasks(config)
    if not tasks:
        print("No valid tasks to schedule")
        return False
    
    print(f"Setting up {len(tasks)} cron jobs...")
    
    success_count = 0
    for cron_schedule, function_name in tasks:
        if add_cronjob(cron_schedule, function_name):
            success_count += 1
    
    print(f"Successfully set up {success_count}/{len(tasks)} cron jobs")
    return success_count > 0

def remove_all_jobs():
    config = load_config()
    if not config:
        return False
    
    tasks = parse_cron_tasks(config)
    if not tasks:
        print("No tasks found to remove")
        return True
    
    print(f"Removing {len(tasks)} cron jobs...")
      success_count = 0
    for cron_schedule, function_name in tasks:
        if remove_cronjob(function_name, cron_schedule):
            success_count += 1
    
    print(f"Successfully removed {success_count}/{len(tasks)} cron jobs")
    return success_count > 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python scheduler.py <command>")
        print("Commands:")
        print("  setup    - Setup all cron jobs from settings.conf")
        print("  remove   - Remove all MailChecker cron jobs")
        print("  list     - List current cron jobs")
        print("  add <cron_schedule> <function> - Add single cron job")
        print("  del <function> - Remove single cron job")
        print("")
        print("Examples:")
        print("  python scheduler.py setup")
        print("  python scheduler.py add '20 9 * * *' scheduledTask1")
        print("  python scheduler.py del scheduledTask1")
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        setup_all_jobs()
    elif command == "remove":
        remove_all_jobs()
    elif command == "list":
        list_cronjobs()
    elif command == "add" and len(sys.argv) >= 4:
        cron_schedule = sys.argv[2]
        function_name = sys.argv[3]
        add_cronjob(cron_schedule, function_name)
    elif command == "del" and len(sys.argv) >= 3:
        function_name = sys.argv[2]
        remove_cronjob(function_name)
    else:
        print(f"Unknown command: {command}")
        print("Use 'python scheduler.py' to see available commands")

if __name__ == "__main__":
    main()