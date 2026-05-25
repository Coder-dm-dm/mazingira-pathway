import os
from llama_cpp import Llama

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "gemma-4-E2B-Q8_0.gguf")

# Global singleton storage variable to prevent reload resource leaks
_model_instance = None

def get_llm():
    """Initializes and returns the cached local LLM interface context."""
    global _model_instance
    if _model_instance is None:
        if not os.path.exists(MODEL_PATH):
            print(f"CRITICAL WARNING: Model binary missing at: {MODEL_PATH}")
            return None
        try:
            print(f"[AI ENGINE] Mounting Weights into RAM: {MODEL_PATH}")
            _model_instance = Llama(model_path=MODEL_PATH, n_ctx=512, n_threads=2)
            print("[AI ENGINE] Model context verified successfully!")
        except Exception as e:
            print(f"[AI ENGINE] Error during loading initialization pipeline: {e}")
            return None
    return _model_instance

def generate_ai_broadcast(prompt_text):
    """Function (c): Generates an SMS-optimized broadcast message using local inference."""
    llm = get_llm()
    if llm is None:
        return "[SYSTEM NOTIFICATION: Local AI weights file is currently unreachable.]"

    system_instruction = (
        "You are an environmental alert broadcast generator. Write a short, clear broadcast "
        "message based on the user's prompt. Do not include chat pleasantries or extra text."
    )
    full_prompt = f"<|im_start|>system\n{system_instruction}<|im_end|>\n<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"

    try:
        response = llm(
            full_prompt,
            max_tokens=160,  # Limits character volume output safely for SMS
            stop=["<|im_end|>", "\n\n"],
            temperature=0.3
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        return f"[Error processing tokens: {e}]"