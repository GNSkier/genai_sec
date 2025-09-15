# Gemini Setup Instructions

## Quick Setup

1. **Create `.env` file in master directory**:
   ```bash
   cd /Users/skier/MSDS/Data_Engineering/GenAI_Security/Homeworks/genai_sec
   echo "GCP_KEY=your-gemini-api-key-here" > .env
   ```

2. **Get your Gemini API key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key

3. **Add the key to `.env` file**:
   ```bash
   # Edit the .env file and replace 'your-gemini-api-key-here' with your actual key
   nano .env
   ```

4. **Test the integration**:
   ```bash
   cd MCP_Server
   python gemini_llm_integration.py --demo
   ```

## Alternative: Environment Variable

Instead of using `.env` file, you can set the environment variable directly:

```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
python gemini_llm_integration.py --demo
```

## File Structure

```
genai_sec/
├── .env                    # Your API keys (GCP_KEY=your-key)
├── MCP_Server/
│   ├── gemini_llm_integration.py
│   ├── setup_real_llm.py
│   └── ...
└── PII_testing/
    └── ...
```

## Troubleshooting

- **"GCP_KEY not found"**: Make sure `.env` file exists in master directory
- **"API key test failed"**: Check that your API key is valid
- **"No .env file found"**: The script will still work with environment variables
