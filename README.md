# SAGE - Search And Guidance Engine

AI-powered autonomous rescue rover that uses TwelveLabs Pegasus 1.2 and Google Gemini to detect and assist survivors in disaster zones.

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

## Key Features

- **Dual AI Detection**: Gemini for real-time target acquisition, TwelveLabs for medical assessment
- **Intelligent Tracking**: Automatic person detection with automated rover movement
- **Medical Analysis**: AI-powered injury assessment with rescue priority classification
- **Live Dashboard**: Real-time mission monitoring and survivor alerts

---

## Quick Start

### Installation

```bash
git clone https://github.com/yourusername/sage.git
cd sage
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
TL_API_KEY=your_twelvelabs_api_key
GEMINI_API_KEY=your_gemini_api_key
BODY_CAMERA_ID=0
PI_IP=10.33.22.106
PI_PORT=50000
```

### Usage

Start the main system:
```bash
python main.py
```

Start the dashboard (optional):
```bash
cd rescue_dashboard
python rescue_dashboard_server.py
```
Open browser to `http://localhost:5000`

---

## How It Works

1. **Target Acquisition**: Gemini analyzes images to detect and center on survivors
2. **Medical Assessment**: TwelveLabs analyzes video to assess injuries and prioritize rescue
3. **Rescue Protocol**: Automated emergency response with medical supply deployment
4. **Dashboard**: Real-time monitoring and mission logging

---

## Project Structure

```
sage/
├── main.py                      # Main system entry point
├── body_detection.py            # TwelveLabs integration
├── camera_manager.py            # Camera control
├── gemini_bmp_detector.py       # Gemini detection
├── rescue_protocol.py           # Rescue procedures
├── config.py                    # Configuration
└── rescue_dashboard/            # Web dashboard
```

---

## Technologies

- **TwelveLabs Pegasus 1.2**: Video analysis
- **Google Gemini 1.5 Flash**: Real-time image detection
- **OpenCV**: Camera control
- **Flask**: Web dashboard
- **Raspberry Pi**: Rover control

---

## Troubleshooting

**Camera not working?** Try different `BODY_CAMERA_ID` values (0, 1, 2)

**API issues?** Verify your API keys in `.env`

**Pi connection failed?** Check `PI_IP` and ensure Pi control server is running

---

## Author

**Sehaj** - Initial development

---

*Built for search and rescue operations*
