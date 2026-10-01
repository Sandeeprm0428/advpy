import os
import subprocess
import sys
import shutil

# --- CONFIGURATION SETTINGS ---
REPO_URL = "https://github.com/Sandeeprm0428/Advocate-Hub.git"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(ROOT_DIR, "workspace")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
REPO_NAME = "Advocate-Hub"
REPO_PATH = os.path.join(WORKSPACE_DIR, REPO_NAME)

def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

def initialize_environment():
    """Creates workspace/logs and clones/updates the repository automatically."""
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    if not os.path.exists(REPO_PATH):
        print(f"[*] Cloning repository from {REPO_URL} into {REPO_PATH}...")
        result = subprocess.run(["git", "clone", REPO_URL, REPO_PATH], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Failed to clone repository:\n{result.stderr}")
            sys.exit(1)
        print("[SUCCESS] Repository cloned successfully.\n")
    else:
        print("[*] Repository already exists. Pulling latest changes...")
        subprocess.run(["git", "-C", REPO_PATH, "pull"], capture_output=True, text=True)
        print("[SUCCESS] Repository updated.\n")

def setup_backend_environment(backend_dir):
    """Installs backend dependencies and runs the native setup-env.js script."""
    print(f"[*] Target Backend Directory: {backend_dir}")

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    # 1. Install backend dependencies first so setup-env.js and packages work properly
    package_json = os.path.join(backend_dir, "package.json")
    if os.path.exists(package_json):
        if not shutil.which("npm"):
            print("[ERROR] Node.js/npm is not found in your system PATH. Please install Node.js.")
            sys.exit(1)
        print("[*] Installing backend dependencies (npm install)...")
        subprocess.run([npm_cmd, "install"], cwd=backend_dir, check=True)

    # 2. Run the repository's native setup-env.js script if available
    setup_script = os.path.join(backend_dir, "setup-env.js")
    if os.path.exists(setup_script):
        print("[*] Running native environment generator: node setup-env.js admin@law4u.in...")
        res = subprocess.run(
            ["node", "setup-env.js", "admin@law4u.in", "Admin@123"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            print("[SUCCESS] Environment configured successfully via setup-env.js.\n")
        else:
            print(f"[WARNING] setup-env.js execution details:\n{res.stdout}\n{res.stderr}\n")
    else:
        print("[-] setup-env.js not found, skipping script execution.\n")

    # 3. Check for python requirements if any
    backend_req = os.path.join(backend_dir, "requirements.txt")
    if os.path.exists(backend_req) and backend_dir != os.path.join(REPO_PATH, "chatbot"):
        print("[*] Installing Python backend requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=backend_dir, check=True)

def run_chatbot_service():
    """Step 1: Setup and run the Chatbot service."""
    print("=" * 60)
    print("            STEP 1: CHATBOT SERVICE")
    print("=" * 60)
    
    chatbot_dir = os.path.join(REPO_PATH, "chatbot")
    if not os.path.exists(chatbot_dir):
        chatbot_dir = REPO_PATH
    
    print(f"[*] Target Chatbot Directory: {chatbot_dir}")

    venv_path = os.path.join(chatbot_dir, "san")
    if not os.path.exists(venv_path):
        print("[*] Creating virtual environment 'san'...")
        subprocess.run([sys.executable, "-m", "venv", "san"], cwd=chatbot_dir, check=True)
    
    pip_executable = os.path.join(venv_path, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(venv_path, "bin", "pip")
    if not os.path.exists(pip_executable):
        pip_executable = "pip"

    req_file = os.path.join(chatbot_dir, "requirements.txt")
    if os.path.exists(req_file):
        print("[*] Installing chatbot requirements...")
        subprocess.run([pip_executable, "install", "-r", "requirements.txt"], cwd=chatbot_dir, check=True)

    print("[*] Launching Chatbot app...")
    if os.name == "nt":
        subprocess.Popen(f'start cmd /k "cd /d {chatbot_dir} && call san\\Scripts\\activate && python app.py"', shell=True)
    else:
        subprocess.Popen(['xterm', '-hold', '-e', f'cd {chatbot_dir} && source san/bin/activate && python app.py'])
    print("[SUCCESS] Chatbot service launched in a new window!\n")

def run_frontend_service():
    """Step 2: Setup and run the Frontend service."""
    print("=" * 60)
    print("            STEP 2: FRONTEND SERVICE")
    print("=" * 60)

    frontend_dir = os.path.join(REPO_PATH, "frontend", "myapp")
    if not os.path.exists(frontend_dir):
        frontend_dir = os.path.join(REPO_PATH, "frontend")
    if not os.path.exists(frontend_dir):
        frontend_dir = REPO_PATH

    print(f"[*] Target Frontend Directory: {frontend_dir}")

    if not shutil.which("npm"):
        print("[ERROR] Node.js/npm is not found in your system PATH. Please install Node.js.")
        return

    print("[*] Installing frontend dependencies (npm install)...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    subprocess.run([npm_cmd, "install"], cwd=frontend_dir, check=True)

    print("[*] Starting React frontend (npm start)...")
    if os.name == "nt":
        subprocess.Popen(f'start cmd /k "cd /d {frontend_dir} && npm start"', shell=True)
    else:
        subprocess.Popen(['xterm', '-hold', '-e', f'cd {frontend_dir} && npm start'])
    print("[SUCCESS] Frontend service launched in a new window!\n")

def run_backend_service():
    """Step 3: Setup and run the Backend service."""
    print("=" * 60)
    print("            STEP 3: BACKEND SERVICE")
    print("=" * 60)

    backend_dir = os.path.join(REPO_PATH, "backend")
    if not os.path.exists(backend_dir):
        backend_dir = REPO_PATH

    # Setup environment & run setup-env.js automatically
    setup_backend_environment(backend_dir)

    script_candidates = ["backend.py", "server.py", "app.py", "main.py", "index.js", "server.js"]
    target_script = "server.js"
    for script in script_candidates:
        if os.path.exists(os.path.join(backend_dir, script)) and script != "app.py":
            target_script = script
            break

    print(f"[*] Launching Backend service ({target_script})...")
    if os.name == "nt":
        if target_script.endswith(".js"):
            subprocess.Popen(f'start cmd /k "cd /d {backend_dir} && node {target_script}"', shell=True)
        else:
            subprocess.Popen(f'start cmd /k "cd /d {backend_dir} && python {target_script}"', shell=True)
    else:
        runner = f"node {target_script}" if target_script.endswith(".js") else f"python {target_script}"
        subprocess.Popen(['xterm', '-hold', '-e', f'cd {backend_dir} && {runner}'])
    print("[SUCCESS] Backend service launched in a new window!\n")

def main():
    clear_screen()
    print("=" * 60)
    print("       ADVOCATE-HUB MASTER AUTO-SETUP (ALL-IN-ONE)")
    print("=" * 60)
    print()

    # 1. Clone repository & set up folders
    initialize_environment()

    # 2. Run all services automatically in sequence: Chatbot -> Frontend -> Backend
    try:
        run_chatbot_service()
        run_frontend_service()
        run_backend_service()

        print("=" * 60)
        print("[COMPLETE] All Advocate-Hub services have been launched!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] An error occurred during setup: {e}")
    
    input("\nPress Enter to exit setup...")

if __name__ == "__main__":
    main()
