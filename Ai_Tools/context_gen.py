# AI_Tools/context_gen.py — V2.1 (Context saved inside AI_Tools/)
import os
import datetime
import subprocess

WORKFLOW_FILENAME = "WORKFLOW.txt"
ARCHITECTURE_FILENAME = "ARCHITECTURE.txt"
LATEST_CONTEXT_FILENAME = "LATEST_PROJECT_CONTEXT.txt"
BACKUP_DIR_NAME = "context_backups"

IGNORE_DIRS = {'AI_Tools', 'Ai_Tools', 'context_backups', '.git', '.idea', 
               '.vscode', '__pycache__', 'venv', 'env', '.venv', 'build', 
               'dist', '_SNAPSHOTS'}

TEXT_EXTENSIONS = {'.py', '.js', '.html', '.css', '.json', '.xml', '.txt', 
                   '.md', '.yml', '.yaml', '.ini', '.conf', '.kv', '.sql'}

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_ai_tools_path():
    return os.path.dirname(os.path.abspath(__file__))

def read_instruction_file(filename, section_num, section_title):
    ai_path = get_ai_tools_path()
    fpath = os.path.join(ai_path, filename)
    
    result = f"{'#'*40}\n{section_num}. {section_title}\n{'#'*40}\n\n"
    
    if os.path.exists(fpath):
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                result += f.read() + f"\n\n[✅ Loaded: {filename}]\n"
        except Exception as e:
            result += f"[❌ Error: {e}]\n"
    else:
        result += f"[⚠️ {filename} not found]\n"
    
    return result + "\n"

def get_workflow_rules():
    return read_instruction_file(WORKFLOW_FILENAME, "0", "CRITICAL WORKFLOW INSTRUCTIONS")

def get_architecture_spec():
    return read_instruction_file(ARCHITECTURE_FILENAME, "1", "PROJECT ARCHITECTURE")

def generate_tree_structure(root):
    tree = "="*40 + "\n2. PROJECT STRUCTURE\n" + "="*40 + "\n"
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        level = dirpath.replace(root, '').count(os.sep)
        indent = ' ' * 4 * level
        folder = os.path.basename(dirpath) or os.path.basename(root)
        tree += f"{indent}[DIR] {folder}/\n"
        
        for f in filenames:
            tree += f"{' '*4*(level+1)}{f}\n"
    
    return tree + "\n"

def get_installed_packages():
    pkg = "="*40 + "\n3. INSTALLED PACKAGES\n" + "="*40 + "\n"
    
    try:
        result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
        pkg += result.stdout
    except Exception as e:
        pkg += f"Error: {e}\n"
    
    return pkg + "\n"

def get_code_contents(root):
    content = "="*40 + "\n4. FILE CONTENTS\n" + "="*40 + "\n"
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in TEXT_EXTENSIONS:
                full_path = os.path.join(dirpath, f)
                rel_path = os.path.relpath(full_path, root)
                
                content += f"\n{'='*20} START: {rel_path} {'='*20}\n"
                try:
                    with open(full_path, 'r', encoding='utf-8') as file:
                        content += file.read()
                except Exception as e:
                    content += f"[Error: {e}]"
                content += f"\n{'='*20} END: {rel_path} {'='*20}\n"
    
    return content

def create_context_file():
    root = get_project_root()
    ai_tools = get_ai_tools_path()
    now = datetime.datetime.now()
    
    print("="*60)
    print("🔄 CONTEXT GENERATOR V2.1")
    print(f"   Root: {root}")
    print(f"   Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    content = f"GENERATED: {now.strftime('%Y-%m-%d %H:%M:%S')}\nVERSION: 2.1\n\n"
    
    print("   📄 Loading WORKFLOW.txt...")
    content += get_workflow_rules()
    
    print("   📐 Loading ARCHITECTURE.txt...")
    content += get_architecture_spec()
    
    print("   📁 Generating tree...")
    content += generate_tree_structure(root)
    
    print("   📦 Reading packages...")
    content += get_installed_packages()
    
    print("   💻 Reading code...")
    content += get_code_contents(root)
    
    # ═══ KEY: Save inside AI_Tools (not Root) ═══
    latest_path = os.path.join(ai_tools, LATEST_CONTEXT_FILENAME)
    backup_dir = os.path.join(ai_tools, BACKUP_DIR_NAME)
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"context_{now.strftime('%Y%m%d_%H%M%S')}.txt")
    
    try:
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n   ✅ Context saved: {latest_path}")
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ Backup saved: {backup_path}")
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        return False
    
    print("\n" + "="*60)
    print("📊 CONTEXT GENERATION COMPLETE")
    print("="*60)
    return True

if __name__ == "__main__":
    success = create_context_file()
    if success:
        print("\n🎉 Success!")
    else:
        print("\n⚠️ Completed with errors.")
