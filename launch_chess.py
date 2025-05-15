import os
import subprocess
import sys

# Get the directory where the launcher script is located (i.e., project root directory)
project_root_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to main/main.py
main_game_script = os.path.join(project_root_dir, "main", "main.py")

# Use the Python interpreter currently running the launcher to execute the game script
python_executable = sys.executable

print(f"Project root directory: {project_root_dir}")
print(f"Game script to be executed: {main_game_script}")
print(f"Python interpreter used: {python_executable}")

try:
    # Execute the game script as a module in the project root directory
    # This ensures that relative paths and relative imports in main/main.py can be resolved correctly
    # Command: python -m main.main
    process = subprocess.Popen([python_executable, "-m", "main.main"], cwd=project_root_dir)
    process.wait()  # Wait for the game process to end
    print("Game has been closed.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while starting the game: {e}")
except FileNotFoundError:
    print(f"Error: Cannot find Python interpreter '{python_executable}' or game script '{main_game_script}'.")
except Exception as e:
    print(f"An unknown error occurred: {e}")