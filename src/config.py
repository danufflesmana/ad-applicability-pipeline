from openai import OpenAI
from typing import List, Dict, Any

BASE_URL = "https://llm.soji.ai"
API_KEY = "sk-hZK5AkUvGO0CXMbg67j7Aw"

# Simple client initialization without extra parameters
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

MODELS = {"text": "gemini/gemini-2.5-flash", "vision": "gemini/gemini-2.5-flash"}
FALLBACK_MODELS = {"text": ["gemini-2.5-flash"], "vision": ["gemini-2.5-flash"]}
DEFAULT_PARAMS = {"temperature": 0, "max_tokens": 2000, "response_format": {"type": "json_object"}}

def get_completion(messages: List[Dict[str, Any]], use_vision: bool = False, **kwargs) -> Any:
    model_type = "vision" if use_vision else "text"
    models_to_try = [MODELS[model_type]] + FALLBACK_MODELS[model_type]
    params = {**DEFAULT_PARAMS, **kwargs}
    
    for model in models_to_try:
        try:
            print(f"  → Trying: {model}")
            response = client.chat.completions.create(model=model, messages=messages, **params)
            print(f"  ✓ Success")
            return response
        except Exception as e:
            print(f"  ✗ Failed: {str(e)[:80]}")
            if model == models_to_try[-1]:
                raise

def test_api_connection() -> bool:
    try:
        response = get_completion(
            messages=[{"role": "user", "content": "Say 'API works'"}],
            use_vision=False, max_tokens=10
        )
        result = response.choices[0].message.content
        print(f"✓ API test: {result}")
        return True
    except Exception as e:
        print(f"✗ API failed: {e}")
        return False

def list_available_models():
    try:
        models = client.models.list()
        return [m.id for m in models.data]
    except:
        return []
