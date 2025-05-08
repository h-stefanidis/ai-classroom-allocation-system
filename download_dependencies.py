import os
import subprocess

# Define the directories and their respective requirements files
requirements = {
    "backend": "requirements.txt",
    "ml": "requirements.txt",
    "db": "requirements.txt",
    "frontend": "requirements.txt"
}

def install_requirements(directory, filename):
    path = os.path.join(directory, filename)
    if os.path.exists(path):
        print(f"\n Installing requirements from {path}...")
        try:
            subprocess.check_call(["pip", "install", "-r", path])
            print(f"Installed requirements for {directory}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements in {directory}: {e}")
    else:
        print(f"No requirements.txt found in {directory}, skipping...")

if __name__ == "__main__":
    for dir_name, req_file in requirements.items():
        install_requirements(dir_name, req_file)
