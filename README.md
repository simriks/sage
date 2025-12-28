# SAGE - Search And Guidance Engine

## AI-Powered Rescue Rover System

SAGE is an intelligent autonomous rescue rover system that uses advanced computer vision and AI to detect, locate, and assist survivors in disaster zones. The system combines multiple AI technologies including TwelveLabs Pegasus 1.2 for video analysis and Google Gemini for real-time image detection to create a comprehensive search and rescue platform.

---

## Key Features

### Dual-Stage Detection System
- **Stage 1 - Target Acquisition (Gemini)**: Real-time image analysis for survivor detection and positioning
- **Stage 2 - Medical Assessment (TwelveLabs)**: Deep video analysis for injury assessment and rescue prioritization

### Intelligent Target Tracking
- Automatic person detection and centering
- Confidence-based decision making
- Automated rover movement control via HTTP commands

### Medical Analysis
- AI-powered injury severity assessment
- Automatic rescue priority classification (Low/Medium/High/Critical)
- Detailed survivor condition reporting

### Real-Time Dashboard
- Live mission monitoring
- Real-time survivor alerts
- Medical analysis visualization
- Mission history and event logging

### Automated Rescue Protocol
- Immediate response actions
- Medical supply deployment logic
- Voice communication system integration
- Base station reporting

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SAGE RESCUE ROVER                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Camera Manager  │────────▶│  Body Detection  │         │
│  │   (OpenCV)       │         │   (TwelveLabs)   │         │
│  └──────────────────┘         └──────────────────┘         │
│           │                             │                    │
│           ▼                             ▼                    │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Gemini BMP      │         │ Rescue Protocol  │         │
│  │   Detector       │────────▶│   Activation     │         │
│  └──────────────────┘         └──────────────────┘         │
│           │                             │                    │
│           └─────────────┬───────────────┘                    │
│                         ▼                                    │
│              ┌──────────────────┐                           │
│              │  Raspberry Pi    │                           │
│              │  Motor Control   │                           │
│              └──────────────────┘                           │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │  Web Dashboard   │
                │  (Flask + SQLite)│
                └──────────────────┘
```

---

## Core Components

### 1. Main System (`main.py`)
- Central orchestrator for the entire rescue rover
- Manages system lifecycle and mission monitoring
- Coordinates all subsystems
- Handles graceful shutdowns and error recovery

### 2. Camera Manager (`camera_manager.py`)
- OpenCV-based camera control
- Multi-threaded frame capture
- Video recording for analysis
- Frame queue management (30 frame buffer)
- Dual recording methods (queue-based and direct)

### 3. Body Detection System (`body_detection.py`)
- TwelveLabs Pegasus 1.2 integration
- Automated video analysis every N seconds
- Survivor detection with confidence scoring
- Medical condition assessment
- JSON-structured analysis output

### 4. Gemini BMP Detector (`gemini_bmp_detector.py`)
- Real-time image analysis for target acquisition
- Person detection and centering logic
- BMP file management and cleanup
- HTTP-based rover movement commands
- Target lock mechanism

### 5. Rescue Protocol (`rescue_protocol.py`)
- Automated emergency response procedures
- Medical supply deployment logic
- Voice communication system
- Base station reporting
- Rescue documentation and logging

### 6. Rescue Dashboard (`rescue_dashboard/`)
- Flask-based web server
- Real-time WebSocket communication
- SQLite mission database
- Live camera feed streaming
- Mission history and analytics

### 7. Configuration (`config.py`)
- Centralized configuration management
- Environment variable support
- API key management
- Camera and detection parameters

---

## Installation

### Prerequisites
- Python 3.8+
- OpenCV compatible camera
- TwelveLabs API key
- Google Gemini API key
- Raspberry Pi (for physical rover control)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/sage.git
cd sage
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
Create a `.env` file in the project root:

```env
# TwelveLabs Configuration
TL_API_KEY=your_twelvelabs_api_key_here

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Camera Configuration
BODY_CAMERA_ID=0
VIDEO_RECORDING_DURATION=5
DETECTION_INTERVAL=10

# Detection Thresholds
CONFIDENCE_THRESHOLD=0.75
HIGH_PRIORITY_THRESHOLD=0.85

# Rover Configuration
ROVER_NAME=RescueBot
MISSION_ID=mission_001

# Raspberry Pi Configuration
PI_IP=10.33.22.106
PI_PORT=50000

# Gemini Detection
MOVEMENT_FRAME_RATE=0.25
TARGET_KEYWORD=TARGET_LOCKED
```

### Step 4: Install Dashboard Dependencies (Optional)
```bash
cd rescue_dashboard
pip install -r requirements_dashboard.txt
```

---

## Usage

### Starting the Main Rescue System

```bash
python main.py
```

This will:
1. Validate configuration
2. Initialize camera system
3. Start body detection system
4. Begin survivor scanning

### Starting the Dashboard (Separate Terminal)

```bash
cd rescue_dashboard
python rescue_dashboard_server.py
```

Then open your browser to: `http://localhost:5000`

### Testing Gemini Detection Only

```bash
python gemini_bmp_detector.py
```

---

## How It Works

### Mission Flow

1. **System Startup**
   - Camera initialization
   - TwelveLabs index creation
   - Gemini API connection
   - Raspberry Pi connection test

2. **Stage 1: Target Acquisition (Gemini)**
   - Continuous image capture (0.25s intervals)
   - Real-time person detection
   - Position and centering analysis
   - When target locked:
     - Sends HTTP command to Pi
     - Rover stops spinning
     - Rover moves toward target

