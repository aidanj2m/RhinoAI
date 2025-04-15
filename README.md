# RhinoAI - Intelligent AI Assistant for Rhino 8

RhinoAI is an advanced AI-driven modeling assistant that integrates seamlessly within Rhino 8, allowing users to generate and manipulate geometry using natural language instructions.

## Architecture

RhinoAI uses a streamlined cloud-based architecture:

1. **Panel Interface**: A sleek, integrated panel directly within Rhino 8 for all user interactions
2. **Vercel Cloud API**: All AI processing happens on our secure serverless API
3. **Context-Aware Processing**: The system automatically analyzes your Rhino environment before generating code

## Features

- **Conversational UI**: Interact with the AI assistant through a dedicated panel within Rhino
- **Cloud Processing**: Powerful AI capabilities without local computational overhead
- **Context Awareness**: The system understands your current Rhino file, layers, and selections
- **One-Command Access**: Just type "RhinoAI" in Rhino to launch the assistant
- **Auto-Loading**: Optionally starts automatically when you launch Rhino

## Installation

1. **Prerequisites**:
   - Rhino 8 
   - Active internet connection
   - OpenAI API key

2. **Setup**:
   - Download the RhinoAI Python files
   - Place the files in a folder of your choice
   - Run the installer script by typing `RunPythonScript` in Rhino and selecting `install_rhinoai.py`
   - Enter your OpenAI API key when prompted (it will be saved for future use)

3. **API Key Setup** (one of the following methods):
   - Create a `.env` file in the same directory as the script with your key: `OPENAI_API_KEY=your-api-key-here`
   - Set the `OPENAI_API_KEY` environment variable on your system
   - Enter your API key when prompted on first use (it will be saved to a config file)

## Usage

1. Type `RhinoAI` in the Rhino command line to open the panel
2. Enter your request in the text box and press Send (or Ctrl+Enter)
3. RhinoAI will process your request and generate the appropriate geometry
4. Continue the conversation with additional requests

## Example Prompts

- "Create a sphere with radius 10 at the origin"
- "Generate a spiral staircase with 20 steps, total height 50, and radius 20"
- "Create a wavy surface resembling ocean waves within a 100x100 area"
- "Generate a gear with 24 teeth and diameter 50"
- "Hatch the selected closed curves with a solid fill"

## How It Works

1. When you send a request, RhinoAI:
   - Collects context from your current Rhino environment (objects, layers, selection)
   - Sends this context along with your prompt to the cloud API
   - The API processes your request using AI and returns ready-to-execute Python code
   - The panel executes the code in your Rhino environment

2. The cloud API automatically:
   - Formats your request with the appropriate context
   - Generates Python code specifically for Rhino 8
   - Adds error handling and safety measures
   - Returns both the explanation and executable code

## Troubleshooting

- **API Key Issues**: Ensure your OpenAI API key is valid and has sufficient quota
- **Network Problems**: Check your internet connection if requests fail
- **Panel Not Showing**: Try restarting Rhino and running the installer again
- **Execution Errors**: Check the error message for details on what went wrong

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*RhinoAI is not affiliated with or endorsed by Robert McNeel & Associates or OpenAI.* 