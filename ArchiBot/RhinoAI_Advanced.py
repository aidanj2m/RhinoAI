import rhinoscriptsyntax as rs
import Rhino
import Rhino.UI
import scriptcontext as sc
import System
import json
import os
import traceback
import time
import re
from System.Net import WebClient, WebRequest, WebResponse, WebHeaderCollection
from System.Text import Encoding
from System.IO import StreamReader, File
from System.Security import SecureString
from System import Uri, Convert, Environment, Guid
from Rhino.UI import Dialogs
from Rhino.Commands import Result

# Constants
OPENAI_MODEL = "gpt-4"
OPENAI_API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_TEMPERATURE = 0.7
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "RhinoAI_config.json")

# Try multiple possible locations for the .env file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else None
ENV_LOCATIONS = [
    os.path.join(os.getcwd(), ".env"),  # Current working directory
    os.path.join(os.path.expanduser("~"), ".env"),  # User's home directory
]
if SCRIPT_DIR:
    ENV_LOCATIONS.insert(0, os.path.join(SCRIPT_DIR, ".env"))  # Script directory if available

LOG_DIR = os.path.join(os.path.expanduser("~"), "RhinoAI_logs")
MAX_HISTORY = 10  # Maximum number of conversation turns to remember

# Create log directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

SYSTEM_PROMPT = """You are RhinoAI, an advanced assistant for Rhino3D modeling.
Your task is to interpret user prompts and provide Python code using rhinoscriptsyntax (rs) and RhinoCommon
to generate the requested geometry. 

ALWAYS FOLLOW THESE RULES:
1. Generate ONLY valid executable Python code with no explanations or comments
2. Use rhinoscriptsyntax (as rs) and RhinoCommon libraries only
3. When creating objects, always create geometry in the active document
4. Add all objects to the document using rs.AddXXX functions or doc.Objects.Add
5. Use descriptive, unique layer names for organizing geometry
6. For complex geometry, use groups or named objects for better organization
7. Always check if layers exist before using them, create if they don't
8. Clean up any temporary geometry not needed in the final result
9. Include basic error handling in your code
10. Use proper Rhino document scale

Your response must be EXECUTABLE PYTHON CODE ONLY and should create the geometry described by the user.
"""

# Global conversation history
conversation_history = []

def read_env_file():
    """Read the API key from a .env file in multiple possible locations"""
    # Print debug info
    print("Looking for .env file in the following locations:")
    for location in ENV_LOCATIONS:
        print(f"- {location}")
        if os.path.exists(location):
            try:
                with open(location, 'r') as f:
                    env_content = f.read()
                    print(f"Found .env file at: {location}")
                    # Look for OPENAI_API_KEY in the file
                    match = re.search(r'OPENAI_API_KEY=([^\s]+)', env_content)
                    if match:
                        api_key = match.group(1)
                        print("Successfully extracted API key from .env file")
                        return api_key
                    else:
                        print("Could not find OPENAI_API_KEY entry in .env file")
            except Exception as e:
                print(f"Error reading .env file at {location}: {e}")
    
    print("No valid .env file with API key found")
    return None

