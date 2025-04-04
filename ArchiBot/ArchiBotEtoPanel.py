import Rhino
import Rhino.UI
import Eto.Forms as forms
import Eto.Drawing as drawing
import scriptcontext as sc
import System # Required for InvokeOnUiThread

# --- Chatbot Interaction Logic (Placeholder) ---
# In a real scenario, this would call an external API or model
def get_chatbot_response(user_message):
    """Placeholder function to simulate chatbot response."""
    # Simple echo bot for demonstration
    if "hello" in user_message.lower():
        return "Hello there! How can I help you with Rhino today?"
    elif "create sphere" in user_message.lower():
         # Placeholder for agent action recognition
        return "OK, I will try to create a sphere. (Action recognition placeholder)"
    elif "list layers" in user_message.lower():
        return "OK, I will list the layers. (Action recognition placeholder)"
    else:
        return "I received your message: '{}'. How can I assist?".format(user_message)

# --- Agent Action Logic (Placeholder) ---
def execute_rhino_action(response_text):
    """Placeholder function to simulate executing Rhino actions."""
    action_result = None
    if "create sphere" in response_text.lower():
        print("ArchiBot attempting to run Rhino command: _Sphere")
        # Uncomment the line below to actually run the command
        # Rhino.RhinoApp.RunScript("_-Sphere 0,0,0 5 _Enter", False)
        action_result = "Executed: Create Sphere (Placeholder Action)"
    elif "list layers" in response_text.lower():
        print("ArchiBot attempting to list layers")
        # Example using RhinoCommon - more robust than RunScript for data retrieval
        layer_names = [layer.Name for layer in sc.doc.Layers]
        action_result = "Current layers: {}".format(", ".join(layer_names))
        # You might want to display this result differently in the chat.

    return action_result


# --- Eto Panel Definition ---
class ArchiBotEtoPanel(forms.Form):
    """Defines the Eto Form for the ArchiBot Panel."""
    def __init__(self):
        # Call the base class constructor first!
        super(ArchiBotEtoPanel, self).__init__()
        # Proceed with setting properties
        self.Title = "ArchiBot Panel" # This title won't be used for the dockable panel tab
        # ClientSize might be less relevant for docked panel, but keep for now
        self.ClientSize = drawing.Size(400, 500)
        # Padding is now handled by the outer layout
        # self.Padding = drawing.Padding(10)
        self.Resizable = True # Resizing handled by panel docking

        # UI Controls
        self.chat_history = forms.TextArea() # Create instance first
        self.chat_history.ReadOnly = True     # Set properties afterwards
        self.chat_history.Wrap = True
        self.chat_history.BackgroundColor = drawing.Colors.WhiteSmoke

        self.input_textbox = forms.TextBox()
        self.send_button = forms.Button() # Create instance first
        self.send_button.Text = "Send"    # Set properties afterwards
        self.status_label = forms.Label() # Create instance first
        self.status_label.Text = "Status: Ready" # Set properties afterwards

        # Event Handlers
        self.send_button.Click += self.on_send_click
        self.input_textbox.KeyDown += self.on_input_keydown # Allow Enter key to send

        # Layout Configuration
        # Use vertical layout for the main panel content
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)
        layout.Padding = drawing.Padding(10) # Add padding to the main layout

        # Chat history: Allow vertical scaling
        layout.Add(self.chat_history, yscale=True)

        # Input row: Textbox scales horizontally, Button fixed size
        input_layout = forms.DynamicLayout()
        input_layout.Spacing = drawing.Size(5, 5)
        # Add controls individually within a horizontal group
        input_layout.BeginHorizontal()
        input_layout.Add(self.input_textbox, xscale=True)  # Textbox scales horizontally
        input_layout.Add(self.send_button, xscale=False) # Button has fixed size
        input_layout.EndHorizontal()
        # Add this nested layout to the main layout, no vertical scaling
        layout.Add(input_layout, xscale=True)

        # Status label: Fixed size at the bottom
        layout.Add(self.status_label)

        self.Content = layout

        # Add initial greeting
        self.add_message_to_history("ArchiBot", "Welcome! Ask me anything about your Rhino model.")


    def add_message_to_history(self, sender, message):
        """Safely appends a message to the chat history text area."""
        # Ensure UI updates happen on the main Rhino thread
        def update_ui():
            self.chat_history.AppendText("{}: {}\n\n".format(sender, message), True) # Append and scroll
        # Use InvokeOnUiThread for thread safety when updating UI from events
        Rhino.RhinoApp.InvokeOnUiThread(System.Action(update_ui))


    def on_send_click(self, sender, e):
        """Handles the logic when the Send button is clicked."""
        user_message = self.input_textbox.Text.strip()
        if not user_message:
            return

        self.add_message_to_history("You", user_message)
        self.input_textbox.Text = "" # Clear input box
        self.status_label.Text = "Status: ArchiBot is thinking..."
        Rhino.UI.RhinoEtoApp.PumpEvents() # Allow UI to update status

        # --- Get response (Simulated) ---
        # In a real app, this might involve background threads/async calls
        # to avoid blocking the UI thread, especially for network requests.
        try:
            bot_response = get_chatbot_response(user_message)
            self.add_message_to_history("ArchiBot", bot_response)

            # --- Attempt Agent Action (Simulated) ---
            action_result = execute_rhino_action(bot_response)
            if action_result:
                 self.add_message_to_history("ArchiBot (Action)", action_result)

        except Exception as ex:
            self.add_message_to_history("ArchiBot (Error)", "An error occurred: {}".format(ex))
            print("Error during chat processing: {}".format(ex)) # Log detailed error
        finally:
             # Ensure status is reset even if errors occur
             def reset_status():
                 self.status_label.Text = "Status: Ready"
             Rhino.RhinoApp.InvokeOnUiThread(System.Action(reset_status))


    def on_input_keydown(self, sender, e):
        """Handles key presses in the input textbox, specifically Enter."""
        # Send message if Enter key is pressed without Shift
        if e.Key == forms.Keys.Enter and not e.Modifiers & forms.Keys.Shift:
            e.Handled = True # Consume the event to prevent newline in textbox
            self.on_send_click(sender, None) # Trigger the send action


# --- Function to Show Panel ---
def show_archibot_panel():
    """Manages the creation and display of the ArchiBot panel."""
    # Use a unique key for scriptcontext.sticky
    panel_key = "ArchiBotPanelInstance_EtoForm"

    # Check if panel already exists and close it to avoid duplicates
    if panel_key in sc.sticky:
        try:
            existing_panel = sc.sticky[panel_key]
            if existing_panel and not existing_panel.IsDisposed:
                 print("Closing existing ArchiBot panel.")
                 existing_panel.Close() # Close the existing form
            else:
                 # If panel is disposed but key still exists, remove key
                 sc.sticky.Remove(panel_key)

        except Exception as ex:
            print("Error closing existing panel: {}. Removing sticky key.".format(ex))
            if panel_key in sc.sticky:
                 sc.sticky.Remove(panel_key) # Attempt removal again if error


    # Create and show the new panel instance
    print("Creating new ArchiBot panel.")
    panel = ArchiBotEtoPanel()
    # Parent to Rhino's main window to keep it on top
    panel.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    panel.Show() # Show as modeless dialog

    # Store a reference in scriptcontext.sticky to prevent garbage collection
    sc.sticky[panel_key] = panel

# --- Main Execution Guard ---
# This allows the script to be run directly using RunPythonScript
# or imported into another script without automatically executing.
if __name__ == "__main__":
    show_archibot_panel() 