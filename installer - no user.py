import os
import sys
import subprocess

MODULES_TO_INSTALL = ['numpy', 'pandas', 'openpyxl']
CONFLICTING_FILE_NAMES = {'numpy.py', 'pandas.py', 'random.py', 'string.py'}
PATH = sys.executable

def in_venv() -> bool:
    # True for both venv and virtualenv
    return hasattr(sys, "real_prefix") or (getattr(sys, "base_prefix", sys.prefix) != sys.prefix)

def pip_cmd(*extra):
    """Build a pip command that avoids --user in venvs."""
    base = [PATH, "-m", "pip"]
    return base + list(extra)

def update_pip():
    print('Upgrading pip to latest version... \n')
    cmd = pip_cmd("install", "--upgrade", "pip")
    # Only add --user if NOT in a venv
    if not in_venv():
        cmd.insert(3, "--user")  # after "install"
    subprocess.run(cmd, check=True)

def install_module(module):
    print(f'Installing {module}... \n')
    cmd = pip_cmd("install", "--upgrade", "--force-reinstall",
                  "--no-cache-dir", "--no-warn-script-location", module)
    if not in_venv():
        cmd.insert(3, "--user")
    subprocess.run(cmd, check=True)

def check_for_conflicting_files():
    has_conflicts = False
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for file in files:
        if file.lower() in CONFLICTING_FILE_NAMES:
            print(f"IMPORTANT WARNING: '{file}' in this folder will conflict with numpy/matplotlib.")
            print("Please rename/remove it, then run this again.\n")
            has_conflicts = True
    return has_conflicts

def main():
    print(f'Python executable at: {PATH}\n')
    if check_for_conflicting_files():
        return
    update_pip()
    try:
        for module in MODULES_TO_INSTALL:
            install_module(module)
    except subprocess.CalledProcessError:
        for module in ['msvc-runtime'] + MODULES_TO_INSTALL:
            install_module(module)
    print('Done. If you’re in PyCharm, no restart is needed; Wing message can be ignored.')

if __name__ == "__main__":
    main()
