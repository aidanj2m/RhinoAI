import rhinoscriptsyntax as rs
import Rhino
import Rhino.UI
import scriptcontext as sc
import System
import json
import os
import traceback
import re
from System.Net import WebClient, WebRequest, WebResponse, WebHeaderCollection, HttpRequestHeader
from System.Text import Encoding
from System.IO import StreamReader, File
from System.Security import SecureString
from System import Uri, Convert, Environment, Guid
from Rhino.UI import Dialogs, PanelType, StackedDialogPage
from System.Drawing import Size, Point, Color, Font, FontStyle, Rectangle, SolidBrush, Bitmap, Graphics, StringFormat
from System.Windows.Forms import (Form, Button, TextBox, Label, Panel, 
                                 BorderStyle, FormBorderStyle, AnchorStyles, 
                                 DockStyle, ScrollBars, Keys, DialogResult,
                                 ControlStyles, AutoScaleMode, AutoSizeMode,
                                 PictureBox, PictureBoxSizeMode, Padding,
                                 RichTextBox)

# Constants
VERCEL_API_ENDPOINT = "https://rhino-ai-buzzed-technologies.vercel.app/api"
DEFAULT_TEMPERATURE = 0.7
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "RhinoAI_config.json")
panel_id = Guid.NewGuid()

# Try multiple possible locations for the .env file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else None
ENV_LOCATIONS = [
    os.path.join(os.getcwd(), ".env"),  # Current working directory
    os.path.join(os.path.expanduser("~"), ".env"),  # User's home directory
]
if SCRIPT_DIR:
    ENV_LOCATIONS.insert(0, os.path.join(SCRIPT_DIR, ".env"))  # Script directory if available

