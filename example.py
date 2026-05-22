import streamlit as st
import re
import numpy as np
from kittentts import KittenTTS
from llama_cpp import Llama

# 1. Setup Models (Cached so they only load once)
@st.cache_resource
def load_models():
    tts = KittenTTS("KittenML/kitten-tts-nano-0.8-int8")
    llm = Llama(model_path="./resources/smollm2-135m-instruct-q8_0.gguf", n_ctx=4096, n_threads=4)
    return tts, llm

tts, llm = load_models()

# 2. Text Cleaning
def clean_for_tts(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'[:{}()\[\]|_+=#@^&*<>/\\~-]', ' ', text)
    return " ".join(text.split()).strip()

# 3. UI Layout
st.title("🐱 SmolLM + KittenTTS Voice Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        llm_prompt = f"<|im_start|>system\nYou are a helpful AI.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        output = llm(llm_prompt, stop=["<|im_end|>"], max_tokens=1024)
        response = output["choices"][0]["text"].strip()
        st.markdown(response)
        
        # Audio Generation
        tts_text = clean_for_tts(response)
        if len(tts_text) > 2:
            try:
                raw_audio = tts.generate(tts_text, voice='Jasper')
                # Scale for Streamlit audio player
                int_audio = (np.clip(raw_audio, -1.0, 1.0) * 32767).astype(np.int16)
                
                # Streamlit's audio component is very stable
                st.audio(int_audio, sample_rate=24000, autoplay=True)
            except Exception as e:
                st.error(f"Audio Error: {e}")

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
