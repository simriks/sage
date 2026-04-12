from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sqlite3
import json
import threading
import time
import base64
import cv2
from datetime import datetime
import requests
import os
import secrets

app = Flask(__name__)
dashboard_secret_key = os.getenv('DASHBOARD_SECRET_KEY')
if not dashboard_secret_key:
    dashboard_secret_key = secrets.token_hex(32)
    print("⚠️  DASHBOARD_SECRET_KEY not set; generated an ephemeral secret key")
app.config['SECRET_KEY'] = dashboard_secret_key
socketio = SocketIO(app, cors_allowed_origins="*")

class RescueDashboardServer:
    def __init__(self):
        self.setup_database()
        self.active_missions = {}
        self.bot_status = {}
        self.live_feeds = {}
        
        print("🚁 Rescue Dashboard Server Starting...")
        
    def setup_database(self):
        """Initialize SQLite database for mission data"""
        with sqlite3.connect('rescue_missions.db') as conn:
            cursor = conn.cursor()

            # Mission table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id TEXT UNIQUE,
                rover_name TEXT,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                survivor_detected BOOLEAN,
                analysis_complete BOOLEAN,
                location_lat REAL,
                location_lng REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Events table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS mission_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id TEXT,
                event_type TEXT,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
            )
            ''')

            # Survivor analysis table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS survivor_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id TEXT,
                detection_confidence REAL,
                medical_analysis TEXT,
                injury_severity TEXT,
                recommended_action TEXT,
                analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
            )
            ''')
        print("✅ Database initialized")

dashboard_server = RescueDashboardServer()


