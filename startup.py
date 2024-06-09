import os
import shutil

def create_startup_script():
    user_profile = os.environ['USERPROFILE']
    desktop_path = os.path.join(user_profile, 'Desktop')
    startup_path = os.path.join(user_profile, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

    wolfpivots_path = os.path.join(desktop_path, 'wolfpivots.py')
    wolfrss_path = os.path.join(desktop_path, 'wolfrss.py')

    if not os.path.exists(wolfpivots_path):
        print(f"File not found: {wolfpivots_path}")
        return

    if not os.path.exists(wolfrss_path):
        print(f"File not found: {wolfrss_path}")
        return

    startup_script_content = f"""@echo off
python "{wolfpivots_path}"
python "{wolfrss_path}"
exit
"""

    batch_file_path = os.path.join(startup_path, 'run_wolf_scripts.bat')
    
    try:
        with open(batch_file_path, 'w') as file:
            file.write(startup_script_content)
        print(f"Batch file created successfully at: {batch_file_path}")
    except Exception as e:
        print(f"Failed to create batch file: {e}")

create_startup_script()
