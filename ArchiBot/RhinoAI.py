import rhinoscriptsyntax as rs
import Rhino
import Rhino.UI
import scriptcontext as sc
import System
import json
import os
import traceback
import re
from System.Net import WebClient, WebRequest, WebResponse, WebHeaderCollection
from System.Text import Encoding
from System.IO import StreamReader, File
from System.Security import SecureString
from System import Uri, Convert, Environment
from Rhino.UI import Dialogs
import math

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

SYSTEM_PROMPT = """You are an expert Rhino 3D Python scripting assistant, specializing in precise 2D drawing editing, detailed annotation, and advanced layer management within Rhino 8. Generate clear, efficient, and robust Python scripts adhering strictly to these guidelines:

### 1. High-Quality 2D Drawing Edits and Enhancements:

A. Poche (Section Hatch Fills):
- "Poche" means solid hatch fills emphasizing architectural section cuts.
- Create poche by:
  - Identifying or generating closed boundary curves outlining hatch areas.
  - Applying appropriate hatch patterns and fills based on architectural standards.
  - Managing fills through proper layer organization.
- Place poche on a dedicated layer named "Poche".

B. Scale Figures:
- Interpret user descriptions (e.g., "standing," "seated," "walking figures").
- Generate minimal, clean vector representations at correct architectural scales (~1.8 meters height unless otherwise stated).
- Position logically based on user inputs or selection points.
- Use layer "Scale_Figures".

C. Enhancing Make2D Outputs:
- Recognize common Make2D issues (fragmented curves, duplicates).
- Join fragmented curves and remove duplicates when appropriate.
- Optimize geometry for clarity and efficiency.

### 2. Advanced Rhino Layer Management:

- Always organize and manage geometry on clearly named layers reflecting their function, including:
  - "Heavy_Lineweight": Strong plot-weight, solid visible lines.
  - "Hidden_Lines": Dashed lines (use Rhino's default "Hidden" linetype).
  - "Poche": Solid fill hatch layers.
  - "Scale_Figures": Human scale figure elements.
- Set unique, distinguishable colors for each layer.
- Assign clear lineweights (plot weights) and linetypes when appropriate.
- Check if layers or linetypes exist before creation to prevent duplication errors.

### 3. Script Robustness and Usability:

- Write modular, commented, reusable Python code.
- Provide adjustable parameters clearly defined at the top.
- Anticipate edge cases and provide descriptive error handling.
- Focus on clean geometry, optimized for further editing by users."""

def read_env_file():
    """Read the API key from a .env file in multiple possible locations"""
    # Print debug info
    print("Looking for .env file in the following locations:")
    for location in ENV_LOCATIONS:
        print("- {}".format(location))
        if os.path.exists(location):
            try:
                with open(location, 'r') as f:
                    env_content = f.read()
                    print("Found .env file at: {}".format(location))
                    # Look for OPENAI_API_KEY in the file
                    match = re.search(r'OPENAI_API_KEY=([^\s]+)', env_content)
                    if match:
                        api_key = match.group(1)
                        print("Successfully extracted API key from .env file")
                        return api_key
                    else:
                        print("Could not find OPENAI_API_KEY entry in .env file")
            except Exception as e:
                print("Error reading .env file at {}: {}".format(location, e))
    
    print("No valid .env file with API key found")
    return None

def get_api_key():
    """Retrieve the OpenAI API key from .env file, environment variable, or config file"""
    # First try to get from .env file
    api_key = read_env_file()
    
    # If not found, try environment variable
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            print("Found API key in environment variables")
        else:
            print("API key not found in environment variables")
    
    # If still not found, try config file
    if not api_key and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                api_key = config.get("api_key")
                if api_key:
                    print("Found API key in config file: {}".format(CONFIG_FILE))
                else:
                    print("No API key found in config file: {}".format(CONFIG_FILE))
        except Exception as e:
            print("Error reading config file: {}".format(e))
    
    # If still not found, prompt user using rs.GetString instead of Dialogs.ShowTextEntry
    if not api_key:
        print("OpenAI API key not found. Please enter it below.")
        api_key = rs.GetString("OpenAI API Key")
        if api_key:
            # Save to config file
            try:
                with open(CONFIG_FILE, 'w') as f:
                    json.dump({"api_key": api_key}, f)
                print("API key saved to config file: {}".format(CONFIG_FILE))
            except Exception as e:
                print("Error saving config file: {}".format(e))
    
    return api_key

def call_openai_api(prompt, api_key):
    """Make a request to the OpenAI API and return the response"""
    try:
        # Create the request object
        request = WebRequest.Create(Uri(OPENAI_API_ENDPOINT))
        request.Method = "POST"
        request.ContentType = "application/json"
        request.Headers.Add("Authorization", "Bearer " + api_key)
        
        # Prepare the request payload
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
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
        return response_json["choices"][0]["message"]["content"]
    
    except Exception as e:
        error_msg = "Error calling OpenAI API: {}\n{}".format(str(e), traceback.format_exc())
        print(error_msg)
        return None

def execute_python_code(code):
    """Execute the Python code generated by the API"""
    try:
        # Clean up the code to handle code blocks
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        # Add debugging information
        print("Executing the following code:")
        print(code)
        
        # Execute the code in a safe environment with proper integer handling
        exec(code, {'__builtins__': __builtins__, 
                   'rs': rs, 
                   'math': math,
                   'int': int,
                   'range': range,
                   'round': round})
        return True
    except Exception as e:
        error_msg = "Error executing Python code: {}\n{}".format(str(e), traceback.format_exc())
        print(error_msg)
        return False

def get_file_context():
    """Get meaningful information about existing objects in the file"""
    context = "Existing objects in the file:\n"
    
    # Get curves and analyze them
    curves = rs.ObjectsByType(rs.filter.curve)
    if curves:
        # Count total curves
        context += "- {} curves found\n".format(len(curves))
        
        # Get bounding box to understand the drawing extent
        bbox = rs.BoundingBox(curves)
        if bbox:
            width = rs.Distance(bbox[0], bbox[1])
            height = rs.Distance(bbox[0], bbox[3])
            context += "- Drawing extent: width={:.2f}, height={:.2f}\n".format(width, height)
        
        # Get curve types
        closed_curves = sum(1 for curve in curves if rs.IsCurveClosed(curve))
        context += "- {} closed curves\n".format(closed_curves)
    
    return context

def rhinoai_command():
    """Main RhinoAI command function"""
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("API key is required to use RhinoAI")
        return
    
    # Get file context
    file_context = get_file_context()
    
    # Use a custom input box to allow spaces
    user_prompt = rs.StringBox("Enter your modeling prompt", "", "RhinoAI Prompt")
    if not user_prompt:
        return
    
    # Combine user prompt with file context
    full_prompt = "{}\n{}".format(file_context, user_prompt)
    
    print("Processing: '{}'".format(full_prompt))
    
    # Call OpenAI API
    print("Contacting OpenAI, please wait...")
    response = call_openai_api(full_prompt, api_key)
    
    if response:
        # Execute the generated code
        print("Executing generated code...")
        success = execute_python_code(response)
        
        if success:
            print("Model generation complete")
        else:
            print("Failed to execute generated code")
    else:
        print("Failed to get response from OpenAI")

# Register the RhinoAI command
if __name__ == "__main__":
    rhinoai_command() 