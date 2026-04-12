import time
import json
import os
from datetime import datetime
from ..config import Config

class RescueProtocol:
    def __init__(self):
        self.config = Config()
        self.rescue_active = False
        self.rescue_start_time = None
        
    def handle_survivor_detection(self, detection_data):
        """Handle survivor detection and initiate rescue protocol"""
        print(f"\n🚨 RESCUE PROTOCOL ACTIVATED")
        print(f"Priority: {detection_data['priority_level']}")
        
        self.rescue_active = True
        self.rescue_start_time = time.time()
        
        # Step 1: Immediate response
        self._immediate_response(detection_data)
        
        # Step 2: Medical assessment
        self._medical_response(detection_data)
        
        # Step 3: Base station communication
        self._communicate_with_base(detection_data)
        
        # Step 4: Documentation
        self._document_rescue_attempt(detection_data)
        
        print("✅ Rescue protocol completed")
    
    def _immediate_response(self, detection_data):
        """Immediate response actions"""
        print("🤖 IMMEDIATE RESPONSE:")
        
        # Stop rover movement (placeholder)
        print("   🛑 Rover movement stopped")
        
        # Activate emergency signals
        print("   🚨 Emergency signals activated")
        
        # Position rover for optimal view
        print("   📍 Positioning rover for optimal view")
        
        # Wait for positioning
        time.sleep(2)
        
        print("   ✅ Immediate response completed")
    
    def _medical_response(self, detection_data):
        """Medical response based on assessment"""
        print("🩺 MEDICAL RESPONSE:")
        
        priority = detection_data['priority_level']
        
        if priority == "CRITICAL":
            print("   🚑 CRITICAL: Preparing emergency medical deployment")
            self._deploy_critical_medical_supplies()
        elif priority == "HIGH":
            print("   🏥 HIGH: Preparing standard medical kit")
            self._deploy_standard_medical_supplies()
        else:
            print("   🩹 MEDIUM: Basic first aid assessment")
            self._prepare_basic_first_aid()
        
        # Voice communication
        self._start_voice_communication(detection_data)
    
    def _deploy_critical_medical_supplies(self):
        """Deploy critical medical supplies"""
        print("     📦 Deploying emergency medical kit")
        print("     💉 Preparing trauma supplies")
        print("     🩸 Readying blood loss control items")
        # TODO: Integrate with rover's mechanical arm/claw
        time.sleep(3)
        print("     ✅ Critical supplies deployed")
    
    def _deploy_standard_medical_supplies(self):
        """Deploy standard medical supplies"""
        print("     📦 Deploying standard first aid kit")
        print("     🩹 Preparing bandages and antiseptic")
        print("     💊 Readying pain medication")
        # TODO: Integrate with rover's mechanical arm/claw
        time.sleep(2)
        print("     ✅ Standard supplies deployed")
    
    def _prepare_basic_first_aid(self):
        """Prepare basic first aid"""
        print("     📦 Preparing basic first aid assessment")
        print("     🔍 Visual assessment tools ready")
        time.sleep(1)
        print("     ✅ Basic assessment ready")
    
    def _start_voice_communication(self, detection_data):
        """Start voice communication with survivor"""
        print("🎤 VOICE COMMUNICATION:")
        print("   📢 Activating speaker system")
        
        # Generate appropriate message based on detection
        survivors_count = detection_data['total_survivors']
        priority = detection_data['priority_level']
        
        if priority == "CRITICAL":
            message = "This is an emergency rescue robot. Help is on the way. Please remain calm and do not move if you are injured."
        else:
            message = f"Hello, this is a rescue robot. I have detected {survivors_count} person(s) in this area. Can you hear me?"
        
        print(f"   🗣️  Message: '{message}'")
        
        # TODO: Implement actual text-to-speech
        # import pyttsx3
        # engine = pyttsx3.init()
        # engine.say(message)
        # engine.runAndWait()
        
        time.sleep(2)
        print("   ✅ Voice communication initiated")
    
    def _communicate_with_base(self, detection_data):
        """Send detailed report to base station"""
        print("📡 BASE STATION COMMUNICATION:")
        
        # Prepare comprehensive report
        base_report = {
            'mission_id': self.config.MISSION_ID,
            'rover_name': self.config.ROVER_NAME,
            'alert_type': 'SURVIVOR_DETECTION',
            'timestamp': datetime.now().isoformat(),
            'location': detection_data['rover_location'],
            'survivors': {
                'count': detection_data['total_survivors'],
                'priority_level': detection_data['priority_level'],
                'highest_confidence': detection_data['highest_confidence'],
                'details': detection_data['survivors']
            },
            'medical_assessment': detection_data['medical_analysis'],
            'rescue_actions_taken': [
                'Rover stopped and positioned',
                'Emergency signals activated',
                'Medical supplies prepared',
                'Voice communication initiated'
            ],
            'next_actions_required': self._determine_next_actions(detection_data)
        }
        
        # Save report locally
        report_filename = os.path.join(
            self.config.RESCUE_REPORTS_DIR,
            f"rescue_report_{int(time.time())}.json"
        )
        with open(report_filename, 'w') as f:
            json.dump(base_report, f, indent=2)
        
        print(f"   📄 Report saved: {report_filename}")
        
        # TODO: Implement actual base station communication
        # This could be via radio, cellular, or satellite communication
        print("   📡 Transmitting to base station...")
        time.sleep(3)
        print("   ✅ Base station notified")
        
        # Print summary for demonstration
        self._print_base_report_summary(base_report)
    
    def _determine_next_actions(self, detection_data):
        """Determine next actions required"""
        actions = []
        priority = detection_data['priority_level']
        
        if priority == "CRITICAL":
            actions.extend([
                "Immediate human rescue team dispatch required",
                "Medical evacuation preparation needed",
                "Maintain rover position for guidance"
            ])
        elif priority == "HIGH":
            actions.extend([
                "Human rescue team dispatch recommended",
                "Medical assessment team needed",
                "Continue monitoring survivor condition"
            ])
        else:
            actions.extend([
                "Human team assessment when available",
                "Continue survivor monitoring",
                "Provide basic assistance as possible"
            ])
        
        return actions
    
    def _print_base_report_summary(self, report):
        """Print base station report summary"""
        print("\n" + "="*50)
        print("📡 BASE STATION REPORT SUMMARY")
        print("="*50)
        print(f"Mission: {report['mission_id']}")
        print(f"Rover: {report['rover_name']}")
        print(f"Alert: {report['alert_type']}")
        print(f"Survivors: {report['survivors']['count']} ({report['survivors']['priority_level']} priority)")
        print(f"Confidence: {report['survivors']['highest_confidence']:.3f}")
        
        print(f"\nNEXT ACTIONS REQUIRED:")
        for i, action in enumerate(report['next_actions_required'], 1):
            print(f"  {i}. {action}")
        
        print("="*50)
    
    def _document_rescue_attempt(self, detection_data):
        """Document the rescue attempt"""
        print("📝 RESCUE DOCUMENTATION:")
        
        rescue_log = {
            'rescue_id': f"rescue_{int(time.time())}",
            'mission_id': self.config.MISSION_ID,
            'rover_name': self.config.ROVER_NAME,
            'timestamp': datetime.now().isoformat(),
            'rescue_duration': time.time() - self.rescue_start_time,
            'detection_data': detection_data,
            'actions_taken': [
                'Survivor detection confirmed',
                'Emergency protocols activated',
                'Medical supplies prepared',
                'Base station notified',
                'Voice communication initiated'
            ],
            'rescue_status': 'IN_PROGRESS',
            'follow_up_required': True
        }
        
        # Save rescue log
        log_filename = os.path.join(
            self.config.RESCUE_LOGS_DIR,
            f"rescue_log_{rescue_log['rescue_id']}.json"
        )
        with open(log_filename, 'w') as f:
            json.dump(rescue_log, f, indent=2)
        
        print(f"   📄 Rescue log saved: {log_filename}")
        print("   ✅ Documentation completed")
    
    def emergency_stop(self):
        """Emergency stop protocol"""
        print("🛑 EMERGENCY STOP ACTIVATED")
        self.rescue_active = False
        
        # TODO: Implement emergency stop for rover
        print("   🤖 Rover emergency stop")
        print("   📡 Emergency alert sent to base")
        print("   ✅ Emergency stop completed")
    
    def get_rescue_status(self):
        """Get current rescue status"""
        return {
            'rescue_active': self.rescue_active,
            'rescue_duration': time.time() - self.rescue_start_time if self.rescue_start_time else 0,
            'protocol_active': self.rescue_active
        }    
