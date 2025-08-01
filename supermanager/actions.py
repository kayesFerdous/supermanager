import subprocess
import os

LOG_FILE = "/tmp/supermanager_debug.log"

def log_debug(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{message}\n")

def get_directory_entries(path, show_hidden):
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "get_dir.sh")
    cmd = [script_path, path]
    if show_hidden:
        cmd.append("--all")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not result.stdout:
        return []
    return result.stdout.strip().split('\n')

def delete_item(path):
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "delete.sh")
    subprocess.run([script_path, path])

def add_item(path):
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "add.sh")
    subprocess.run([script_path, path])

async def find_item(directory, query):
    found_items = []
    query_lower = query.lower()
    try:
        for entry_name in os.listdir(directory):
            if query_lower in entry_name.lower():
                full_path = os.path.join(directory, entry_name)
                if os.path.isdir(full_path):
                    found_items.append(f"dir|{full_path}")
                elif os.path.isfile(full_path):
                    found_items.append(f"file|{full_path}")
    except OSError as e:
        log_debug(f"Error accessing directory {directory}: {e}")
        return []
    return sorted(found_items)

def pin_item(full_path, name, timestamp):
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "pin_item.sh")
    item_data = f"{full_path}|{name}|{timestamp}"
    subprocess.run([script_path, item_data])

def get_pinned_items():    
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "get_pinned_items.sh")    
    result = subprocess.run([script_path], capture_output=True, text=True)    
    if not result.stdout:        
        return []    
    return result.stdout.strip().split('\n')


def unpin_item(full_path):
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "unpin_item.sh")
    subprocess.run([script_path, full_path])

def write_selected_items(items):
    file_path = os.path.join(os.path.dirname(__file__), "scripts", "selected_items.txt")
    with open(file_path, "w") as f:
        for item in items:
            f.write(f"{item}\n")

def get_selected_items():
    file_path = os.path.join(os.path.dirname(__file__), "scripts", "selected_items.txt")
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def paste_items(destination_dir):
    source_paths = get_selected_items()
    if not source_paths:
        return  # Nothing to paste

    script_path = os.path.join(os.path.dirname(__file__), "scripts", "copy.sh")

    # Run the copy script with destination first, then all sources
    log_debug(f"Executing copy command: {[script_path, destination_dir] + source_paths}")
    subprocess.run([script_path, destination_dir, *source_paths])

def move_items(destination_dir):
    source_paths = get_selected_items()
    if not source_paths:
        return  # Nothing to move

    script_path = os.path.join(os.path.dirname(__file__), "scripts", "move.sh")

    # Construct the command list, ensuring each path is a separate argument
    command = [script_path, destination_dir] + source_paths
    log_debug(f"Executing move command: {command}") # Debug print
    subprocess.run(command)
