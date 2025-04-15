# Deployment Guide for RhinoAI Vercel API

This guide explains how to deploy the RhinoAI API backend to Vercel.

## Prerequisites

- A Vercel account (create one at [vercel.com](https://vercel.com))
- Node.js and npm installed on your local machine
- Vercel CLI installed (`npm install -g vercel`)
- An OpenAI API key

## Deployment Steps

1. **Login to Vercel CLI**

   ```bash
   vercel login
   ```

2. **Deploy the API**

   Navigate to the project directory and run:

   ```bash
   cd api
   vercel
   ```

   Follow the prompts to link to your Vercel account and project.

3. **Set Environment Variables**

   After deployment, you need to set your OpenAI API key as an environment variable:

   - Go to your project on the Vercel dashboard
   - Navigate to Settings > Environment Variables
   - Add a new variable:
     - Name: `OPENAI_API_KEY`
     - Value: Your OpenAI API key
   - Save the changes

4. **Deploy to Production**

   To deploy to production:

   ```bash
   vercel --prod
   ```

5. **Update API Endpoint in RhinoAI Scripts**

   Once deployed, update the `VERCEL_API_ENDPOINT` constant in both `RhinoAI.py` and `RhinoAI_Panel.py` with your Vercel deployment URL. The endpoint should be something like:

   ```
   https://your-project-name.vercel.app/api
   ```

## Testing the API

You can test your API endpoint using curl:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
  -d '{"prompt":"Create a simple cube at the origin", "temperature": 0.7, "max_tokens": 2048}' \
  https://your-project-name.vercel.app/api
```

## Troubleshooting

- **CORS Issues**: If you have CORS issues, ensure your Vercel functions are properly configured with CORS headers as shown in the API code.
- **API Key Not Working**: Verify your OpenAI API key is correctly set in the Vercel environment variables.
- **Function Timeouts**: If you experience timeouts, consider increasing the function execution time limit in your Vercel project settings.

## Local Development

For local development before deploying:

1. Install dependencies:

   ```bash
   cd api
   npm install
   ```

2. Create a `.env` file in the `api` folder with your OpenAI API key:

   ```
   OPENAI_API_KEY=your-api-key-here
   ```

3. Start the local development server:

   ```bash
   vercel dev
   ```

Your API will be available at `http://localhost:3000/api` for testing. 