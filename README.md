# 🚗 Driver Drowsiness Monitoring System

A real-time desktop application engineered to detect signs of driver fatigue through computer vision and dynamic alerting mechanisms. The system utilizes a YOLOv8-based detection pipeline to monitor blink and yawn behavior via webcam, triggering sound alarms and recommending safe rerouting through Google Maps when fatigue thresholds are exceeded.

This modular, Python-powered solution integrates a PyQt5 GUI, MongoDB Atlas for cloud-based session logging, and a robust `.env` configuration approach to ensure secure, scalable deployments. Packaged as a standalone executable using PyInstaller, it is optimized for non-technical users with zero setup friction.

---

## 🧠 Key Capabilities

- **Fatigue Detection**: Implements a YOLOv8 model to monitor eye closure duration, blink frequency, and yawns.
- **Alerting System**: Classifies drowsiness severity (`Normal`, `Moderate`, `Strong`) and triggers corresponding sound alerts.
- **Reroute Logic**: On strong fatigue events, the system locates nearby refreshment stops and opens driving directions via Google Maps.
- **Cloud Session Logging**: Captures and stores monitoring data to MongoDB Atlas for post-analysis and dashboard visualization.
- **Secure Configuration Management**: Utilizes a `.env` file to securely manage API keys and database URIs.
- **Executable Packaging**: Built into a single `.exe` using PyInstaller to ensure easy distribution and compatibility across Windows machines.

---

## 🛠️ Technology Stack

| Component         | Description                                     |
|------------------|-------------------------------------------------|
| GUI Framework     | PyQt5 for interactive monitoring interface      |
| Vision Processing | OpenCV + YOLOv11 via `ultralytics`              |
| Cloud Storage     | MongoDB Atlas via `pymongo`                     |
| Deployment        | PyInstaller for single-file executable          |
| Configuration     | `python-dotenv` for secrets and environment     |
| Dashboard         | Streamlit + Plotly for session analytics        |
| Audio Playback    | `pygame` for fatigue-triggered alarm sounds     |

---

## 🚀 Getting Started

### Installation & Setup

If you prefer not to run the application from source, you can use the standalone executable:

📎 **Download the packaged `.exe` from:**  
👉 [Google Drive link] : (https://drive.google.com/drive/folders/1t4j4fk9pVe5XVK5IPU0coEUpzBFWPW2l?usp=sharing)

No installation is required. Go to dist folder and simply download and double-click the file to launch the application. The system will begin monitoring webcam input and respond to fatigue events with audible alerts and rerouting suggestions.