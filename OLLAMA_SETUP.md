# Ollama Setup Guide

## Overview

Your J.A.R.V.I.S chatbot has been migrated from Groq (cloud-based LLM) to Ollama (local LLM). This means:

- **Local Execution**: The model runs on your machine, not in the cloud
- **No API Keys**: No need for Groq API keys
- **Privacy**: All conversations stay on your device
- **Model**: Google's gemma4:e4b (high-performance open model)

## Prerequisites

### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from: https://ollama.ai/download

**Linux (Alternative - from source):**
```bash
sudo apt-get install ollama
```

### 2. Pull the gemma4:e4b Model

```bash
ollama pull gemma4:e4b
```

This downloads the model (~5-10GB depending on your internet speed). First download may take a few minutes.

### 3. Verify Installation

```bash
# Start Ollama server (if not running in background)
ollama serve

# In another terminal, test the model
ollama run gemma4:e4b "Hello, how are you?"
```

## Running J.A.R.V.I.S with Ollama

### Step 1: Start Ollama Server

```bash
ollama serve
```

This keeps the LLM server running on `http://localhost:11434`

### Step 2: In Another Terminal, Run the App

```bash
cd ~/chatbot/jarvisai
source .venv/bin/activate
python run.py
```

### Step 3: Access the API

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)

## Configuration

Edit `.env` to adjust:

```env
OLLAMA_BASE_URL=http://localhost:11434    # Ollama server URL
OLLAMA_MODEL=gemma4:e4b                   # Model to use
```

## Troubleshooting

### Issue: Connection refused on localhost:11434

**Solution**: Make sure Ollama is running
```bash
ollama serve
```

### Issue: Model not found

**Solution**: Pull the model first
```bash
ollama pull gemma4:e4b
```

### Issue: Out of Memory

The gemma4:e4b model requires ~6-8GB of RAM. If you run into memory issues:

1. Use a smaller model:
   ```bash
   ollama pull mistral:7b
   ```
   Then update `.env`:
   ```env
   OLLAMA_MODEL=mistral:7b
   ```

2. Or increase your system's virtual memory/swap space

## API Endpoints

### General Chat (No Web Search)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "session_id": "user-123"
  }'
```

### Realtime Chat (With Web Search via Tavily)
```bash
curl -X POST http://localhost:8000/chat/realtime \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the latest news today?",
    "session_id": "user-123"
  }'
```

### Get Chat History
```bash
curl http://localhost:8000/chat/history/user-123
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Advantages of Ollama

- ✅ **Local**: No internet required for inference
- ✅ **Privacy**: Data never leaves your device
- ✅ **Free**: No API costs
- ✅ **Fast**: Optimized for local hardware
- ✅ **Control**: Choose which model to use
- ✅ **Offline**: Works without cloud connectivity

## Performance Tips

1. **GPU Acceleration**: Ollama supports GPU (CUDA, Metal, HIP)
   - NVIDIA GPUs are supported out of the box
   - AMD/ROCm requires additional setup
   - Apple Silicon (Metal) is built-in

2. **Memory Management**: Ollama unloads models from memory after 5 minutes of inactivity

3. **Faster Models**: If gemma4:e4b is slow, try:
   ```bash
   ollama pull mistral:7b      # Faster, ~7B params
   ollama pull neural-chat:7b  # Optimized for chat
   ```

## Switching Models

To use a different model:

1. Pull the model:
   ```bash
   ollama pull mistral:7b
   ```

2. Update `.env`:
   ```env
   OLLAMA_MODEL=mistral:7b
   ```

3. Restart the app

## Popular Models to Try

- `gemma4:e4b` (4B params) - Current default, lightweight
- `mistral:7b` (7B params) - Good balance of speed/quality
- `neural-chat:7b` (7B params) - Optimized for conversations
- `llama2:7b` (7B params) - Good general purpose
- `openchat:7b` (7B params) - Fast and capable

See: https://ollama.ai/library for more models

## Support

- Ollama Issues: https://github.com/ollama/ollama/issues
- Model Questions: https://ollama.ai/library