class RhinoAIPanel(Form):
    def __init__(self):
        self.initialize_component()
        self.api_key = self.get_api_key()
        
    def initialize_component(self):
        """Initialize the panel UI components"""
        self.Text = "RhinoAI Assistant"
        self.Size = Size(450, 650)
        self.BackColor = Color.White
        self.FormBorderStyle = FormBorderStyle.Fixed3D
        self.AutoScaleMode = AutoScaleMode.Font

        # Create the header panel
        self.header_panel = Panel()
        self.header_panel.BackColor = Color.FromArgb(240, 240, 240)
        self.header_panel.Dock = DockStyle.Top
        self.header_panel.Height = 60
        self.header_panel.Padding = Padding(10)

        # Add logo and title
        self.title_label = Label()
        self.title_label.Text = "RhinoAI Assistant"
        self.title_label.Font = Font("Segoe UI", 16, FontStyle.Bold)
        self.title_label.Location = Point(15, 15)
        self.title_label.AutoSize = True
        
        # Add conversation history display
        self.history_box = RichTextBox()
        self.history_box.ReadOnly = True
        self.history_box.BackColor = Color.White
        self.history_box.Dock = DockStyle.Fill
        self.history_box.BorderStyle = BorderStyle.Fixed3D
        self.history_box.Font = Font("Segoe UI", 10)
        self.history_box.ScrollBars = ScrollBars.Vertical
        
        # Add prompt input area
        self.input_panel = Panel()
        self.input_panel.Dock = DockStyle.Bottom
        self.input_panel.Height = 100
        self.input_panel.Padding = Padding(10)
        self.input_panel.BackColor = Color.FromArgb(245, 245, 245)
        
        self.prompt_box = TextBox()
        self.prompt_box.Multiline = True
        self.prompt_box.ScrollBars = ScrollBars.Vertical
        self.prompt_box.Dock = DockStyle.Fill
        self.prompt_box.BorderStyle = BorderStyle.FixedSingle
        self.prompt_box.Font = Font("Segoe UI", 10)
        self.prompt_box.KeyDown += self.on_key_down
        
        self.send_button = Button()
        self.send_button.Text = "Send"
        self.send_button.Width = 80
        self.send_button.Height = 30
        self.send_button.Dock = DockStyle.Right
        self.send_button.Click += self.on_send_click
        
        # Add components to panels
        self.header_panel.Controls.Add(self.title_label)
        
        self.input_panel.Controls.Add(self.prompt_box)
        self.input_panel.Controls.Add(self.send_button)
        
        # Add panels to form
        self.Controls.Add(self.history_box)
        self.Controls.Add(self.header_panel)
        self.Controls.Add(self.input_panel)
        
        # Show welcome message
        self.history_box.AppendText("Welcome to RhinoAI Assistant!\n")
        self.history_box.AppendText("Type your request below and press Send or Ctrl+Enter.\n\n")
        
        # Set focus to the prompt box
        self.prompt_box.Focus()

    def on_key_down(self, sender, e):
        """Handle key press events, submit on Ctrl+Enter"""
        if e.Control and e.KeyCode == Keys.Enter:
            e.SuppressKeyPress = True
            self.send_prompt()

    def on_send_click(self, sender, e):
        """Handle send button click"""
        self.send_prompt()

    def send_prompt(self):
        """Process and send the prompt to the API"""
        prompt = self.prompt_box.Text.Strip()
        if not prompt:
            return
        
        # Display user prompt in history
        self.history_box.AppendText("You: " + prompt + "\n\n")
        self.prompt_box.Text = ""
        
        # Get context information about the file
        context = self.get_rhino_context()
        
        # Show pending message
        self.history_box.AppendText("RhinoAI: Thinking...\n")
        self.history_box.ScrollToCaret()
        
        # Call the API asynchronously
        self.call_api_async(prompt, context)

    def call_api_async(self, prompt, context):
        """Call the API asynchronously to prevent UI freezing"""
        try:
            # Create a WebClient instance
            client = WebClient()
            client.Headers[HttpRequestHeader.ContentType] = "application/json"
            client.Headers[HttpRequestHeader.Authorization] = "Bearer " + self.api_key
            
            # Prepare payload
            payload = {
                "prompt": prompt,
                "context": context,
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": 2048
            }
            
            # Convert payload to JSON
            json_payload = json.dumps(payload)
            
            # Set up callbacks
            client.UploadStringCompleted += self.on_api_response
            client.UploadStringAsync(Uri(VERCEL_API_ENDPOINT), "POST", json_payload)
        except Exception as e:
            self.handle_error("Error calling API: " + str(e))

    def on_api_response(self, sender, e):
        """Handle the API response"""
        try:
            if e.Error:
                self.handle_error("API Error: " + str(e.Error))
                return
            
            # Process the response
            response_json = json.loads(e.Result)
            raw_result = response_json.get("raw_result")
            executable_code = response_json.get("executable_code")
            
            if not executable_code:
                self.handle_error("Received empty response from API")
                return
                
            # Update the history box with the response
            self.history_box.Text = self.history_box.Text.Replace("RhinoAI: Thinking...\n", "")
            self.history_box.AppendText("RhinoAI: I'll help you with that.\n\n")
            
            # Display the raw result in a cleaner format
            if raw_result:
                # Strip code blocks for display
                display_text = raw_result
                if "```" in display_text:
                    display_text = re.sub(r'```(?:python)?(.*?)```', 
                                         r'[Code implementation not shown]', 
                                         display_text, 
                                         flags=re.DOTALL)
                
                self.history_box.AppendText(display_text + "\n\n")
            
            # Execute the code
            self.execute_python_code(executable_code)
            
        except Exception as e:
            self.handle_error("Error processing API response: " + str(e))

    def handle_error(self, message):
        """Display error message in the history"""
        self.history_box.Text = self.history_box.Text.Replace("RhinoAI: Thinking...\n", "")
        self.history_box.AppendText("RhinoAI: " + message + "\n\n")
        self.history_box.ScrollToCaret()
        
    def execute_python_code(self, code):
        """Execute the Python code generated by the API"""
        try:
            # Display execution message
            self.history_box.AppendText("Executing code...\n")
            self.history_box.ScrollToCaret()
            
            # Execute the code directly - no need to clean it up as the API has done that
            exec(code, globals())
            
            self.history_box.AppendText("Code executed successfully!\n\n")
            self.history_box.ScrollToCaret()
        except Exception as e:
            error_msg = "Error executing code: " + str(e) + "\n" + traceback.format_exc()
            self.handle_error(error_msg)

    def get_rhino_context(self):
        """Get comprehensive context information about the Rhino environment"""
        context = {}
        
        # Get curve information
        curves = rs.ObjectsByType(rs.filter.curve)
        if curves:
            context["curves"] = {
                "count": len(curves),
                "closed": sum(1 for curve in curves if rs.IsCurveClosed(curve))
            }
            
            # Get bounding box information
            bbox = rs.BoundingBox(curves)
            if bbox:
                width = rs.Distance(bbox[0], bbox[1])
                height = rs.Distance(bbox[0], bbox[3])
                context["extent"] = {
                    "width": width,
                    "height": height
                }
        
        # Get layer information
        try:
            layers = rs.LayerNames()
            if layers:
                context["layers"] = layers
                
                # Get current layer
                current_layer = rs.CurrentLayer()
                if current_layer:
                    context["current_layer"] = current_layer
        except:
            pass
            
        # Get selection information
        selected_objects = rs.SelectedObjects()
        if selected_objects:
            context["selection"] = {
                "count": len(selected_objects),
                "types": {}
            }
            
            # Count types of selected objects
            for obj in selected_objects:
                obj_type = rs.ObjectType(obj)
                if obj_type not in context["selection"]["types"]:
                    context["selection"]["types"][obj_type] = 0
                context["selection"]["types"][obj_type] += 1
        
        return context

    def read_env_file(self):
        """Read the API key from a .env file in multiple possible locations"""
        for location in ENV_LOCATIONS:
            if os.path.exists(location):
                try:
                    with open(location, 'r') as f:
                        env_content = f.read()
                        # Look for OPENAI_API_KEY in the file
                        match = re.search(r'OPENAI_API_KEY=([^\s]+)', env_content)
                        if match:
                            return match.group(1)
                except Exception:
                    pass
        return None

    def get_api_key(self):
        """Retrieve the OpenAI API key from .env file, environment variable, or config file"""
        # First try to get from .env file
        api_key = self.read_env_file()
        
        # If not found, try environment variable
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
        
        # If still not found, try config file
        if not api_key and os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    api_key = config.get("api_key")
            except:
                pass
        
        # If still not found, prompt user
        if not api_key:
            api_key_result = rs.GetString("Enter your OpenAI API Key", "")
            if api_key_result:
                # Save to config file
                try:
                    with open(CONFIG_FILE, 'w') as f:
                        json.dump({"api_key": api_key_result}, f)
                except:
                    pass
                return api_key_result
            else:
                return None
        
        return api_key

# This is the required panel class for Rhino
class RhinoAIPanelHost:
    def __init__(self):
        self.panel = None
        
    def PanelShown(self, sender, e):
        if not self.panel:
            self.panel = RhinoAIPanel()
            e.AddPage(self.panel, "RhinoAI")

# Create and register the panel
def register_rhinoai_panel():
    global panel_id
    panel_host = RhinoAIPanelHost()
    Rhino.UI.Panels.RegisterPanel(panel_id, panel_host, "RhinoAI", PanelType.Floating)
    
def rhinoai_panel_command():
    """Command to show the RhinoAI panel"""
    register_rhinoai_panel()
    Rhino.UI.Panels.OpenPanel(panel_id)

# Register the command
if __name__ == "__main__":
    register_rhinoai_panel() 