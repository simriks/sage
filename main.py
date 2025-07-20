#!/usr/bin/env python3
"""
Rescue Rover Body Detection System
Main entry point for the rescue robot body detection system using TwelveLabs API.
"""

import sys
import signal
import time
from datetime import datetime
from config import Config
from camera_manager import CameraManager
from body_detection import BodyDetectionSystem
from rescue_protocol import RescueProtocol

class RescueRoverSystem:
    def __init__(self):
        print("🤖 Initializing Rescue Rover Body Detection System")
        print("="*60)
        
        # Validate configuration
        Config.validate_config()
        
        # Initialize components
        self.camera_manager = CameraManager()
        self.body_detection = BodyDetectionSystem(self.camera_manager)
        self.rescue_protocol = RescueProtocol()
        
        # System state
        self.system_active = False
        self.mission_start_time = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("✅ System components initialized")
    
    def start_mission(self):
        """Start the rescue mission"""
        print("\n🚁 STARTING RESCUE MISSION")
        print("="*60)
        print(f"Mission ID: {Config.MISSION_ID}")
        print(f"Rover Name: {Config.ROVER_NAME}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # Step 1: Initialize camera
            print("\n📷 CAMERA INITIALIZATION")
            if not self.camera_manager.start_camera():
                print("❌ Failed to initialize camera system")
                return False
            
            # Step 2: Start body detection
            print("\n🔍 BODY DETECTION SYSTEM")
            detection_thread = self.body_detection.start_detection_system()
            
            # Step 3: System ready
            self.system_active = True
            self.mission_start_time = time.time()
            
            print("\n✅ RESCUE ROVER FULLY OPERATIONAL")
            print("="*60)
            self._print_system_status()
            print("="*60)
            print("Press Ctrl+C to stop mission\n")
            
            # Main mission loop
            self._mission_loop()
            
        except Exception as e:
            print(f"❌ Mission failed: {e}")
            return False
        finally:
            self._shutdown_system()
    
    def _mission_loop(self):
        """Main mission monitoring loop"""
        status_update_interval = 30  # seconds
        last_status_update = 0
        
        while self.system_active:
            try:
                current_time = time.time()
                
                # Print status updates periodically
                if current_time - last_status_update >= status_update_interval:
                    self._print_mission_status()
                    last_status_update = current_time
                
                # Check for system health
                self._check_system_health()
                
                # Sleep to prevent CPU overload
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Mission interrupted by user")
                break
            except Exception as e:
                print(f"❌ Mission loop error: {e}")
                time.sleep(5)
    
    def _print_system_status(self):
        """Print current system status"""
        camera_status = self.camera_manager.get_camera_status()
        detection_status = self.body_detection.get_detection_status()
        
        print("📊 SYSTEM STATUS:")
        print(f"   Camera: {'🟢 Active' if camera_status['is_running'] else '🔴 Inactive'}")
        print(f"   Camera Type: {camera_status['camera_type']}")
        print(f"   Detection: {'🟢 Active' if detection_status['is_detecting'] else '🔴 Inactive'}")
        print(f"   Frame Queue: {camera_status['queue_size']} frames")
        print(f"   Detection Index: {detection_status['index_id']}")
    
    def _print_mission_status(self):
        """Print periodic mission status"""
        if not self.mission_start_time:
            return
        
        mission_duration = time.time() - self.mission_start_time
        detection_status = self.body_detection.get_detection_status()
        
        print(f"\n⏱️  MISSION STATUS UPDATE - {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Mission Duration: {mission_duration/60:.1f} minutes")
        print(f"   Total Scans: {detection_status['total_scans']}")
        print(f"   Survivors Found: {detection_status['survivors_found']}")
        print(f"   Last Scan: {(time.time() - detection_status['last_scan_time'])/60:.1f} minutes ago")
        
        if detection_status['survivors_found'] > 0:
            print(f"   🚨 Active Rescues: {detection_status['survivors_found']}")
    
    def _check_system_health(self):
        """Check system health and handle issues"""
        camera_status = self.camera_manager.get_camera_status()
        detection_status = self.body_detection.get_detection_status()
        
        # Check camera health
        if not camera_status['is_running']:
            print("⚠️  Camera system offline - attempting restart...")
            self.camera_manager.start_camera()
        
        # Check queue health - fix the logic here
        queue_size = camera_status['queue_size']
        if queue_size == 0 and camera_status['is_running']:
            print("⚠️  No frames in queue - camera may need restart")
        elif queue_size > 25:
            print("⚠️  Frame queue getting full")
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {sig} - shutting down gracefully...")
        self.system_active = False
    
    def _shutdown_system(self):
        """Gracefully shutdown all systems"""
        print("\n🛑 SHUTTING DOWN RESCUE ROVER SYSTEM")
        print("="*60)
        
        # Stop body detection
        if hasattr(self.body_detection, 'stop_detection_system'):
            self.body_detection.stop_detection_system()
        
        # Stop camera
        if hasattr(self.camera_manager, 'stop_camera'):
            self.camera_manager.stop_camera()
        
        # Print final mission summary
        self._print_mission_summary()
        
        print("✅ System shutdown complete")
        print("="*60)
    
    def _print_mission_summary(self):
        """Print final mission summary"""
        if not self.mission_start_time:
            return
        
        mission_duration = time.time() - self.mission_start_time
        detection_status = self.body_detection.get_detection_status()
        
        print("📊 MISSION SUMMARY:")
        print(f"   Mission Duration: {mission_duration/60:.1f} minutes")
        print(f"   Total Scans Performed: {detection_status['total_scans']}")
        print(f"   Survivors Found: {detection_status['survivors_found']}")
        print(f"   Detection Rate: {(detection_status['survivors_found']/max(detection_status['total_scans'], 1)):.2f} per scan")
        print(f"   System Uptime: {(mission_duration/3600):.2f} hours")

def main():
    """Main entry point"""
    print("🤖 Rescue Rover Body Detection System v1.0")
    print("Powered by TwelveLabs AI")
    print("="*60)
    
    try:
        # Create and start rescue rover system
        rescue_rover = RescueRoverSystem()
        rescue_rover.start_mission()
        
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
    
    print("\n👋 Rescue Rover System terminated")

if __name__ == "__main__":
    main()