# RhinoAI - Intelligent Modeling Agent for Rhino3D

RhinoAI is an advanced AI-driven modeling assistant that integrates seamlessly within Rhino3D, allowing users to generate and manipulate geometry using natural language instructions.

## New Architecture

RhinoAI now features a cloud-based architecture:

1. **Vercel Backend API**: All AI requests are processed through a secure Vercel-hosted API
2. **Native Rhino Panel**: A sleek, integrated panel interface directly within Rhino 8
3. **Improved Performance**: Offloading processing to the cloud means faster responses even on less powerful machines

## Features

- **Natural Language Input**: Create complex geometry by simply describing what you want
- **Real-time Generation**: See your ideas come to life instantly in the Rhino viewport
- **Conversational UI**: Interact with the AI assistant through a dedicated panel within Rhino
- **Cloud Processing**: Powerful AI capabilities without local computational overhead
- **Debug Mode**: Detailed logging for troubleshooting and understanding the generation process

## Installation

1. **Prerequisites**:
   - Rhino 8 
   - Active internet connection
   - OpenAI API key

2. **Setup**:
   - Download the RhinoAI Python script files
   - Place the files in your Rhino Python scripts folder:
     - Windows: `%APPDATA%\McNeel\Rhinoceros\8.0\scripts`
     - macOS: `~/Library/Application Support/McNeel/Rhinoceros/8.0/scripts`
   - Run the installer script by typing `RunPythonScript` in Rhino and selecting `install_rhinoai_panel.py`
   - Set your OpenAI API key when prompted (it will be saved for future use)

3. **API Key Setup** (one of the following methods):
   - Create a `.env` file in the same directory as the script with your key: `OPENAI_API_KEY=your-api-key-here`
   - Set the `OPENAI_API_KEY` environment variable on your system
   - Enter your API key when prompted on first use (it will be saved to a config file)

## Usage

### Panel Interface

1. Type `RhinoAIPanel` in the Rhino command line to open the panel
2. Enter your request in the text box and press Send (or Ctrl+Enter)
3. Watch as RhinoAI processes your request and generates the geometry
4. Continue the conversation with additional requests

### Command Line Interface

1. Type `RhinoAI` in the Rhino command line
2. Enter your modeling instruction when prompted
3. Wait a moment as RhinoAI processes your request and generates the geometry

## Example Prompts

- "Create a sphere with radius 10 at the origin"
- "Generate a spiral staircase with 20 steps, total height 50, and radius 20"
- "Create a wavy surface resembling ocean waves within a 100x100 area"
- "Generate a gear with 24 teeth and diameter 50"

## Technical Details

RhinoAI works by:

1. Capturing your natural language input
2. Sending it to our secure Vercel API
3. The API processes your request using OpenAI's powerful language models
4. Python code is generated to create the requested geometry
5. That code is executed within the Rhino environment

The system uses:
- Rhino's built-in Python scripting environment
- RhinoScriptSyntax for geometry manipulation
- Vercel serverless functions for API hosting
- .NET's HTTP request capabilities for API communication

## Troubleshooting

- **API Key Issues**: Ensure your OpenAI API key is valid and has sufficient quota
- **Network Problems**: Check your internet connection if requests fail
- **Panel Not Showing**: Try restarting Rhino and running the installer again
- **Command Registration**: If the commands don't register, try restarting Rhino or using `RunPythonScript` to run the installer directly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*RhinoAI is not affiliated with or endorsed by Robert McNeel & Associates or OpenAI.* 