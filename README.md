# mazingira-pathway-alert
# My hand-typed notes without ai(if my writings are convoluted I've told ai to rewrite for me; I'll put that below)
You run gateway.py continuously; it does not require any special libraries at the moment. 
When SMSGate is installed on your Android device, connect to it via its hotspot to make sure it's on the same network

When a user sends to the Android number 'JOIN', the gateway.py will receive the api request from SMSGate and save that number to database.txt(this is currently empty because it's a public GitHub)

broadcast.py is a basic script that uses HTTP requests to send a broadcast to users in the database.txt. This needs more work. It has 2 main functions: read_subscribers_from_database() and broadcast_emergency_alert(custom_message_template)

scan.py was purely made with AI for the sole purpose of brute-forcing to find a suitable gateway for the Python application to access SMSGate via HTTP

TO-DO
Last/Simultaneous Step - Create a dashboard website to run on the laptop itself
This dashboard should be made using Flask to be run locally via localhost
-The dashboard should control 
  -the running of gateway.py (or a similar functionality)
  -the sending of broadcast.py (the user interface of broadcast.py)

gateway.py - Implement SMSGate webhooks to read messages off the tablet instead of using adb, which is unreliable/finicky

broadcast.py - Due to AI implementation necessities, as I discussed with edgarkano987-alt in person, we plan to use a local large language model to help the user make a better broadcast with tips on preparation for climate disasters or change quickly by 'amberlerters', which is critical in times of need. We plan to do this using a very small AI model called Smolvlm. I have/will shortly upload an example code file in a personal project where I used smolvlm locally to generate text locally. It will be under the examples/ folder.  

database.txt - We should change this to database.json for technical standards and to make it accessible to the website in future implementations. The .txt file may be finicky

history.py - create a Python file for the sole purpose of recording the history of broadcasted messages(number, estimated cost), history of inbound messages (searchable on the dashboard) and the period during which phone numbers joined

# AI Improved
# Mazingira Pathway Alert

This system acts as a localised, resilient SMS gateway designed to manage emergency climate alerts and subscriber registrations. It bridges a local Python environment running on a host machine with an Android device handling cellular SMS traffic.

⚙️ Current Project Architecture
The system is split into foundational scripts that manage the network lifecycle, incoming data data pools, and outbound alert dispatches:

gateway.py

The primary core of the application runs continuously to catch inbound text interactions.

Current Functionality: Monitors the Android device's database to detect incoming messages. When a user text includes the keyword "JOIN", the script extracts their information and appends the subscriber record into storage.

Dependencies: Requires zero external libraries at this stage; runs completely on native Python modules.

broadcast.py

An administrative framework handling outbound message distribution using targeted HTTP POST queries.

Current Architecture: Reads comma-separated string entries via read_subscribers_from_database() and creates a structured collection of sub-dictionaries containing phone arrays and regional markers. It then uses broadcast_emergency_alert(custom_message_template) to push payloads sequentially down the local line.

scan.py

A diagnostic network utility built entirely through AI generation.

Purpose: Brute-forces IP addresses across a local subnet range to locate the exact active network endpoint where SMSGate is broadcasting its local API.

📡 Deployment & Networking Rules
To ensure successful data relay between Python and the device, adhere to the following network topology and operational settings:

Network Unity: The Android device must have SMSGate installed. The host computer executing the Python environment must actively connect directly to that Android device's local Wi-Fi Hotspot. This guarantees they occupy the exact same subnet domain.

API Routing Targets: Outbound payloads target the specific CapCom6 Android Gateway local API structure at [http://192.168.1.99:8080/message](http://192.168.1.99:8080/message).

State Isolation: The database.txt file is intentionally omitted or left completely blank in public source control to protect subscriber privacy and retain an empty canvas for local setups.

📋 The Development Roadmap
The system is undergoing architectural upgrades to scale performance and integrate intelligent localised messaging during climate emergencies.

1. Data Layer Upgrade (database.json)
Objective: Formally transition flat-file storage from database.txt into a structured JSON database schema (database.json).

Rationale: Eliminates brittle string-parsing vulnerabilities inherent to unstructured text (like manually splitting lines by commas), aligning data models with engineering standards and providing clean read/write bindings for future web interfaces.

2. Network Integration (gateway.py)
Objective: Drop legacy, hardware-dependent ADB shell queries.

Implementation: Configure native SMSGate HTTP webhooks to instantly route incoming SMS packets straight to a local Python network hook, removing flaky physical wire connections or sleeping wireless ADB ports.

3. Intelligent Broadcast Optimisation (broadcast.py + SmolVLM)
Objective: Implement an edge-AI assistant to aid system operators ("amberlighters") during high-stress disaster windows.

Implementation: Embed SmolVLM to run locally on-device. The model will analyse situational inputs to draft highly optimised, precise emergency instructions and disaster preparation tips.

Reference: Functional baseline code implementations utilising localised SmolVLM models are stored inside the /examples repository folder.

4. Telemetry Logging Framework (history.py)
Objective: Construct a dedicated analytical tracking module.

Tracking Metrics:

Outbound Telemetry: Archive of broadcast transmissions, target phone distributions, and calculated transaction costs.

Inbound Telemetry: Chronological registration tracking, tracking when specific phone cohorts subscribed, and building searchable incoming query hooks.

5. Unified Operator Dashboard (Flask App)
Objective: Build a clean, graphical control application running natively on the operator's laptop web browser via localhost.

Functional Interface Control:

Real-time process controls to start, monitor, or restart gateway.py.

An intuitive UX/UI command centre replacing raw terminal execution for broadcast.py, giving operators text input boxes to deploy alert vectors easily.

Direct database search filters to monitor incoming log structures handled by history.py.

**To find more on how I made the AI-improved document, go see my chat using the link below**
https://gemini.google.com/share/480e6b8212dc
