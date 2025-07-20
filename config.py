import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    # TwelveLabs Configuration
    TWELVELABS_API_KEY = os.getenv("TL_API_KEY")
    
    # Camera Configuration
    BODY_CAMERA_ID = int(os.getenv("BODY_CAMERA_ID", 0))
    VIDEO_RECORDING_DURATION = int(os.getenv("VIDEO_RECORDING_DURATION", 5))
    DETECTION_INTERVAL = int(os.getenv("DETECTION_INTERVAL", 10))
    
    # Detection Configuration
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.75))
    HIGH_PRIORITY_THRESHOLD = float(os.getenv("HIGH_PRIORITY_THRESHOLD", 0.85))
    
    # Rover Configuration
    ROVER_NAME = os.getenv("ROVER_NAME", "RescueBot")
    MISSION_ID = os.getenv("MISSION_ID", "mission_001")
    
    # Directories
    TEMP_VIDEO_DIR = "temp_videos"
    
    # Survivor Detection Queries
    SURVIVOR_QUERIES = [
        "person lying on ground injured",
        "unconscious person on the ground",
        "person trapped under debris or rubble", 
        "injured person calling for help with hands raised",
        "person with visible wounds or bleeding",
        "person in distress showing signs of pain",
        "person sitting or lying motionless",
        "person with torn or damaged clothing indicating injury"
    ]
    
    # Medical Assessment Queries
    MEDICAL_QUERIES = [
        "What injuries or medical conditions are visible on this person?",
        "Is this person conscious or unconscious?",
        "Are there signs of bleeding or open wounds?",
        "What is the apparent severity of this person's condition?",
        "What immediate medical attention might be needed?"
    ]

    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.TWELVELABS_API_KEY:
            raise ValueError("TL_API_KEY is required in .env file")
        
        # Create temp directory if it doesn't exist
        os.makedirs(cls.TEMP_VIDEO_DIR, exist_ok=True)
        
        print("✅ Configuration validated successfully")