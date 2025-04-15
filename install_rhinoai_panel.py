import rhinoscriptsyntax as rs
import Rhino
import System
import os

def install_commands():
    try:
        # Get the current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rhinoai_path = os.path.join(script_dir, "RhinoAI.py")
        rhinoai_panel_path = os.path.join(script_dir, "RhinoAI_Panel.py")
        
        if not os.path.exists(rhinoai_path):
            print("Error: RhinoAI.py not found in the same directory.")
            return
            
        if not os.path.exists(rhinoai_panel_path):
            print("Error: RhinoAI_Panel.py not found in the same directory.")
            return
        
        # Create the Python command file content
        rhinoai_alias = f'-_RunPythonScript "{rhinoai_path}"'
        rhinoai_panel_alias = f'-_RunPythonScript "{rhinoai_panel_path}"'
        
        # Register the RhinoAI command alias
        if not rs.IsAlias("RhinoAI"):
            rs.AddAlias("RhinoAI", rhinoai_alias)
            print(f"Successfully installed the 'RhinoAI' command!")
        else:
            print(f"The 'RhinoAI' command is already installed.")
            
        # Register the RhinoAIPanel command alias
        if not rs.IsAlias("RhinoAIPanel"):
            rs.AddAlias("RhinoAIPanel", rhinoai_panel_alias)
            print(f"Successfully installed the 'RhinoAIPanel' command!")
        else:
            print(f"The 'RhinoAIPanel' command is already installed.")
        
        print("\nInstallation complete! You can now use the following commands in Rhino:")
        print("- 'RhinoAI' - Run RhinoAI in command line mode")
        print("- 'RhinoAIPanel' - Open the RhinoAI panel interface")
        
    except Exception as e:
        print(f"Error installing commands: {str(e)}")

if __name__ == "__main__":
    install_commands() 