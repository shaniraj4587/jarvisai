# Migration Details: Groq → Ollama

## Quick Summary

**Before (Groq):**
- Cloud-based LLM API
- Multiple API keys with round-robin fallback
- Rate limiting and costs
- Internet required

**After (Ollama):**
- Local LLM runtime
- Single model (gemma4:e4b)
- No API keys or costs
- Works offline

## Detailed Code Changes

### 1. Dependencies Change

**File:** `requirements.txt`

```diff
- langchain-groq
+ langchain-ollama
```

### 2. Configuration Changes

**File:** `config.py`

**Removed:**
```python
# OLD: Multi-key Groq configuration
def _load_groq_api_keys() -> list:
    # ... complex key loading logic
    
GROQ_API_KEYS = _load_groq_api_keys()
GROQ_API_KEY = GROQ_API_KEYS[0] if GROQ_API_KEYS else ""
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
```

**Added:**
```python
# NEW: Simple Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
```

### 3. LLM Service Changes

**File:** `app/services/groq_service.py`

**Import Changes:**
```python
# OLD
from langchain_groq import ChatGroq

# NEW
from langchain_ollama import OllamaLLM
from config import OLLAMA_BASE_URL, OLLAMA_MODEL  # Changed
```

**Class Simplification:**
```python
# OLD: Complex multi-key round-robin logic
class GroqService:
    _shared_key_index = 0  # Class-level counter
    
    def __init__(self, vector_store_service):
        self.llms = [
            ChatGroq(groq_api_key=key, model_name=GROQ_MODEL, temperature=0.8)
            for key in GROQ_API_KEYS
        ]
    
    def _invoke_llm(self, prompt, messages, question):
        # 100+ lines of round-robin and fallback logic
        ...

# NEW: Simple single-model approach
class GroqService:
    def __init__(self, vector_store_service):
        self.llm = OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.8,
        )
    
    def get_response(self, question, chat_history=None):
        # Direct Ollama call, no round-robin needed
        chain = prompt | self.llm
        response = chain.invoke({"history": messages, "question": question})
        return response
```

**Removed Methods:**
- `_invoke_llm()` - No longer needed (direct chain invocation)
- Helper functions:
  - `_is_rate_limit_error()` - Ollama doesn't have rate limits
  - `_mask_api_key()` - No API keys to mask

### 4. Realtime Service Changes

**File:** `app/services/realtime_service.py`

- Updated class docstring to reference Ollama
- Updated `__init__` docstring
- Removed comment about multi-key fallback in `get_response()`

### 5. API Error Handling Changes

**File:** `app/main.py`

**Removed:**
```python
# OLD: Rate limit handling
RATE_LIMIT_MESSAGE = "You've reached your daily API limit..."

def _is_rate_limit_error(exc: Exception) -> bool:
    return "429" in str(exc) or "rate limit" in msg or "tokens per day" in msg

# In endpoints:
if _is_rate_limit_error(e):
    raise HTTPException(status_code=429, detail=RATE_LIMIT_MESSAGE)
```

**Simplified Error Handling:**
```python
# NEW: Direct error handling (no rate limits)
except Exception as e:
    logger.error(f"Error processing chat: {e}")
    raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

**Updated Logging:**
```diff
- logger.info("Initializing Groq service (general chat)...")
+ logger.info("Initializing Ollama service (general chat)...")

- logger.info(" - Groq AI (General): Ready")
+ logger.info(" - Ollama AI (General): Ready")
```

### 6. Environment Configuration

**File:** `.env`

```diff
# OLD
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_groq api

# NEW
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e4b
```

## Lines of Code Impact

| File | Changes | Net Change |
|------|---------|-----------|
| config.py | Removed 40+ lines of key loading logic | -40 lines |
| groq_service.py | Removed 150+ lines (round-robin, fallback, helpers) | -150 lines |
| realtime_service.py | Updated docstrings only | -3 lines |
| main.py | Removed rate limit handling and related functions | -30 lines |
| requirements.txt | Replaced 1 package | 0 lines |
| **Total** | | **-220+ lines** |

## Architecture Benefits

### Before (Groq):
```
Client → API Request → Cloud (Groq API) → Response
         ↓ (API Key)    (Rate Limits)
     (Internet Required)
```

### After (Ollama):
```
Client → API Request → Local Ollama Server → Ollama LLM → Response
                      (gemma4:e4b Model)
                      (No Internet Required)
```

## Testing Checklist

After migration, verify:

- [x] Syntax checks pass: `python -m py_compile app/services/groq_service.py`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Ollama server running: `ollama serve`
- [ ] Model available: `ollama pull gemma4:e4b`
- [ ] General chat works: POST `/chat`
- [ ] Realtime chat works: POST `/chat/realtime`
- [ ] Chat history loads: GET `/chat/history/{session_id}`
- [ ] Health check works: GET `/health`

## Rollback Instructions

If you need to go back to Groq:

1. Restore from git: `git checkout HEAD -- .`
2. Or manually revert files using git history

## Future Improvements

1. Add model switching API endpoint
2. Support for different Ollama models dynamically
3. Model performance metrics collection
4. GPU acceleration detection and logging
5. Model preloading based on usage patterns