3. **Stage 2: Detailed Analysis (TwelveLabs)**
   - Records 5-second video segments
   - Uploads to TwelveLabs Pegasus
   - Analyzes for:
     - Survivor count
     - Injury severity
     - Medical conditions
     - Rescue priority level
   - Repeats every 10 seconds

4. **Rescue Protocol Activation**
   - Immediate rover stop and positioning
   - Emergency signals activation
   - Medical supply preparation
   - Voice communication
   - Base station notification
   - Mission documentation

5. **Dashboard Monitoring**
   - Real-time mission status
   - Live camera feed
   - Survivor alerts
   - Medical analysis display
   - Mission history

---

## Configuration Options

### Camera Settings
- `BODY_CAMERA_ID`: Camera device index (default: 0)
- `VIDEO_RECORDING_DURATION`: Seconds per video clip (default: 5)
- `DETECTION_INTERVAL`: Seconds between scans (default: 10)

### Detection Thresholds
- `CONFIDENCE_THRESHOLD`: Minimum confidence for detection (default: 0.75)
- `HIGH_PRIORITY_THRESHOLD`: Threshold for high priority alerts (default: 0.85)

### Gemini Movement Detection
- `MOVEMENT_FRAME_RATE`: Time between Gemini frames (default: 0.25s)
- `TARGET_KEYWORD`: Keyword for target lock (default: "TARGET_LOCKED")

### Raspberry Pi Control
- `PI_IP`: IP address of the Pi (default: 10.33.22.106)
- `PI_PORT`: Control port (default: 50000)

---

## Project Structure

```
sage/
├── main.py                      # Main system entry point
├── body_detection.py            # TwelveLabs integration
├── camera_manager.py            # Camera control
├── gemini_bmp_detector.py       # Gemini detection system
├── rescue_protocol.py           # Rescue procedures
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
│
├── temp_videos/                 # Temporary video storage
├── gemini_frames/               # Gemini detection frames
├── temp_files/                  # Temporary files
│
├── rescue_dashboard/            # Web dashboard
│   ├── rescue_dashboard_server.py
│   ├── requirements_dashboard.txt
│   ├── rescue_missions.db       # SQLite database
│   ├── templates/               # HTML templates
│   └── run_dashboard.sh
│
└── README.md                    # This file
```

---

## Technologies Used

### AI & Computer Vision
- **TwelveLabs Pegasus 1.2**: Advanced video understanding and analysis
- **Google Gemini 1.5 Flash**: Real-time image analysis and decision making
- **OpenCV**: Camera control and video processing

### Backend
- **Python 3.8+**: Core programming language
- **Flask**: Web dashboard server
- **Flask-SocketIO**: Real-time communication
- **SQLite**: Mission data storage

### Hardware Integration
- **Raspberry Pi**: Rover motor control
- **HTTP API**: Pi communication protocol

---

## System Output

### Console Output
```
Initializing Rescue Rover Body Detection System
============================================================
Configuration validated successfully
System components initialized

STARTING RESCUE MISSION
============================================================
Mission ID: mission_001
Rover Name: RescueBot
Start Time: 2024-12-27 15:30:00
============================================================

CAMERA INITIALIZATION
Camera initialized successfully

BODY DETECTION SYSTEM
Detection index created: idx_abc123
Starting detection scan #1

SURVIVORS DETECTED: 1 found!
Description: Person lying on ground showing signs of distress
Priority Level: HIGH
Recommended Action: Immediate medical assessment required
```

### Analysis Output Format
```json
{
    "survivors_detected": true,
    "survivor_count": 1,
    "detailed_description": "Person lying on ground with visible injuries",
    "survivor_details": [
        {
            "position": "Center-left of frame, approximately 10 meters ahead",
            "condition": "Visible bleeding, appears unconscious",
            "urgency_level": "critical",
            "confidence": 0.92
        }
    ],
    "rescue_priority": "critical",
    "recommended_action": "Immediate medical evacuation required"
}
```

---

## Security Notes

- Store API keys in `.env` file (never commit to Git)
- Add `.env` to `.gitignore`
- Use HTTPS for production deployments
- Secure Raspberry Pi communication with authentication
- Restrict dashboard access with proper authentication

---

## Troubleshooting

### Camera Issues
```
Camera initialization failed
```
**Solution**: 
- Check camera connection
- Try different `BODY_CAMERA_ID` values (0, 1, 2)
- Ensure camera permissions are granted

### API Connection Issues
```
Failed to create detection index
```
**Solution**:
- Verify TwelveLabs API key is correct
- Check internet connection
- Ensure API quota is available

### Raspberry Pi Connection Failed
```
Cannot connect to Pi at http://10.33.22.106:50000/injury
```
**Solution**:
- Verify Pi is powered on
- Check IP address and port
- Ensure Pi control server is running
- Test network connectivity

---

## Future Enhancements

- Multi-rover coordination
- GPS integration for location tracking
- Thermal camera support
- Voice recognition for survivor communication
- Automated medical supply dispensing
- Drone integration for aerial surveillance
- Mobile app for dashboard
- Advanced path planning and navigation
- Multi-language support

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Authors

- **Sehaj** - *Initial work and development*

---

## Acknowledgments

- TwelveLabs for providing advanced video understanding APIs
- Google for Gemini AI capabilities
- OpenCV community for computer vision tools
- The open-source community for various libraries used

---

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Email: [your-email@example.com]
- Documentation: [Link to docs if available]

---

**Built for Search and Rescue Operations**

*Making the world a safer place, one rescue at a time.*
