import json
import os
import re
import threading
from llama_cpp import Llama

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "settings.json")

ai_inference_lock = threading.Lock()
_models_cache = {}


def load_settings():
    default_settings = {
        "force_offline": True,
        "use_translator": True,
        "reasoning_model_path": "models/reasoning/Gemma-3-1B-it-GLM-4.7-Flash-Thinking_Q8_0.gguf",
        "local_model_path": "models/text-reply/gemma-3-1b-it-q4_0.gguf",
        "translator_model_path": "models/translator/swahili-gemma-1b-q4_k_m.gguf",
        "max_tokens": 1024
    }
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return {**default_settings, **json.load(f)}
        except Exception:
            pass
    return default_settings


def save_settings(updated_dict):
    cfg = load_settings()
    cfg.update(updated_dict)
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def get_model_instance(model_rel_path, n_ctx=2048):
    global _models_cache
    model_full_path = os.path.join(BASE_DIR, model_rel_path)
    
    if not os.path.exists(model_full_path):
        model_full_path = os.path.join(BASE_DIR, "models/text-reply/gemma-3-1b-it-q4_0.gguf")

    if model_full_path not in _models_cache:
        print(f"[AI ENGINE] Mounting Model: {model_full_path}")
        _models_cache[model_full_path] = Llama(model_path=model_full_path, n_ctx=n_ctx, verbose=False)
        
    return _models_cache[model_full_path]


def translate_to_swahili_local(english_text, cfg, override_toggle=None):
    active_toggle = override_toggle if override_toggle is not None else cfg.get("use_translator", True)

    if not active_toggle or not english_text.strip():
        return english_text

    try:
        llm = get_model_instance(cfg["translator_model_path"])
        prompt = (
            f"<start_of_turn>user\nTafsiri ujumbe huu kwa Kiswahili rahisi cha kilimo ukitumia aya mbili fupi (aya ya kwanza iwe muhtasari, ya pili iwe hatua ya vitendo):\n\n"
            f"\"{english_text}\"<end_of_turn>\n<start_of_turn>model\n"
        )
        # Increased max_tokens to 250 to fit two full paragraphs comfortably
        output = llm(prompt, max_tokens=250, temperature=0.1, stop=["<end_of_turn>", "<eos>"], echo=False)
        return output["choices"][0]["text"].strip()
    except Exception as e:
        print(f"⚠️ Translation fault: {e}")
        return english_text


def stream_ai_broadcast(user_prompt, use_translator=None):
    cfg = load_settings()
    if use_translator is None:
        use_translator = cfg.get("use_translator", True)

    with ai_inference_lock:
        try:
            # -------------------------------------------------------------
            # STAGE 1: Richer Thinking Pass (1-2 Short Paragraphs)
            # -------------------------------------------------------------
            reasoning_path = cfg.get("reasoning_model_path", "models/reasoning/Gemma-3-1B-it-GLM-4.7-Flash-Thinking_Q8_0.gguf")
            llm_reasoning = get_model_instance(reasoning_path, n_ctx=2048)

            sys_think_instruction = (
                "You are an agricultural reasoning expert for Kenyan farmers. "
                "Analyze the given weather or crop condition in 1 to 2 short, structured paragraphs inside <think>...</think> tags. "
                "Evaluate the immediate agronomic risks, impact on soil/crops, and potential corrective actions."
            )
            think_prompt = f"<start_of_turn>user\n{sys_think_instruction}\n\nContext: {user_prompt}<end_of_turn>\n<start_of_turn>model\n"

            stream = llm_reasoning(
                think_prompt, 
                max_tokens=600, 
                temperature=0.5, 
                stop=["</think>", "<end_of_turn>", "<eos>"], 
                echo=False, 
                stream=True
            )

            accumulated_thoughts = ""
            for chunk in stream:
                token = chunk["choices"][0]["text"]
                clean_token = token.replace("<think>", "").replace("</think>", "")
                accumulated_thoughts += clean_token
                if clean_token:
                    yield f"data: {json.dumps({'thought_chunk': clean_token})}\n\n"

            # -------------------------------------------------------------
            # STAGE 2: Two-Paragraph Action Draft Pass (Summary + Practical Action)
            # -------------------------------------------------------------
            yield f"data: {json.dumps({'status': 'Synthesizing two-paragraph action broadcast...'})}\n\n"

            llm_action = get_model_instance(cfg["local_model_path"])
            action_prompt = (
                f"<start_of_turn>user\n"
                f"Based on these agricultural reasoning notes:\n{accumulated_thoughts[:1000]}\n\n"
                f"Write a response structured into exactly two short paragraphs:\n"
                f"Paragraph 1: Summary of the situation and agronomic risks.\n"
                f"Paragraph 2: Direct practical action for the farmer.<end_of_turn>\n"
                f"<start_of_turn>model\n"
            )

            action_output = llm_action(
                action_prompt, 
                max_tokens=150,  # Increased max tokens to allow space for two paragraphs
                temperature=0.2, 
                stop=["<end_of_turn>", "<eos>"], 
                echo=False
            )

            raw_english_reply = action_output["choices"][0]["text"].strip()
            raw_english_reply = re.sub(r"^Okay,?\s*here'?s.*?:", "", raw_english_reply, flags=re.IGNORECASE).strip()

            if not raw_english_reply:
                raw_english_reply = (
                    "Severe weather conditions pose a significant risk of crop damage and nutrient runoff across local agricultural zones.\n\n"
                    "Dig small drainage channels around farm plots immediately to divert excess rainwater away from root zones."
                )

            # If Swahili Translation is OFF, output English draft immediately
            if not use_translator:
                yield f"data: {json.dumps({'token': raw_english_reply})}\n\n"

            # -------------------------------------------------------------
            # STAGE 3: Swahili Translation Pass
            # -------------------------------------------------------------
            if use_translator:
                yield f"data: {json.dumps({'status': 'Translating to Kiswahili...'})}\n\n"
                swahili_reply = translate_to_swahili_local(raw_english_reply, cfg, override_toggle=True)
                yield f"data: {json.dumps({'token': swahili_reply})}\n\n"

        except Exception as e:
            print(f"❌ [STREAM FAULT] {e}")
            yield f"data: {json.dumps({'token': f'Error: {str(e)}'})}\n\n"

    yield "data: [DONE]\n\n"


def generate_ai_response(user_prompt, phone_number=None, is_broadcast=False):
    cfg = load_settings()
    sys_instruction = "Give 1 short summary paragraph and 1 direct practical action paragraph for a Kenyan farmer."
    
    with ai_inference_lock:
        try:
            llm = get_model_instance(cfg["local_model_path"])
            out = llm(
                f"<start_of_turn>user\n{sys_instruction}\n\nQuestion: {user_prompt}<end_of_turn>\n<start_of_turn>model\n",
                max_tokens=180, temperature=0.2, stop=["<end_of_turn>", "<eos>"], echo=False
            )
            raw = out["choices"][0]["text"].strip()
            cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
            cleaned = re.sub(r"^Okay,?\s*here'?s.*?:", "", cleaned, flags=re.IGNORECASE).strip()
        except Exception:
            cleaned = (
                "Weather conditions pose immediate risks to vulnerable crops and soil stability in your region.\n\n"
                "Clear small drainage channels around your farm to direct water away from roots."
            )

        return translate_to_swahili_local(cleaned, cfg)


def generate_ai_broadcast(user_prompt):
    return generate_ai_response(user_prompt, is_broadcast=True)