def _get_json_payload():
    """Safely parse JSON request payload."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    return data


def _error_response(message, status_code=500):
    """Create a structured API error response."""
    return jsonify({'status': 'error', 'message': message}), status_code

# API Endpoints for Bot Communication
@app.route('/api/mission/start', methods=['POST'])
def start_mission():
    """Receive mission start from bot"""
    try:
        data = _get_json_payload()
        if data is None:
            return _error_response('Invalid JSON payload', 400)
        mission_id = data.get('mission_id')
        if not mission_id:
            return _error_response('mission_id is required', 400)
        rover_name = data.get('rover_name', 'Unknown')

        # Store in database
        with sqlite3.connect('rescue_missions.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO missions (mission_id, rover_name, status, start_time, survivor_detected, analysis_complete)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (mission_id, rover_name, 'ACTIVE', datetime.now(), False, False))

        # Update active missions
        dashboard_server.active_missions[mission_id] = {
            'rover_name': rover_name,
            'status': 'ACTIVE',
            'start_time': datetime.now().isoformat(),
            'survivor_detected': False
        }

        # Broadcast to dashboard
        socketio.emit('mission_started', {
            'mission_id': mission_id,
            'rover_name': rover_name,
            'status': 'ACTIVE',
            'timestamp': datetime.now().isoformat()
        })

        print(f"🚨 Mission started: {mission_id} by {rover_name}")
        return jsonify({'status': 'success', 'message': 'Mission registered'})
    except sqlite3.IntegrityError:
        return _error_response('mission_id already exists', 409)
    except sqlite3.Error as exc:
        print(f"❌ Database error in start_mission: {exc}")
        return _error_response('database operation failed')

@app.route('/api/mission/survivor_detected', methods=['POST'])
def survivor_detected():
    """Receive survivor detection from bot"""
    data = _get_json_payload()
    if data is None:
        return jsonify({'status': 'error', 'message': 'Invalid JSON payload'}), 400
    mission_id = data.get('mission_id')
    if not mission_id:
        return jsonify({'status': 'error', 'message': 'mission_id is required'}), 400
    confidence = data.get('confidence', 0.0)
    position = data.get('position', 'Unknown')
    
    # Update database
    with sqlite3.connect('rescue_missions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE missions SET survivor_detected = ? WHERE mission_id = ?
        ''', (True, mission_id))

        cursor.execute('''
        INSERT INTO mission_events (mission_id, event_type, event_data)
        VALUES (?, ?, ?)
        ''', (mission_id, 'SURVIVOR_DETECTED', json.dumps({
            'confidence': confidence,
            'position': position
        })))
    
    # Update active missions
    if mission_id in dashboard_server.active_missions:
        dashboard_server.active_missions[mission_id]['survivor_detected'] = True
        dashboard_server.active_missions[mission_id]['last_detection'] = {
            'confidence': confidence,
            'position': position,
            'timestamp': datetime.now().isoformat()
        }
    
    # Broadcast URGENT alert to dashboard
    socketio.emit('survivor_alert', {
        'mission_id': mission_id,
        'confidence': confidence,
        'position': position,
        'timestamp': datetime.now().isoformat(),
        'alert_level': 'URGENT'
    })
    
    print(f"🚨 SURVIVOR DETECTED in mission {mission_id}!")
    return jsonify({'status': 'success', 'message': 'Survivor detection recorded'})

@app.route('/api/mission/medical_analysis', methods=['POST'])
def medical_analysis():
    """Receive medical analysis from TwelveLabs"""
    data = _get_json_payload()
    if data is None:
        return jsonify({'status': 'error', 'message': 'Invalid JSON payload'}), 400
    mission_id = data.get('mission_id')
    if not mission_id:
        return jsonify({'status': 'error', 'message': 'mission_id is required'}), 400
    analysis = data.get('analysis', {})
    
    # Store analysis
    with sqlite3.connect('rescue_missions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE missions SET analysis_complete = ? WHERE mission_id = ?
        ''', (True, mission_id))

        cursor.execute('''
        INSERT INTO survivor_analysis 
        (mission_id, detection_confidence, medical_analysis, injury_severity, recommended_action)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            mission_id,
            analysis.get('confidence', 0.0),
            json.dumps(analysis.get('medical_details', {})),
            analysis.get('severity', 'Unknown'),
            analysis.get('recommended_action', 'Immediate rescue required')
        ))
    
    # Update active missions
    if mission_id in dashboard_server.active_missions:
        dashboard_server.active_missions[mission_id]['medical_analysis'] = analysis
        dashboard_server.active_missions[mission_id]['analysis_complete'] = True
    
    # Broadcast medical alert
    socketio.emit('medical_analysis_complete', {
        'mission_id': mission_id,
        'analysis': analysis,
        'timestamp': datetime.now().isoformat()
    })
    
    print(f"🏥 Medical analysis complete for mission {mission_id}")
    return jsonify({'status': 'success', 'message': 'Medical analysis recorded'})

@app.route('/api/mission/status', methods=['POST'])
def update_mission_status():
    """Receive general status updates from bot"""
    data = _get_json_payload()
    if data is None:
        return jsonify({'status': 'error', 'message': 'Invalid JSON payload'}), 400
    mission_id = data.get('mission_id')
    status = data.get('status')
    if not mission_id or not status:
        return jsonify({'status': 'error', 'message': 'mission_id and status are required'}), 400
    details = data.get('details', '')
    
    # Store event
    with sqlite3.connect('rescue_missions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO mission_events (mission_id, event_type, event_data)
        VALUES (?, ?, ?)
        ''', (mission_id, 'STATUS_UPDATE', json.dumps({
            'status': status,
            'details': details
        })))
    
    # Broadcast status update
    socketio.emit('status_update', {
        'mission_id': mission_id,
        'status': status,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'status': 'success'})

@app.route('/api/camera_feed', methods=['POST'])
def receive_camera_feed():
    """Receive camera frames from bot"""
    data = _get_json_payload()
    if data is None:
        return jsonify({'status': 'error', 'message': 'Invalid JSON payload'}), 400
    mission_id = data.get('mission_id')
    frame_data = data.get('frame_data')  # base64 encoded
    if not mission_id or not frame_data:
        return jsonify({'status': 'error', 'message': 'mission_id and frame_data are required'}), 400
    
    # Store latest frame for live feed
    dashboard_server.live_feeds[mission_id] = {
        'frame_data': frame_data,
        'timestamp': datetime.now().isoformat()
    }
    
    # Broadcast to connected clients
    socketio.emit('live_feed_update', {
        'mission_id': mission_id,
        'frame_data': frame_data,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'status': 'success'})

# Dashboard Web Interface
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/missions')
def get_missions():
    """Get all missions for dashboard"""
    try:
        with sqlite3.connect('rescue_missions.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT mission_id, rover_name, status, start_time, survivor_detected, analysis_complete
            FROM missions ORDER BY start_time DESC LIMIT 50
            ''')
            missions = cursor.fetchall()

        mission_list = []
        for mission in missions:
            mission_list.append({
                'mission_id': mission[0],
                'rover_name': mission[1],
                'status': mission[2],
                'start_time': mission[3],
                'survivor_detected': mission[4],
                'analysis_complete': mission[5]
            })

        return jsonify(mission_list)
    except sqlite3.Error as exc:
        print(f"❌ Database error in get_missions: {exc}")
        return _error_response('database operation failed')

@app.route('/api/mission/<mission_id>/details')
def get_mission_details(mission_id):
    """Get detailed information for specific mission"""
    try:
        with sqlite3.connect('rescue_missions.db') as conn:
            cursor = conn.cursor()

            # Get mission info
            cursor.execute('SELECT * FROM missions WHERE mission_id = ?', (mission_id,))
            mission = cursor.fetchone()

            # Get events
            cursor.execute('''
            SELECT event_type, event_data, timestamp FROM mission_events 
            WHERE mission_id = ? ORDER BY timestamp DESC
            ''', (mission_id,))
            events = cursor.fetchall()

            # Get analysis
            cursor.execute('SELECT * FROM survivor_analysis WHERE mission_id = ?', (mission_id,))
            analysis = cursor.fetchone()

        return jsonify({
            'mission': mission,
            'events': events,
            'analysis': analysis
        })
    except sqlite3.Error as exc:
        print(f"❌ Database error in get_mission_details: {exc}")
        return _error_response('database operation failed')

# WebSocket Events for Real-time Communication
@socketio.on('connect')
def handle_connect():
    print('🔗 Dashboard client connected')
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('🔌 Dashboard client disconnected')

if __name__ == '__main__':
    print("🚁 Starting Rescue Dashboard Server...")
    print("📊 Dashboard URL: http://localhost:5000")
    print("🔗 API Base URL: http://localhost:5000/api")
    debug_mode = os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true'
    socketio.run(app, host='0.0.0.0', port=5000, debug=debug_mode)
