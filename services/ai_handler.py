import os
import threading
from llama_cpp import Llama

# Modern GenAI library integration to silence the legacy FutureWarning notice
try:
    from google import genai
    from google.genai import types
    HAS_GEMINI_LIB = True
except ImportError:
    # Fallback to legacy if the environment hasn't been updated via pip yet
    try:
        import google.generativeai as genai
        HAS_GEMINI_LIB = True
    except ImportError:
        HAS_GEMINI_LIB = False

# 1. Thread Mutual Exclusion Lock (Mutex)
# Prevents multiple concurrent Flask requests from corrupting the C++ layer memory allocations
ai_inference_lock = threading.Lock()

# Global tracking variable to maintain a single memory cache allocation for the local model
_local_llm_instance = None

# Dynamically resolve pathing relative to the location of this service script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "smollm2-135m-instruct-q8_0.gguf")


def get_local_engine():
    """
    Lazy-initialization singleton container. Allocates system memory for 
    the model weights exactly once on the first inbound inference request.
    """
    global _local_llm_instance
    
    if _local_llm_instance == None:
        print(f"[AI ENGINE] Mounting Weights into RAM: {MODEL_PATH}")
        
        # Instantiate local Llama engine matching context parameters found in your logs
        _local_llm_instance = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,       # Set to 512 tokens to match terminal allocation capacity
            verbose=True     # Keeps native llama.cpp performance telemetry visible in terminal
        )
        print("[AI ENGINE] Model context verified successfully!")
        
    return _local_llm_instance


def generate_ai_broadcast(user_prompt):
    """
    Executes the Dual-Mode Inference loop sequence.
    Attempts cloud API generation if an API key is present; drops down safely to 
    the air-gapped local engine using a strict thread-safe queue lock if offline.
    """
    # System engineering instructions extracted directly from your application's request parameters
    system_prompt = (
        "You are a helpful field assistant drafting a clear, informative text message for rural community outreach. "
        "Transform the request below into a brief, direct, paragraph-style SMS message that explains the concept or gives practical advice. "
        "Do not include any headers, greeting intros, closing signatures, bullet points, or markdown formatting. "
        "Output ONLY the text message body ready to send down an SMS line.\n\n"
        f"Request: {user_prompt}"
    )

    # MODE 1: High-Capability Cloud Inference (If API key is bound and system is online)
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key and HAS_GEMINI_LIB:
        try:
            # Check if using modern google-genai client library structure
            if hasattr(genai, 'Client'):
                client = genai.Client(api_key=gemini_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=system_prompt,
                )
                if response and response.text:
                    return response.text.strip()
            else:
                # Fallback implementation configuration for legacy generativeai layout
                genai.configure(api_key=gemini_key)
                legacy_model = genai.GenerativeModel('gemini-2.5-flash')
                response = legacy_model.generate_content(system_prompt)
                if response and response.text:
                    return response.text.strip()
        except Exception as cloud_error:
            # Network timeout, API restriction, or air-gapped drop -> transition to fallback mode
            pass

    # MODE 2: Air-Gapped Local Resource Fallback Engine
    print("[AI ENGINE] Routing prompt to local engine (smollm2-135m-instruct-q8_0.gguf)...")
    
    # The Lock ensures that if a user double-clicks or submits concurrently, requests queue up linearly
    with ai_inference_lock:
        try:
            # Retrieve or initialize the native model reference
            llm = get_local_engine()
            
            # Format raw strings into target Smollm2 GGUF chat token templates
            formatted_input = (
                f"<|im_start|>system\nYou are a helpful AI assistant named SmolLM, trained by Hugging Face<|im_end|>\n"
                f"<|im_start|>user\n{system_prompt}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )
            
            # Fire local generation loop
            output = llm(
                formatted_input,
                max_tokens=150,
                stop=["<|im_end|>", "<|endoftext|>"],
                echo=False
            )
            
            # Extract final text block clean slice
            generated_text = output['choices'][0]['text'].strip()
            return generated_text
            
        except Exception as local_error:
            print(f"[AI ENGINE FAULT] Fatal runtime crash during fallback cycle: {local_error}")
            return "Error: Local inferencing engine is busy or unavailable. Please try again."