class RhinoAICommand:
    # The instance running command
    instance = None
    
    def __init__(self):
        self.docSerialNumber = Rhino.RhinoDoc.ActiveDoc.SerialNumber
        self.api_key = None
        self.debug_mode = False
        self.last_generated_ids = []
        
    @staticmethod
    def get_instance():
        """Get the command instance"""
        serial_number = Rhino.RhinoDoc.ActiveDoc.SerialNumber
        if RhinoAICommand.instance is None or RhinoAICommand.instance.docSerialNumber != serial_number:
            RhinoAICommand.instance = RhinoAICommand()
        return RhinoAICommand.instance
    
    def get_api_key(self):
        """Retrieve the OpenAI API key from .env file, environment variable, or config file"""
        # First try to get from .env file
        api_key = read_env_file()
        
        # If not found, try environment variable
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                print("Found API key in environment variables")
                if self.debug_mode:
                    self.log_activity("API Key", "Found in environment variables")
            else:
                print("API key not found in environment variables")
        
        # If still not found, try to get from config file
        if not api_key and os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    api_key = config.get("api_key")
                    if api_key:
                        print(f"Found API key in config file: {CONFIG_FILE}")
                        if self.debug_mode:
                            self.log_activity("API Key", f"Found in config file: {CONFIG_FILE}")
                    else:
                        print(f"No API key found in config file: {CONFIG_FILE}")
            except Exception as e:
                if self.debug_mode:
                    print(f"Error reading config file: {e}")
                    self.log_activity("Error", f"Failed to read config file: {e}")
        
        # If still not found, prompt user using rs.GetString instead of Dialogs.ShowTextEntry
        if not api_key:
            print("OpenAI API key not found. Please enter it below.")
            api_key = rs.GetString("OpenAI API Key")
            if api_key:
                # Save to config file
                try:
                    with open(CONFIG_FILE, 'w') as f:
                        json.dump({"api_key": api_key}, f)
                    print(f"API key saved to config file: {CONFIG_FILE}")
                    if self.debug_mode:
                        self.log_activity("API Key", f"Saved to config file: {CONFIG_FILE}")
                except Exception as e:
                    if self.debug_mode:
                        print(f"Error saving config file: {e}")
                        self.log_activity("Error", f"Failed to save config file: {e}")
        
        self.api_key = api_key
        return api_key
    
    def log_activity(self, action, content):
        """Log activity for debugging and auditing"""
        if not self.debug_mode:
            return
            
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(LOG_DIR, f"rhinoai_log_{time.strftime('%Y%m%d')}.txt")
        
        try:
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] {action}: {content}\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            print(f"Error writing to log: {e}")
    
    def call_openai_api(self, prompt):
        """Make a request to the OpenAI API and return the response"""
        if not self.api_key:
            self.get_api_key()
            
        if not self.api_key:
            print("API key is required to use RhinoAI")
            return None
            
        try:
            # Create the request object
            request = WebRequest.Create(Uri(OPENAI_API_ENDPOINT))
            request.Method = "POST"
            request.ContentType = "application/json"
            request.Headers.Add("Authorization", "Bearer " + self.api_key)
            
            # Create message array with conversation history
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Add conversation history
            for msg in conversation_history:
                messages.append(msg)
                
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Prepare the request payload
            payload = {
                "model": OPENAI_MODEL,
                "messages": messages,
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": 2048
            }
            
            # Convert payload to JSON and encode as bytes
            json_payload = json.dumps(payload)
            bytes_payload = Encoding.UTF8.GetBytes(json_payload)
            
            # Set content length and write request stream
            request.ContentLength = bytes_payload.Length
            using_stream = request.GetRequestStream()
            using_stream.Write(bytes_payload, 0, bytes_payload.Length)
            using_stream.Close()
            
            # Get response
            response = request.GetResponse()
            using_response_stream = response.GetResponseStream()
            using_reader = StreamReader(using_response_stream)
            response_text = using_reader.ReadToEnd()
            
            # Parse JSON response
            response_json = json.loads(response_text)
            ai_response = response_json["choices"][0]["message"]["content"]
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": prompt})
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Limit conversation history size
            while len(conversation_history) > MAX_HISTORY * 2:
                conversation_history.pop(0)
                
            self.log_activity("API Response", ai_response)
            
            return ai_response
        
        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.log_activity("API Error", error_msg)
            return None
    
    def execute_python_code(self, code):
        """Execute the Python code generated by the API"""
        try:
            # Clean up the code to handle code blocks
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
                
            self.log_activity("Executing Code", code)
            
            # Create a list to store IDs of generated objects
            generated_ids = []
            
            # Store original AddObject functions to track created objects
            original_add_curve = rs.AddCurve
            original_add_line = rs.AddLine
            original_add_circle = rs.AddCircle
            original_add_surface = rs.AddSrfPt
            original_add_mesh = rs.AddMesh
            
            # Override AddObject functions to track object IDs
            def track_object(func, *args, **kwargs):
                obj_id = func(*args, **kwargs)
                if obj_id and isinstance(obj_id, System.Guid):
                    generated_ids.append(obj_id)
                return obj_id
                
            # Override key functions to track generated objects
            rs.AddCurve = lambda *args, **kwargs: track_object(original_add_curve, *args, **kwargs)
            rs.AddLine = lambda *args, **kwargs: track_object(original_add_line, *args, **kwargs)
            rs.AddCircle = lambda *args, **kwargs: track_object(original_add_circle, *args, **kwargs)
            rs.AddSrfPt = lambda *args, **kwargs: track_object(original_add_surface, *args, **kwargs)
            rs.AddMesh = lambda *args, **kwargs: track_object(original_add_mesh, *args, **kwargs)
            
            # Execute the code in the global namespace with locals
            exec_globals = globals().copy()
            exec_locals = {"generated_ids": generated_ids}
            exec(code, exec_globals, exec_locals)
            
            # Store the generated IDs for potential future operations
            self.last_generated_ids = generated_ids
            
            # Restore original functions
            rs.AddCurve = original_add_curve
            rs.AddLine = original_add_line
            rs.AddCircle = original_add_circle
            rs.AddSrfPt = original_add_surface
            rs.AddMesh = original_add_mesh
            
            # Ensure all objects are added to document
            sc.doc.Views.Redraw()
            
            return True, generated_ids
            
        except Exception as e:
            error_msg = f"Error executing Python code: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.log_activity("Execution Error", error_msg)
            return False, []
    
    def clear_history(self):
        """Clear the conversation history"""
        global conversation_history
        conversation_history = []
        print("Conversation history cleared")
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode = not self.debug_mode
        print(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")
    
    def undo_last_generation(self):
        """Remove objects from the last generation"""
        if not self.last_generated_ids:
            print("No objects to undo")
            return
            
        for obj_id in self.last_generated_ids:
            rs.DeleteObject(obj_id)
            
        print(f"Removed {len(self.last_generated_ids)} objects from the last generation")
        self.last_generated_ids = []
        sc.doc.Views.Redraw()

def rhinoai_command():
    """Main RhinoAI command function"""
    cmd = RhinoAICommand.get_instance()
    
    # Get API key if not already set
    api_key = cmd.get_api_key()
    if not api_key:
        return Result.Failure
    
    # Get user prompt with options
    options = ["normal", "debug", "clear_history", "undo_last"]
    option_names = {
        "normal": "Normal mode - Enter modeling prompt",
        "debug": "Toggle debug mode",
        "clear_history": "Clear conversation history",
        "undo_last": "Undo last generation"
    }
    
    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt("Enter mode or modeling prompt")
    
    # Add options
    for opt in options:
        go.AddOption(opt)
    
    # Show current mode in the command prompt
    go.AcceptNothing(True)
    
    # Get the option or input
    result = go.Get()
    
    # Process based on the input
    if result == Rhino.Input.GetResult.Option:
        # Option was selected
        selected_option = go.Option().EnglishName
        
        if selected_option == "debug":
            cmd.toggle_debug_mode()
        elif selected_option == "clear_history":
            cmd.clear_history()
        elif selected_option == "undo_last":
            cmd.undo_last_generation()
        
        return Result.Success
        
    elif result == Rhino.Input.GetResult.String:
        # String input was provided
        user_prompt = go.StringResult()
        if not user_prompt:
            return Result.Nothing
            
        print(f"Processing: '{user_prompt}'")
        
        # Call OpenAI API
        print("Contacting OpenAI, please wait...")
        response = cmd.call_openai_api(user_prompt)
        
        if response:
            # Execute the generated code
            print("Executing generated code...")
            success, object_ids = cmd.execute_python_code(response)
            
            if success:
                print(f"Model generation complete - Created {len(object_ids)} objects")
            else:
                print("Failed to execute generated code")
        else:
            print("Failed to get response from OpenAI")
            
        return Result.Success
        
    return Result.Cancel

# Register the command
if __name__ == "__main__":
    # Register as a Rhino command
    try:
        # Use scriptcontext to register the command
        from Rhino.Commands import Command
        from System import Type
        
        class RhinoAIScriptCommand(Command):
            def RunCommand(self, doc, mode):
                return rhinoai_command()
        
        # Attempt to register the command with Rhino
        print("RhinoAI command registered. Use 'RhinoAI' to start.")
    except Exception as e:
        print(f"Error registering command: {e}")
        # Fallback to just running the command
        rhinoai_command() 