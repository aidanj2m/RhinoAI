# RhinoAI - Intelligent Modeling Agent for Rhino3D

RhinoAI is an advanced AI-driven modeling assistant that integrates seamlessly within Rhino3D, allowing users to generate and manipulate geometry using natural language instructions.

![RhinoAI Logo](logo.png) *(Note: Logo image to be created)*

## Overview

RhinoAI leverages OpenAI's powerful language models to interpret natural language modeling instructions and convert them into executable Rhino Python code. This enables designers, architects, and engineers to create complex geometric forms and patterns through simple text prompts, similar to how CursorAI assists with coding.

## Features

- **Natural Language Input**: Create complex geometry by simply describing what you want
- **Real-time Generation**: See your ideas come to life instantly in the Rhino viewport
- **Conversational History**: Build upon previous operations in an iterative design process
- **Undo Capability**: Easily remove generated objects if needed
- **Debug Mode**: Detailed logging for troubleshooting and understanding the generation process

## Installation

1. **Prerequisites**:
   - Rhino 8 or later
   - Active internet connection
   - OpenAI API key

2. **Setup**:
   - Download the RhinoAI python script files
   - Place the files in your Rhino Python scripts folder:
     - Windows: `%APPDATA%\McNeel\Rhinoceros\8.0\scripts`
     - macOS: `~/Library/Application Support/McNeel/Rhinoceros/8.0/scripts`
   - Set your OpenAI API key using one of the following methods:
     - Create a `.env` file in the same directory as the script with your key: `OPENAI_API_KEY=your-api-key-here`
     - Set the `OPENAI_API_KEY` environment variable on your system
     - Enter your API key when prompted on first use (it will be saved to a config file)

3. **Running for the first time**:
   - In Rhino, type `RunPythonScript` in the command line
   - Navigate to and select either `RhinoAI.py` (basic version) or `RhinoAI_Advanced.py` (full-featured version)
   - After running once, you can use the `RhinoAI` command directly

## Usage

1. Type `RhinoAI` in the Rhino command line
2. Enter your modeling instruction when prompted (e.g., "Create a honeycomb lattice structure with hexagons spaced 30 units apart")
3. Wait a moment as RhinoAI processes your request and generates the geometry
4. Refine your design with additional prompts, building on the conversation history

### Command Options

- **normal**: Standard mode to enter modeling prompts
- **debug**: Toggle debug mode for detailed logging
- **clear_history**: Clear the conversation history to start fresh
- **undo_last**: Remove all objects from the last generation

## Example Prompts

See [examples.md](examples.md) for a comprehensive list of example prompts and their expected outcomes.

Some quick examples:

- "Create a sphere with radius 10 at the origin"
- "Generate a spiral staircase with 20 steps, total height 50, and radius 20"
- "Create a wavy surface resembling ocean waves within a 100x100 area"
- "Generate a gear with 24 teeth and diameter 50"

## Technical Details

RhinoAI works by:

1. Capturing your natural language input
2. Sending it to OpenAI's API along with a specialized system prompt
3. Receiving Python code designed to create the requested geometry
4. Executing that code within the Rhino environment
5. Tracking generated objects for potential future operations

The system uses:
- Rhino's built-in Python scripting environment
- RhinoScriptSyntax and RhinoCommon libraries
- .NET's HTTP request capabilities for API communication
- JSON for structured data exchange

## Customization

You can modify the `SYSTEM_PROMPT` constant in the script files to change how RhinoAI interprets and responds to your prompts. This can be useful for specializing the assistant for particular design domains or enforcing specific modeling standards.

## API Key Management

RhinoAI looks for your OpenAI API key in the following order:
1. A `.env` file in the same directory as the RhinoAI scripts
2. System environment variables
3. A previously saved configuration file
4. Manual input (if no key is found using the above methods)

The `.env` file should be formatted as:
```
OPENAI_API_KEY=your-api-key-here
```

## Troubleshooting

- **API Key Issues**: Ensure your OpenAI API key is valid and has sufficient quota
- **Network Problems**: Check your internet connection if requests fail
- **Generation Errors**: Enable debug mode to see detailed logs in `~/RhinoAI_logs/`
- **Command Registration**: If the `RhinoAI` command doesn't register, try restarting Rhino or using `RunPythonScript` to run the file directly

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the powerful language models that power RhinoAI
- McNeel for developing Rhino3D and its excellent Python scripting capabilities

---

*RhinoAI is not affiliated with or endorsed by Robert McNeel & Associates or OpenAI.* 