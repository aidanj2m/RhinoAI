import rhinoscriptsyntax as rs
import Rhino
import System
import os
import shutil

def install_rhinoai():
    try:
        # Get the current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rhinoai_panel_path = os.path.join(script_dir, "RhinoAI_Panel.py")
        
        if not os.path.exists(rhinoai_panel_path):
            print("Error: RhinoAI_Panel.py not found in the same directory.")
            return
            
        # Create the Python command file content
        rhinoai_panel_alias = f'-_RunPythonScript "{rhinoai_panel_path}"'
        
        # Register the RhinoAI command alias
        if not rs.IsAlias("RhinoAI"):
            rs.AddAlias("RhinoAI", rhinoai_panel_alias)
            print(f"Successfully installed the 'RhinoAI' command!")
        else:
            print(f"The 'RhinoAI' command is already installed.")
        
        print("\nInstallation complete! You can now type 'RhinoAI' in the Rhino command line to open the assistant panel.")
        
        # Add startup script to automatically load the panel when Rhino starts
        try:
            rhino_scripts_folder = rs.GetSettings("Directories", "Scripts Folder")
            startup_folder = os.path.join(rhino_scripts_folder, "startup")
            
            # Create startup folder if it doesn't exist
            if not os.path.exists(startup_folder):
                os.makedirs(startup_folder)
            
            # Create a startup script to load RhinoAI
            startup_script_path = os.path.join(startup_folder, "load_rhinoai.py")
            
            with open(startup_script_path, 'w') as f:
                f.write(f'''
# RhinoAI Startup Script
import rhinoscriptsyntax as rs
import os

def load_rhinoai():
    rhinoai_panel_path = r"{rhinoai_panel_path}"
    if os.path.exists(rhinoai_panel_path):
        rs.Command('_-RunPythonScript "{rhinoai_panel_path}" _Enter', False)
        print("RhinoAI Assistant has been loaded.")
    else:
        print("Warning: RhinoAI_Panel.py not found.")

# Run on startup
load_rhinoai()
''')
            print("Added RhinoAI to Rhino startup scripts!")
            
        except Exception as e:
            print(f"Note: Could not add RhinoAI to startup scripts: {str(e)}")
            print("You'll need to run the 'RhinoAI' command manually.")
        
    except Exception as e:
        print(f"Error installing RhinoAI: {str(e)}")

# Run installer
if __name__ == "__main__":
    install_rhinoai() 