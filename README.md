# Mazingira-Gateway Offline-First Climate & Agricultural SMS Broadcast Gateway

Mazingira-Gateway is an offline-first, resilient communication platform designed for rural community outreach. It enables administrators to broadcast automated, AI-generated climate advice and environmental alerts directly to community members over legacy cellular networks—**even when completely disconnected from the internet**. 

By utilizing a hybrid "Dual-Mode" backend, the system seamlessly uses powerful cloud APIs when online and safely drops down to an air-gapped, highly optimized local Large Language Model (LLM) when offline, bridging the digital divide for underserved regions.

---

## 🚀 Key Technical Innovations & Hurdles Overcome

### 1. Dual-Mode Inference Loop
The core engine automatically detects internet connectivity parameters. It favors Google Gemini 2.5 Flash via the cloud when online, but gracefully drops to an entirely air-gapped, resource-optimized, local `SmolLM2-135M` GGUF model when network drops occur.

### 2. Resolving Native Memory Corruption (Thread-Safety)
During stress-testing, rapid or concurrent web requests into the underlying C++ layers of `llama-cpp-python` caused memory buffer collisions (`get_logits_ith: invalid logits id -2`), throwing fatal `GGML_ASSERT` crashes that completely brought down the Flask server. 
* **The Fix:** We engineered a strict **Mutual Exclusion (Mutex) Lock** using Python's `threading.Lock()` to encapsulate the local inference execution loop. This forces simultaneous requests to wait safely in a linear queue, completely eliminating multi-threaded race conditions.

### 3. Hardware Bridge Routing & Enrollment
Instead of relying on expensive, proprietary commercial SMS APIs, Climalink utilizes **Android Debug Bridge (ADB)** to route data down a physical USB cable directly to a connected Android mobile device running an integrated gateway (`SMSGate`). Furthermore, an inbound webhook parser handles incoming messages containing the keyword `JOIN [Zone]`, creating a fully automated, self-service user registration database.

---

## 🛠️ Prerequisites & System Requirements

Before running the application, ensure your workspace meets these criteria:
* **Python Version:** Python 3.10 or higher installed.
* **Hardware Bridge:** An Android device with **USB Debugging Enabled** in its Developer Settings.
* **Android Platform Tools (ADB):** Must be installed on your system host.
    * **Linux:** `sudo apt install android-tools-adb -y`
    * **macOS:** `brew install android-platform-tools`
    * **Windows:** Download the official ZIP from Android Developer Site and add its path to your System Environment Variables.

---

## 📁 Repository Structure Blueprint

```text
Mazingira-Gateway/
├── models/
│   └── smollm2-135m-instruct-q8_0.gguf  <-- Must download manually (not on GitHub)
├── services/
│   ├── __init__.py
│   ├── ai_handler.py
│   ├── data_handler.py
│   ├── history_handler.py
│   └── sms_sender.py
├── static/
│   └── (CSS stylesheets / Logos)
├── templates/
│   └── index.html
├── .gitignore
├── app.py
├── README.md
├── requirements.txt
├── run.bat                              <-- Automation script for Windows
└── run.sh                               <-- Automation script for Linux/macOS
