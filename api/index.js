const { Configuration, OpenAIApi } = require('openai');

// Initialize OpenAI configuration with API key from environment variables
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});

const openai = new OpenAIApi(configuration);

// Default system prompt for RhinoAI
const SYSTEM_PROMPT = `You are an expert Rhino 3D Python scripting assistant, specializing in precise 2D drawing editing, detailed annotation, and advanced layer management within Rhino 8. Generate clear, efficient, and robust Python scripts adhering strictly to these guidelines:

The tools at your disposal are commands within Rhino 8 and you have access to all software within _______


### 1. High-Quality 2D Drawing Edits and Enhancements:

Hatching:
- when the user asks to hatch something, you should create a solid hatch fill in the highlighted area.
- The hatch should be on the layer that is currently selected, unless the user specifies a different layer.
The following rules apply unless the user specifies otherwise:
   - The hatch should be a solid fill.
    - The hatch should be a single color.
    - The hatch should be a single linetype.
    - The hatch should be a single lineweight.
    - The hatch should be a single color.
    - The hatch should be a single linetype.
- When the user asks along the lines of "hatch inside of the shape/s that are part of the layer ______", you should create a solid hatch fill in the shapes that are correlated to that layer.


B. Scale Figures:
- Interpret user descriptions (e.g., "standing," "seated," "walking figures").
- Generate minimal, clean vector representations at correct architectural scales (~6 feet height unless otherwise stated).
- Position logically based on user inputs or selection points.
- they must be closed loops
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

- Write modular, commented, reusable Python code, they must not include
- Provide adjustable parameters clearly defined at the top.
- Anticipate edge cases and provide descriptive error handling.
- Focus on clean geometry, optimized for further editing by users.`;

module.exports = async (req, res) => {
  // Set CORS headers to allow requests from any origin
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization'
  );

  // Handle OPTIONS request (preflight)
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Only allow POST requests for the API endpoint
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed. Please use POST.' });
  }

  try {
    // Validate request body
    const { prompt, model = 'gpt-4', temperature = 0.7, max_tokens = 2048 } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Missing required field: prompt' });
    }

    // Check if API key is configured
    if (!configuration.apiKey) {
      return res.status(500).json({
        error: 'OpenAI API key not configured',
        message: 'Please set the OPENAI_API_KEY environment variable in the Vercel dashboard'
      });
    }

    // Make request to OpenAI API
    const response = await openai.createChatCompletion({
      model: model,
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      temperature: temperature,
      max_tokens: max_tokens
    });

    // Return the generated code from OpenAI
    return res.status(200).json({
      result: response.data.choices[0].message.content
    });
  } catch (error) {
    console.error('Error processing request:', error);
    
    // Determine the appropriate error message and status code
    const statusCode = error.response?.status || 500;
    const errorMessage = error.response?.data?.error?.message || error.message || 'An unknown error occurred';
    
    return res.status(statusCode).json({
      error: errorMessage
    });
  }
}; 