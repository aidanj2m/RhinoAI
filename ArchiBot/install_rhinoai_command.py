import rhinoscriptsyntax as rs
import Rhino
import System
import os

def install_command():
    try:
        # Get the current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rhinoai_path = os.path.join(script_dir, "RhinoAI.py")
        
        if not os.path.exists(rhinoai_path):
            print("Error: RhinoAI.py not found in the same directory.")
            return
        
        # Create the Python command file content
        alias_command = f'-_RunPythonScript "{rhinoai_path}"'
        
        # Create the command alias
        command_name = "RhinoAI"
        
        # Register the alias directly in Rhino
        if not rs.IsAlias(command_name):
            rs.AddAlias(command_name, alias_command)
            print(f"Successfully installed the '{command_name}' command!")
        else:
            print(f"The '{command_name}' command is already installed.")
        
        print("You can now type 'RhinoAI' in Rhino's command line to run the assistant.")
        
    except Exception as e:
        print(f"Error installing command: {str(e)}")

if __name__ == "__main__":
    install_command() 