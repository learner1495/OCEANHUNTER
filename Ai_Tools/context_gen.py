
import os
import datetime

# CONFIG
OUTPUT_FILE = "LATEST_PROJECT_CONTEXT.txt"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# Folders to scan
INCLUDE_DIRS = ['AI_Tools', 'modules', 'tests'] 
EXCLUDE_DIRS = ['.git', '.venv', '__pycache__', 'context_backups', 'data', 'logs', 'candles', 'wallets', 'orderbooks']
# Note: We exclude raw data folders inside 'tests' from context to keep context small, 
# but include 'tests/core', 'tests/runners' etc.

EXTENSIONS = ['.py', '.txt', '.md', '.json', '.env']

def get_tree(startpath):
    tree = ""
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if any(f.endswith(ext) for ext in EXTENSIONS):
                tree += f"{subindent}{f}\n"
    return tree

def read_files(startpath):
    content = ""
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            # Skip large data files even if json/txt
            if "LATEST_PROJECT_CONTEXT" in f: continue
            
            if any(f.endswith(ext) for ext in EXTENSIONS):
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, startpath)
                
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        content += f"\n{'='*20}\nFile: {rel_path}\n{'='*20}\n"
                        content += file.read() + "\n"
                except Exception as e:
                    content += f"\nError reading {rel_path}: {e}\n"
    return content

def create_context_file():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    header = f"GENERATED: {timestamp}\n"
    header += f"VERSION: 3.1 (Phase 1: Virtual Wallet)\n\n"
    
    structure = "PROJECT STRUCTURE:\n" + get_tree(ROOT_DIR)
    file_contents = "\nFILE CONTENTS:\n" + read_files(ROOT_DIR)
    
    full_content = header + structure + file_contents
    
    output_path = os.path.join(SCRIPT_DIR, OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"✅ Context generated at: {output_path}")

if __name__ == "__main__":
    create_context_file()
