# Climalink: Offline-First Climate & Agricultural SMS Broadcast Gateway

Climalink is an offline-first, resilient communication platform designed for rural community outreach. It enables administrators to broadcast automated, AI-generated climate advice and environmental alerts directly to community members over legacy cellular networks—**even when completely disconnected from the internet**. 

By utilizing a hybrid "Dual-Mode" backend, the system seamlessly uses powerful cloud APIs when online and safely drops down to an air-gapped, highly optimized local Large Language Model (LLM) when offline, bridging the digital divide for underserved regions.

---

## 🚀 Key Technical Innovations (For Judges)

* **Dual-Mode Inference Loop:** Automatically detects internet connectivity. Uses Google Gemini 2.5 Flash when online and gracefully falls back to a locally hosted, quantized `SmolLM2-135M` model when offline.
* **Thread-Safe Mutex Engineering:** Implements strict Python `threading.Lock()` controls around native C++ execution structures to prevent multi-threaded Flask race conditions and runtime core dumps.
* **Hardware Bridge Routing:** Connects directly to consumer mobile networks by tunneling data via Android Debug Bridge (ADB) to an on-device gateway (SMSGate), avoiding expensive commercial SMS API dependencies.
* **Automated Registration Node:** Contains an inbound webhook module allowing new community members to autonomously text a keyword (`JOIN [Zone]`) to automatically register into local outreach sectors.

---

## 🛠️ Prerequisites & System Requirements

Before setting up the software, ensure your environment meets the following conditions:
* **Operating System:** Linux (Ubuntu/Debian) or Unix-based macOS.
* **Python Version:** Python 3.10 or higher.
* **Hardware Bridge:** Android Device with **USB Debugging Enabled** in Developer Options.
* **Android Tools:** Android Debug Bridge (`adb`) installed on the host machine.
    * *Linux:* `sudo apt update && sudo apt install android-tools-adb -y`
    * *macOS:* `brew install android-platform-tools`

---

## ⚙️ Automated Installation & Quickstart

We have provided an automated, all-in-one bootstrapper script (`run.sh`) that provisions the environment, checks model status, sets up the phone network routing, and boots the platform.

### Step 1: Clone & Navigate to Project Directory
```bash
cd ~/Desktop/coding-project/mazingira_gateway