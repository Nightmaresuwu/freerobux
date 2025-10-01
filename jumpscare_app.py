#!/usr/bin/env python3
"""
Roblox Free Robux Generator - All-in-One Flask Application
Kombiniert Backend und Frontend in einer einzigen Python-Datei
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string, send_from_directory, session, redirect, url_for
from werkzeug.utils import secure_filename
import logging
from pymongo import MongoClient

# Flask App Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'roblox-prank-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Admin Credentials - Multi-Admin System
ADMIN_ACCOUNTS = {
    "Miko@admin.com": "jumpscare666!!!",
    "Nightmares@admin.com": "jumpscare666!!!"
}

# MongoDB Setup
MONGO_URL = "mongodb+srv://Nightmareshaha:Aimzzon00@cluster0.80nwqlr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "roblox_prank"

# Global MongoDB client and database
client = None
db = None

def init_mongodb():
    """Initialize MongoDB connection"""
    global client, db
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

# Initialize MongoDB on startup
init_mongodb()

# Data Models
class PrankLog:
    def __init__(self, user_agent, choice, ip_address=None, id=None, timestamp=None):
        self.id = id or str(uuid.uuid4())
        self.user_agent = user_agent
        self.choice = choice
        self.ip_address = ip_address
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp,
            'choice': self.choice,
            'ip_address': self.ip_address
        }

class VideoInfo:
    def __init__(self, filename, file_size, is_active=True, uploaded_at=None, id=None):
        self.id = id
        self.filename = filename
        self.uploaded_at = uploaded_at or datetime.utcnow()
        self.file_size = file_size
        self.is_active = is_active
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'uploaded_at': self.uploaded_at,
            'file_size': self.file_size,
            'is_active': self.is_active
        }

class ChatMessage:
    def __init__(self, username, message, timestamp=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'message': self.message,
            'timestamp': self.timestamp
        }

# No need for async helper functions with synchronous PyMongo

# Helper function to check if user is logged in
def is_admin_logged_in():
    return session.get('admin_logged_in', False)

# API Routes
@app.route('/api/')
def api_root():
    """Health check endpoint"""
    return jsonify({"message": "Roblox Robux Generator API is running", "status": "healthy"})

# Admin Login Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if username exists and password matches
        if username in ADMIN_ACCOUNTS and ADMIN_ACCOUNTS[username] == password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return jsonify({"success": True, "message": f"Login successful! Welcome {username}"})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    # Return login form HTML
    return """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login - Roblox Generator</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div class="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 w-full max-w-md">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-white mb-2">🔐 Admin Login</h1>
                <p class="text-white/70">Enter your credentials to access the admin panel</p>
                <div class="mt-4 p-3 bg-blue-500/20 rounded-lg border border-blue-400/30">
                    <p class="text-blue-200 text-sm font-medium">Available Admin Accounts:</p>
                    <p class="text-blue-100 text-xs mt-1">Miko@admin.com • Nightmares@admin.com</p>
                </div>
            </div>
            
            <form id="loginForm" class="space-y-6">
                <div>
                    <label class="block text-white text-sm font-medium mb-2">Username</label>
                    <input type="text" name="username" required 
                           class="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                
                <div>
                    <label class="block text-white text-sm font-medium mb-2">Password</label>
                    <input type="password" name="password" required 
                           class="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                
                <button type="submit" 
                        class="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200">
                    Login
                </button>
            </form>
            
            <div id="message" class="mt-4 text-center"></div>
        </div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const messageDiv = document.getElementById('message');
                
                try {
                    const response = await fetch('/admin/login', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        messageDiv.innerHTML = '<p class="text-green-400">Login successful! Redirecting...</p>';
                        setTimeout(() => {
                            window.location.href = '/';
                        }, 1000);
                    } else {
                        messageDiv.innerHTML = '<p class="text-red-400">Invalid credentials!</p>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<p class="text-red-400">Login failed!</p>';
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect('/')

@app.route('/api/admin/current')
def get_current_admin():
    """Get current admin username"""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"username": session.get('admin_username', 'Unknown')})

# Chat API Routes
@app.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    """Send a chat message"""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message required"}), 400
        
        username = session.get('admin_username', 'Unknown')
        message_text = data['message'].strip()
        
        if not message_text:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Create chat message
        chat_message = ChatMessage(username=username, message=message_text)
        
        # Save to MongoDB
        result = db.chat_messages.insert_one(chat_message.to_dict())
        
        return jsonify({
            "success": True,
            "message": chat_message.to_dict()
        })
    except Exception as e:
        return jsonify({"error": f"Error sending message: {str(e)}"}), 500

@app.route('/api/chat/messages')
def get_chat_messages():
    """Get recent chat messages"""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get last 50 messages
        cursor = db.chat_messages.find().sort("timestamp", -1).limit(50)
        messages = []
        
        for msg in cursor:
            messages.append({
                'id': msg['id'],
                'username': msg['username'],
                'message': msg['message'],
                'timestamp': msg['timestamp'].isoformat()
            })
        
        # Reverse to show oldest first
        messages.reverse()
        
        return jsonify({"messages": messages})
    except Exception as e:
        return jsonify({"error": f"Error getting messages: {str(e)}"}), 500

@app.route('/api/prank-stats', methods=['POST'])
def log_prank():
    """Log when someone clicks on the prank buttons"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get IP address from request
        ip_address = request.remote_addr
        
        choice = data.get('choice', '')
        
        # Parse Robux amount from choice if it's in format "robux_1000"
        robux_amount = None
        if choice.startswith('robux_'):
            try:
                robux_amount = int(choice.split('_')[1])
                choice = 'robux_generation'
            except:
                pass
        
        prank_log = PrankLog(
            user_agent=data.get('user_agent', ''),
            choice=choice,
            ip_address=ip_address
        )
        
        # Add Robux amount to the log if available
        log_data = prank_log.to_dict()
        if robux_amount:
            log_data['robux_amount'] = robux_amount
        
        # Insert into MongoDB
        result = db.prank_logs.insert_one(log_data)
        
        response_data = prank_log.to_dict()
        if robux_amount:
            response_data['robux_amount'] = robux_amount
            
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": f"Error logging prank: {str(e)}"}), 500

@app.route('/api/prank-stats', methods=['GET'])
def get_prank_stats():
    """Get prank statistics for admin dashboard"""
    try:
        # Get total count
        total_pranks = db.prank_logs.count_documents({})
        
        # Get recent pranks (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        cursor = db.prank_logs.find(
            {"timestamp": {"$gte": yesterday}}
        ).sort("timestamp", -1).limit(20)
        
        recent_pranks = []
        for prank in cursor:
            recent_pranks.append({
                'id': prank['id'],
                'user_agent': prank['user_agent'],
                'timestamp': prank['timestamp'].isoformat(),
                'choice': prank['choice'],
                'ip_address': prank['ip_address']
            })
        
        result = {
            'total_views': total_pranks,
            'total_pranks': total_pranks,
            'recent_pranks': recent_pranks
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error getting stats: {str(e)}"}), 500

@app.route('/api/video/current')
def get_current_video():
    """Get current jumpscare video info"""
    try:
        # Check if custom video exists
        video_path = Path('static/jumpscare.mp4')
        
        if video_path.exists():
            return jsonify({
                "videoUrl": "/static/jumpscare.mp4",
                "filename": "jumpscare.mp4",
                "exists": True
            })
        else:
            return jsonify({
                "videoUrl": "/static/placeholder-jumpscare.mp4",
                "filename": "placeholder-jumpscare.mp4", 
                "exists": False,
                "message": "Upload your jumpscare.mp4 to static/ folder"
            })
    except Exception as e:
        return jsonify({"error": f"Error checking video: {str(e)}"}), 500

@app.route('/api/video/upload', methods=['POST'])
def upload_video():
    """Upload new jumpscare video"""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith(('.mp4', '.webm', '.mov')):
            return jsonify({"error": "Only video files allowed (.mp4, .webm, .mov)"}), 400
        
        # Create static directory if it doesn't exist
        static_dir = Path('static')
        static_dir.mkdir(exist_ok=True)
        
        # Save to static folder
        filename = secure_filename('jumpscare.mp4')
        video_path = static_dir / filename
        
        file.save(str(video_path))
        
        # Save video info to MongoDB
        video_info = VideoInfo(
            filename=filename,
            file_size=os.path.getsize(video_path),
            is_active=True
        )
        
        # Remove old entries
        db.video_info.delete_many({})
        # Insert new entry
        result = db.video_info.insert_one(video_info.to_dict())
        
        return jsonify({
            "success": True,
            "filename": filename,
            "message": "Video uploaded successfully"
        })
    except Exception as e:
        return jsonify({"error": f"Error uploading video: {str(e)}"}), 500

@app.route('/api/admin/dashboard')
def get_admin_dashboard():
    """Get admin dashboard data"""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get prank stats
        total_pranks = db.prank_logs.count_documents({})
        
        # Get recent pranks (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        cursor = db.prank_logs.find(
            {"timestamp": {"$gte": yesterday}}
        ).sort("timestamp", -1).limit(20)
        
        recent_pranks = []
        for prank in cursor:
            recent_pranks.append({
                'id': prank['id'],
                'user_agent': prank['user_agent'],
                'timestamp': prank['timestamp'].isoformat(),
                'choice': prank['choice'],
                'ip_address': prank['ip_address']
            })
        
        stats = {
            'total_views': total_pranks,
            'total_pranks': total_pranks,
            'recent_pranks': recent_pranks
        }
        
        # Get video info
        video_info = None
        video_doc = db.video_info.find_one({}, sort=[("uploaded_at", -1)])
        if video_doc:
            video_info = {
                'id': str(video_doc['_id']),
                'filename': video_doc['filename'],
                'uploaded_at': video_doc['uploaded_at'].isoformat(),
                'file_size': video_doc['file_size'],
                'is_active': video_doc['is_active']
            }
        
        result = {
            'stats': stats,
            'video_info': video_info
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error getting dashboard: {str(e)}"}), 500

# Configure static files for Flask
app.static_folder = 'static'
app.static_url_path = '/static'

# Static file serving
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    try:
        return send_from_directory('static', filename)
    except FileNotFoundError:
        return "File not found", 404

# Main Frontend HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Free Robux Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Fredoka', sans-serif; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in { animation: fadeIn 0.6s ease-out; }
        .button-hover:hover { transform: scale(1.05); }
        .button-hover { transition: all 0.2s ease; }
        .roblox-green { background-color: #00A2FF; }
        .roblox-blue { background-color: #0078D4; }
        .roblox-red { background-color: #E60012; }
        .gradient-bg { 
            background: linear-gradient(180deg, #87CEEB 0%, #B0E0E6 30%, #E0F6FF 70%, #F0F8FF 100%);
            background-image: 
                /* City buildings silhouette */
                linear-gradient(90deg, transparent 0%, rgba(100, 149, 237, 0.3) 20%, rgba(70, 130, 180, 0.4) 40%, rgba(100, 149, 237, 0.3) 60%, transparent 100%),
                /* Sky gradient */
                linear-gradient(180deg, rgba(135, 206, 235, 0.8) 0%, rgba(176, 224, 230, 0.6) 50%, rgba(240, 248, 255, 0.9) 100%);
        }
        .slider-container { background: linear-gradient(90deg, #00A2FF 0%, #0078D4 100%); }
        
        /* Custom slider styles */
        .slider::-webkit-slider-thumb {
            appearance: none;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: #FFD700;
            cursor: pointer;
            border: 3px solid #fff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
        
        .slider::-moz-range-thumb {
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: #FFD700;
            cursor: pointer;
            border: 3px solid #fff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body class="min-h-screen gradient-bg flex items-center justify-center p-4">
    <!-- Grid Pattern Background -->
    <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDYwIDAgTCAwIDAgMCA2MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-20"></div>
    
    <!-- Roblox Cityscape Background -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <!-- Large transparent ROBLOX logo at top -->
        <div class="absolute top-8 left-1/2 transform -translate-x-1/2 text-6xl font-bold text-white opacity-30 select-none" style="font-family: 'Arial Black', Arial, sans-serif; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            ROBLOX
        </div>
        
        <!-- City buildings silhouette -->
        <div class="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-gray-800 via-gray-700 to-transparent opacity-60"></div>
        
        <!-- Individual building shapes -->
        <div class="absolute bottom-0 left-0 w-32 h-48 bg-gradient-to-t from-blue-900 to-blue-700 opacity-70"></div>
        <div class="absolute bottom-0 left-32 w-24 h-64 bg-gradient-to-t from-slate-800 to-slate-600 opacity-70"></div>
        <div class="absolute bottom-0 left-56 w-28 h-40 bg-gradient-to-t from-gray-800 to-gray-600 opacity-70"></div>
        <div class="absolute bottom-0 right-0 w-40 h-56 bg-gradient-to-t from-indigo-900 to-indigo-700 opacity-70"></div>
        <div class="absolute bottom-0 right-40 w-32 h-72 bg-gradient-to-t from-blue-800 to-blue-600 opacity-70"></div>
        <div class="absolute bottom-0 right-72 w-24 h-48 bg-gradient-to-t from-slate-700 to-slate-500 opacity-70"></div>
        
        <!-- Roblox Avatars scattered around -->
        <!-- Purple fairy avatar (top left) -->
        <div class="absolute top-20 left-16 w-12 h-16 bg-purple-400 rounded-t-full opacity-80 animate-bounce">
            <div class="w-8 h-8 bg-purple-300 rounded-full mx-auto mt-1"></div>
            <div class="w-16 h-8 bg-purple-500 rounded-full -mt-2"></div>
        </div>
        
        <!-- Golden steampunk avatar (top right) -->
        <div class="absolute top-24 right-20 w-10 h-14 bg-yellow-400 rounded-t-full opacity-80 animate-pulse">
            <div class="w-6 h-6 bg-yellow-300 rounded-full mx-auto mt-1"></div>
            <div class="w-12 h-6 bg-yellow-500 rounded-full -mt-1"></div>
        </div>
        
        <!-- Red scooter avatar (bottom left) -->
        <div class="absolute bottom-32 left-24 w-8 h-10 bg-yellow-300 rounded-t-full opacity-80 animate-bounce">
            <div class="w-6 h-6 bg-yellow-200 rounded-full mx-auto mt-1"></div>
            <div class="w-10 h-4 bg-red-500 rounded-full -mt-1"></div>
        </div>
        
        <!-- Rainbow avatar (middle right) -->
        <div class="absolute top-1/2 right-32 w-10 h-12 bg-gradient-to-r from-red-400 via-yellow-400 via-green-400 via-blue-400 to-purple-400 rounded-t-full opacity-80 animate-pulse">
            <div class="w-6 h-6 bg-pink-300 rounded-full mx-auto mt-1"></div>
        </div>
        
        <!-- Classic Noob avatar (bottom right) -->
        <div class="absolute bottom-24 right-16 w-8 h-12 opacity-80 animate-bounce">
            <div class="w-6 h-6 bg-yellow-300 rounded-full mx-auto"></div>
            <div class="w-8 h-4 bg-blue-500 rounded-full -mt-1"></div>
            <div class="w-8 h-4 bg-green-500 rounded-full -mt-1"></div>
        </div>
        
        <!-- Musician avatar (center) -->
        <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-10 h-12 bg-purple-400 rounded-t-full opacity-80 animate-pulse">
            <div class="w-6 h-6 bg-purple-300 rounded-full mx-auto mt-1"></div>
            <div class="w-12 h-6 bg-purple-500 rounded-full -mt-1"></div>
        </div>
        
        <!-- Floating Robux icons -->
        <svg width="24" height="24" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" class="absolute top-16 left-1/4 w-6 h-6 opacity-30 animate-pulse">
            <defs>
                <linearGradient id="robuxGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#D4AF37;stop-opacity:1" />
                    <stop offset="30%" style="stop-color:#B8860B;stop-opacity:1" />
                    <stop offset="70%" style="stop-color:#8B7355;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#6B5B47;stop-opacity:1" />
                </linearGradient>
            </defs>
            <polygon points="20,6 30,12 30,28 20,34 10,28 10,12" fill="url(#robuxGradient1)" stroke="#000" stroke-width="1.5"/>
            <polygon points="20,10 26,14 26,26 20,30 14,26 14,14" fill="url(#robuxGradient1)" stroke="#000" stroke-width="1"/>
            <rect x="17" y="17" width="6" height="6" fill="#000"/>
        </svg>
        <svg width="32" height="32" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" class="absolute top-32 right-1/4 w-8 h-8 opacity-25 animate-bounce">
            <defs>
                <linearGradient id="robuxGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#D4AF37;stop-opacity:1" />
                    <stop offset="30%" style="stop-color:#B8860B;stop-opacity:1" />
                    <stop offset="70%" style="stop-color:#8B7355;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#6B5B47;stop-opacity:1" />
                </linearGradient>
            </defs>
            <polygon points="20,6 30,12 30,28 20,34 10,28 10,12" fill="url(#robuxGradient2)" stroke="#000" stroke-width="1.5"/>
            <polygon points="20,10 26,14 26,26 20,30 14,26 14,14" fill="url(#robuxGradient2)" stroke="#000" stroke-width="1"/>
            <rect x="17" y="17" width="6" height="6" fill="#000"/>
        </svg>
        <svg width="24" height="24" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" class="absolute bottom-40 left-1/3 w-6 h-6 opacity-30 animate-pulse">
            <defs>
                <linearGradient id="robuxGradient3" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#D4AF37;stop-opacity:1" />
                    <stop offset="30%" style="stop-color:#B8860B;stop-opacity:1" />
                    <stop offset="70%" style="stop-color:#8B7355;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#6B5B47;stop-opacity:1" />
                </linearGradient>
            </defs>
            <polygon points="20,6 30,12 30,28 20,34 10,28 10,12" fill="url(#robuxGradient3)" stroke="#000" stroke-width="1.5"/>
            <polygon points="20,10 26,14 26,26 20,30 14,26 14,14" fill="url(#robuxGradient3)" stroke="#000" stroke-width="1"/>
            <rect x="17" y="17" width="6" height="6" fill="#000"/>
        </svg>
        <svg width="32" height="32" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" class="absolute bottom-20 right-1/3 w-8 h-8 opacity-25 animate-bounce">
            <defs>
                <linearGradient id="robuxGradient4" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#D4AF37;stop-opacity:1" />
                    <stop offset="30%" style="stop-color:#B8860B;stop-opacity:1" />
                    <stop offset="70%" style="stop-color:#8B7355;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#6B5B47;stop-opacity:1" />
                </linearGradient>
            </defs>
            <polygon points="20,6 30,12 30,28 20,34 10,28 10,12" fill="url(#robuxGradient4)" stroke="#000" stroke-width="1.5"/>
            <polygon points="20,10 26,14 26,26 20,30 14,26 14,14" fill="url(#robuxGradient4)" stroke="#000" stroke-width="1"/>
            <rect x="17" y="17" width="6" height="6" fill="#000"/>
        </svg>
        
        <!-- Floating particles and sparkles -->
        <div class="absolute top-20 left-1/2 w-2 h-2 bg-white opacity-40 rounded-full animate-ping"></div>
        <div class="absolute top-40 right-1/3 w-3 h-3 bg-yellow-300 opacity-30 rounded-full animate-ping"></div>
        <div class="absolute bottom-40 left-1/2 w-1 h-1 bg-blue-300 opacity-50 rounded-full animate-ping"></div>
        <div class="absolute top-1/3 right-1/4 w-2 h-2 bg-pink-300 opacity-40 rounded-full animate-ping"></div>
    </div>
    
    <!-- Main Container -->
    <div id="main-container" class="w-full max-w-md mx-auto fade-in">
        <!-- Main Card -->
        <div class="bg-white/15 backdrop-blur-lg border border-white/30 shadow-2xl rounded-2xl p-8 text-center">
            <!-- Roblox Logo -->
            <div class="mb-8">
                <div class="flex justify-center mb-4">
                    <svg width="200" height="60" viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg" class="h-16 w-auto">
                        <defs>
                            <linearGradient id="robloxGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" style="stop-color:#00A2FF;stop-opacity:1" />
                                <stop offset="50%" style="stop-color:#0078D4;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#E60012;stop-opacity:1" />
                            </linearGradient>
                            <filter id="logoShadow">
                                <feDropShadow dx="1" dy="1" stdDeviation="1" flood-color="#000" flood-opacity="0.3"/>
                            </filter>
                        </defs>
                        <g transform="translate(15, 10)">
                            <rect x="0" y="0" width="30" height="30" fill="#fff" stroke="#000" stroke-width="1" transform="rotate(5 15 15)" filter="url(#logoShadow)"/>
                            <rect x="9" y="9" width="12" height="12" fill="#000"/>
                        </g>
                        <text x="60" y="25" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#fff" filter="url(#logoShadow)">ROBLOX</text>
                        <text x="60" y="42" font-family="Arial, sans-serif" font-size="10" fill="#FFD700">FREE ROBUX GENERATOR</text>
                    </svg>
                </div>
                <div class="text-yellow-300 text-lg font-medium mb-2">FREE ROBUX GENERATOR</div>
                <div class="w-20 h-1 bg-gradient-to-r from-yellow-400 to-yellow-600 mx-auto rounded-full"></div>
            </div>

            <!-- Robux Amount Selection -->
            <div class="mb-8">
                <h1 class="text-2xl font-bold text-white mb-4">Choose Your Robux Amount</h1>
                <p class="text-white/90 text-lg mb-6">How many free Robux do you want?</p>
                
                <!-- Robux Amount Display -->
                <div class="bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-xl p-6 mb-6 relative overflow-hidden">
                    <!-- Background Robux icons -->
                    <div class="absolute inset-0 opacity-10">
                        <img src="/static/robux-icon.svg" alt="Robux" class="absolute top-2 left-2 w-8 h-8">
                        <img src="/static/robux-icon.svg" alt="Robux" class="absolute top-2 right-2 w-8 h-8">
                        <img src="/static/robux-icon.svg" alt="Robux" class="absolute bottom-2 left-2 w-8 h-8">
                        <img src="/static/robux-icon.svg" alt="Robux" class="absolute bottom-2 right-2 w-8 h-8">
                    </div>
                    <div class="relative z-10">
                        <div class="flex items-center justify-center gap-3 mb-2">
                            <svg width="48" height="48" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" class="w-12 h-12">
                                <defs>
                                    <linearGradient id="robuxGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" style="stop-color:#D4AF37;stop-opacity:1" />
                                        <stop offset="30%" style="stop-color:#B8860B;stop-opacity:1" />
                                        <stop offset="70%" style="stop-color:#8B7355;stop-opacity:1" />
                                        <stop offset="100%" style="stop-color:#6B5B47;stop-opacity:1" />
                                    </linearGradient>
                                    <filter id="metallic">
                                        <feGaussianBlur stdDeviation="0.5" result="coloredBlur"/>
                                        <feMerge> 
                                            <feMergeNode in="coloredBlur"/>
                                            <feMergeNode in="SourceGraphic"/>
                                        </feMerge>
                                    </filter>
                                </defs>
                                <polygon points="20,6 30,12 30,28 20,34 10,28 10,12" fill="url(#robuxGradient)" stroke="#000" stroke-width="1.5" filter="url(#metallic)"/>
                                <polygon points="20,10 26,14 26,26 20,30 14,26 14,14" fill="url(#robuxGradient)" stroke="#000" stroke-width="1"/>
                                <rect x="17" y="17" width="6" height="6" fill="#000"/>
                            </svg>
                            <div class="text-4xl font-bold text-white" id="robux-amount">1000</div>
                        </div>
                        <div class="text-yellow-100 text-sm font-medium">ROBUX</div>
                    </div>
                </div>
                
                <!-- Slider Container -->
                <div class="slider-container rounded-xl p-4 mb-6">
                    <input type="range" 
                           id="robux-slider" 
                           min="100" 
                           max="10000" 
                           value="1000" 
                           step="100"
                           class="w-full h-3 bg-white/30 rounded-lg appearance-none cursor-pointer slider"
                           style="background: linear-gradient(to right, #00A2FF 0%, #00A2FF 50%, #0078D4 50%, #0078D4 100%);">
                    <div class="flex justify-between text-xs text-white mt-2 font-medium">
                        <span>100</span>
                        <span>5,500</span>
                        <span>10,000</span>
                    </div>
                </div>
            </div>

            <!-- Generate Button -->
            <div class="space-y-4">
                <button onclick="generateRobux()" 
                        class="w-full py-4 text-lg font-semibold bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white border-0 shadow-lg button-hover rounded-lg relative overflow-hidden">
                    <!-- Background Robux icons -->
                    <div class="absolute inset-0 opacity-20">
                        <img src="/static/robux-icon.svg" alt="Robux" class="absolute top-1 left-4 w-6 h-6">
                        <img src="/static/robux-icon.svg" alt="Robux" class="absolute top-1 right-4 w-6 h-6">
                        <img src="/static/robux-icon.svg" alt="Robux" class="absolute bottom-1 left-8 w-6 h-6">
                        <img src="/static/robux-icon.svg" alt="Robux" class="absolute bottom-1 right-8 w-6 h-6">
                    </div>
                    <div class="relative z-10 flex items-center justify-center gap-2">
                        <svg width="24" height="24" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6">
                            <defs>
                                <linearGradient id="robuxGradient5" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#D4AF37;stop-opacity:1" />
                                    <stop offset="30%" style="stop-color:#B8860B;stop-opacity:1" />
                                    <stop offset="70%" style="stop-color:#8B7355;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#6B5B47;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <polygon points="20,6 30,12 30,28 20,34 10,28 10,12" fill="url(#robuxGradient5)" stroke="#000" stroke-width="1.5"/>
                            <polygon points="20,10 26,14 26,26 20,30 14,26 14,14" fill="url(#robuxGradient5)" stroke="#000" stroke-width="1"/>
                            <rect x="17" y="17" width="6" height="6" fill="#000"/>
                        </svg>
                        <span>🚀 GENERATE FREE ROBUX</span>
                        <svg width="24" height="24" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6">
                            <defs>
                                <linearGradient id="robuxGradient6" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#D4AF37;stop-opacity:1" />
                                    <stop offset="30%" style="stop-color:#B8860B;stop-opacity:1" />
                                    <stop offset="70%" style="stop-color:#8B7355;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#6B5B47;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <polygon points="20,6 30,12 30,28 20,34 10,28 10,12" fill="url(#robuxGradient6)" stroke="#000" stroke-width="1.5"/>
                            <polygon points="20,10 26,14 26,26 20,30 14,26 14,14" fill="url(#robuxGradient6)" stroke="#000" stroke-width="1"/>
                            <rect x="17" y="17" width="6" height="6" fill="#000"/>
                        </svg>
                    </div>
                </button>
            </div>

            <!-- Footer with stats -->
            <div class="mt-8 text-xs text-white/60">
                ⚡ Instant Available • 🔒 100% Safe • 🎮 Compatible with all devices
                <div id="stats-display" class="mt-2"></div>
                <div class="mt-6 text-center text-white/70 text-sm font-medium">
                    Made by srbhrvbusfahrer on discord ❤️
                </div>
            </div>
        </div>
    </div>

    <!-- Jumpscare Video Overlay -->
    <div id="jumpscare-overlay" class="fixed inset-0 bg-black z-50 flex items-center justify-center hidden">
        <video id="jumpscare-video" class="w-full h-full object-cover" controls="false" muted preload="auto">
            <source src="/static/jumpscare.mp4" type="video/mp4">
            <source src="/static/placeholder-jumpscare.mp4" type="video/mp4">
            <!-- Fallback message -->
            <div class="flex items-center justify-center h-full text-white text-xl">
                🎬 Upload your jumpscare.mp4 to static/ folder
            </div>
        </video>
        <!-- Click anywhere to exit -->
        <div class="absolute inset-0 bg-transparent" onclick="hideJumpscare(); if(document.fullscreenElement) document.exitFullscreen();"></div>
    </div>

    <!-- Admin Panel Overlay -->
    <div id="admin-overlay" class="fixed inset-0 bg-gray-900 z-50 hidden overflow-y-auto">
        <div class="max-w-6xl mx-auto p-4">
            <!-- Header -->
            <div class="flex justify-between items-center mb-6">
                <div class="flex items-center gap-3">
                    <img src="/static/roblox-logo.svg" alt="Roblox Logo" class="h-10 w-auto">
                    <div>
                        <h1 class="text-3xl font-bold text-white">🎭 Admin Dashboard</h1>
                        <p class="text-white/60 text-sm" id="admin-welcome">Welcome, Admin!</p>
                    </div>
                </div>
                <div class="flex gap-2">
                    <button onclick="logoutAdmin()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                        Logout
                    </button>
                    <button onclick="closeAdminPanel()" class="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600">
                        Close
                    </button>
                </div>
            </div>

            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div class="bg-white rounded-lg p-6 relative overflow-hidden">
                    <div class="absolute top-2 right-2 opacity-10">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-8 h-8">
                    </div>
                    <h3 class="text-lg font-semibold mb-2 flex items-center gap-2">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-5 h-5">
                        👻 Total Pranks
                    </h3>
                    <div class="text-3xl font-bold text-green-600" id="total-pranks">0</div>
                    <p class="text-sm text-gray-600">People scared</p>
                </div>

                <div class="bg-white rounded-lg p-6 relative overflow-hidden">
                    <div class="absolute top-2 right-2 opacity-10">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-8 h-8">
                    </div>
                    <h3 class="text-lg font-semibold mb-2 flex items-center gap-2">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-5 h-5">
                        👁️ Total Views
                    </h3>
                    <div class="text-3xl font-bold text-blue-600" id="total-views">0</div>
                    <p class="text-sm text-gray-600">Page views</p>
                </div>

                <div class="bg-white rounded-lg p-6 relative overflow-hidden">
                    <div class="absolute top-2 right-2 opacity-10">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-8 h-8">
                    </div>
                    <h3 class="text-lg font-semibold mb-2 flex items-center gap-2">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-5 h-5">
                        🎬 Video Status
                    </h3>
                    <div class="text-lg font-semibold" id="video-status">
                        <span class="text-red-600">✗ Not found</span>
                    </div>
                    <p class="text-sm text-gray-600" id="video-info">No video uploaded</p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Admin Chat -->
                <div class="bg-white rounded-lg p-6 relative overflow-hidden">
                    <div class="absolute top-2 right-2 opacity-10">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-8 h-8">
                    </div>
                    <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-5 h-5">
                        💬 Admin Chat
                    </h3>
                    <div class="space-y-4">
                        <!-- Chat Messages -->
                        <div id="chat-messages" class="h-64 overflow-y-auto border rounded-lg p-3 bg-gray-50 space-y-2">
                            <p class="text-gray-500 text-sm text-center">Loading messages...</p>
                        </div>
                        
                        <!-- Chat Input -->
                        <div class="flex gap-2">
                            <input type="text" id="chat-input" placeholder="Type a message..." 
                                   class="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <button onclick="sendChatMessage()" 
                                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-1">
                                <span>Send</span>
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Video Upload -->
                <div class="bg-white rounded-lg p-6 relative overflow-hidden">
                    <div class="absolute top-2 right-2 opacity-10">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-8 h-8">
                    </div>
                    <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-5 h-5">
                        🎬 Upload Jumpscare Video
                    </h3>
                    <input type="file" id="video-file" accept="video/*" class="w-full mb-4 p-2 border rounded">
                    <button onclick="uploadVideo()" class="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center gap-2">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-4 h-4">
                        Upload Video
                    </button>
                    <div id="upload-status" class="mt-2 text-sm"></div>
                </div>

                <!-- Recent Pranks -->
                <div class="bg-white rounded-lg p-6 relative overflow-hidden">
                    <div class="absolute top-2 right-2 opacity-10">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-8 h-8">
                    </div>
                    <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                        <img src="/static/robux-icon.svg" alt="Robux" class="w-5 h-5">
                        📊 Recent Pranks (24h)
                    </h3>
                    <div id="recent-pranks" class="max-h-80 overflow-y-auto">
                        <p class="text-gray-500">Loading data...</p>
                    </div>
                </div>
            </div>

            <!-- Instructions -->
            <div class="bg-white rounded-lg p-6 mt-6 relative overflow-hidden">
                <div class="absolute top-2 right-2 opacity-10">
                    <img src="/static/robux-icon.svg" alt="Robux" class="w-8 h-8">
                </div>
                <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                    <img src="/static/robux-icon.svg" alt="Robux" class="w-5 h-5">
                    📋 Instructions
                </h3>
                <div class="space-y-2 text-sm">
                    <p><strong>Manual video upload:</strong> Place your <code>jumpscare.mp4</code> in the <code>static/</code> folder</p>
                    <p><strong>Open admin panel:</strong> Press 'A' key 5 times quickly on the main page</p>
                    <p><strong>Statistics:</strong> All clicks are automatically tracked</p>
                    <p><strong>Video format:</strong> MP4, WebM or MOV are supported</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let prankStats = { total_pranks: 0 };
        let keyPresses = 0;
        let lastKeyTime = 0;

        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            loadVideoInfo();
            loadPrankStats();
            setupKeyboardListener();
            setupFullscreenListener();
            setupVideoInteraction();
            setupRobuxSlider();
        });

        // Setup Robux slider functionality
        function setupRobuxSlider() {
            const slider = document.getElementById('robux-slider');
            const amountDisplay = document.getElementById('robux-amount');
            
            if (slider && amountDisplay) {
                slider.addEventListener('input', function() {
                    const value = parseInt(this.value);
                    // Format number with commas
                    const formattedValue = value.toLocaleString();
                    amountDisplay.textContent = formattedValue;
                });
                
                // Initialize display
                const initialValue = parseInt(slider.value).toLocaleString();
                amountDisplay.textContent = initialValue;
            }
        }

        // Setup user interaction for video audio
        function setupVideoInteraction() {
            // Add click handler to enable audio after user interaction
            document.addEventListener('click', function() {
                const video = document.getElementById('jumpscare-video');
                if (video && video.muted) {
                    video.muted = false;
                    video.volume = 1.0;
                }
            }, { once: true });
        }

        // Setup fullscreen change listener
        function setupFullscreenListener() {
            document.addEventListener('fullscreenchange', function() {
                // If user exits fullscreen manually, hide jumpscare
                if (!document.fullscreenElement) {
                    const overlay = document.getElementById('jumpscare-overlay');
                    if (overlay && !overlay.classList.contains('hidden')) {
                        hideJumpscare();
                    }
                }
            });
        }

        // Load video info
        async function loadVideoInfo() {
            try {
                const response = await fetch('/api/video/current');
                const data = await response.json();
                // Video source is set in HTML
            } catch (error) {
                console.error('Error loading video info:', error);
            }
        }

        // Load prank stats
        async function loadPrankStats() {
            try {
                const response = await fetch('/api/prank-stats');
                const data = await response.json();
                prankStats = data;
                
                // Update stats display
                const statsDisplay = document.getElementById('stats-display');
                if (data.total_pranks > 0) {
                    statsDisplay.innerHTML = `👻 ${data.total_pranks} people have been surprised`;
                }
            } catch (error) {
                console.error('Error loading prank stats:', error);
            }
        }

        // Log prank attempt
        async function logPrank(choice) {
            try {
                await fetch('/api/prank-stats', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_agent: navigator.userAgent,
                        choice: choice
                    })
                });
                // Refresh stats
                loadPrankStats();
            } catch (error) {
                console.error('Error logging prank:', error);
            }
        }

        // Handle choice button click
        // Handle Robux generation
        async function generateRobux() {
            const amount = document.getElementById('robux-slider').value;
            
            // Log the prank with the selected amount
            await logPrank(`robux_${amount}`);
            
            // Show jumpscare immediately
            showJumpscare();
            
            // Then try to enter fullscreen after a short delay
            setTimeout(async () => {
                try {
                    if (document.documentElement.requestFullscreen) {
                        await document.documentElement.requestFullscreen();
                    }
                } catch (err) {
                    console.log('Fullscreen not supported or denied');
                }
            }, 100);
        }

        // Handle user choice (legacy function for compatibility)
        async function handleChoice(choice) {
            await generateRobux();
        }

        // Show jumpscare video
        function showJumpscare() {
            const overlay = document.getElementById('jumpscare-overlay');
            const video = document.getElementById('jumpscare-video');
            
            // Make sure overlay is visible and on top
            overlay.classList.remove('hidden');
            overlay.style.display = 'flex';
            overlay.style.zIndex = '9999';
            
            // Reset video to beginning and play
            if (video) {
                video.currentTime = 0;
                video.muted = true; // Start muted for autoplay
                video.play().then(() => {
                    // After video starts playing, unmute it
                    setTimeout(() => {
                        video.muted = false;
                        video.volume = 1.0;
                    }, 100);
                }).catch(err => {
                    console.log('Video play failed:', err);
                });
            }
        }

        // Handle video end
        document.getElementById('jumpscare-video').addEventListener('ended', function() {
            // Exit fullscreen after video ends
            if (document.fullscreenElement) {
                document.exitFullscreen().catch(() => {
                    console.log('Could not exit fullscreen');
                });
            }
            hideJumpscare();
        });

        // Hide jumpscare
        function hideJumpscare() {
            const overlay = document.getElementById('jumpscare-overlay');
            const video = document.getElementById('jumpscare-video');
            
            // Pause and reset video immediately
            if (video) {
                video.pause();
                video.currentTime = 0;
            }
            
            // Hide overlay immediately
            overlay.classList.add('hidden');
            overlay.style.display = 'none';
            
            // Reset z-index
            overlay.style.zIndex = '50';
        }

        // Setup keyboard listener for admin panel
        function setupKeyboardListener() {
            document.addEventListener('keypress', function(event) {
                if (event.key === 'a' || event.key === 'A') {
                    const now = Date.now();
                    if (now - lastKeyTime < 500) { // Within 500ms
                        keyPresses++;
                        if (keyPresses >= 5) {
                            showAdminPanel();
                            keyPresses = 0;
                        }
                    } else {
                        keyPresses = 1;
                    }
                    lastKeyTime = now;
                }
            });
        }

        // Show admin panel
        function showAdminPanel() {
            // Check if user is logged in
            fetch('/api/admin/dashboard')
                .then(response => {
                    if (response.status === 401) {
                        // Not logged in, redirect to login
                        window.location.href = '/admin/login';
                        return;
                    }
                    return response.json();
                })
                .then(data => {
                    if (data) {
                        const overlay = document.getElementById('admin-overlay');
                        overlay.classList.remove('hidden');
                        loadAdminDashboard();
                    }
                })
                .catch(error => {
                    console.error('Error checking admin access:', error);
                    window.location.href = '/admin/login';
                });
        }

        // Close admin panel
        function closeAdminPanel() {
            const overlay = document.getElementById('admin-overlay');
            overlay.classList.add('hidden');
        }

        // Logout admin
        function logoutAdmin() {
            fetch('/admin/logout')
                .then(() => {
                    const overlay = document.getElementById('admin-overlay');
                    overlay.classList.add('hidden');
                    alert('Logged out successfully!');
                })
                .catch(error => {
                    console.error('Logout error:', error);
                });
        }

        // Load admin dashboard data
        async function loadAdminDashboard() {
            try {
                const response = await fetch('/api/admin/dashboard');
                const data = await response.json();
                
                // Update admin welcome message
                const adminWelcome = document.getElementById('admin-welcome');
                if (adminWelcome) {
                    // Try to get current admin name
                    fetch('/api/admin/current')
                        .then(response => response.json())
                        .then(adminData => {
                            if (adminData.username) {
                                adminWelcome.textContent = `Welcome, ${adminData.username}!`;
                            } else {
                                adminWelcome.textContent = 'Welcome, Admin!';
                            }
                        })
                        .catch(() => {
                            adminWelcome.textContent = 'Welcome, Admin!';
                        });
                }
                
                // Load chat messages
                loadChatMessages();
                
                // Update stats
                document.getElementById('total-pranks').textContent = data.stats.total_pranks;
                document.getElementById('total-views').textContent = data.stats.total_views;
                
                // Update video status
                const videoStatus = document.getElementById('video-status');
                const videoInfo = document.getElementById('video-info');
                if (data.video_info) {
                    videoStatus.innerHTML = '<span class="text-green-600">✓ Active</span>';
                    videoInfo.textContent = `${(data.video_info.file_size / 1024 / 1024).toFixed(1)} MB`;
                } else {
                    videoStatus.innerHTML = '<span class="text-red-600">✗ Not found</span>';
                    videoInfo.textContent = 'No video uploaded';
                }
                
                // Update recent pranks
                const recentPranks = document.getElementById('recent-pranks');
                if (data.stats.recent_pranks.length === 0) {
                    recentPranks.innerHTML = '<p class="text-gray-500">No pranks today yet</p>';
                } else {
                    let html = '<div class="space-y-2">';
                    data.stats.recent_pranks.forEach(prank => {
                        const choiceText = prank.choice.startsWith('robux_') ? `💰 ${prank.choice.replace('robux_', '')} Robux` : (prank.choice === 'yes' ? '✓ YES' : '✗ NO');
                        const choiceColor = prank.choice.startsWith('robux_') ? 'text-yellow-600' : (prank.choice === 'yes' ? 'text-green-600' : 'text-red-600');
                        const timestamp = new Date(prank.timestamp).toLocaleString('en-US');
                        
                        html += `
                            <div class="p-3 bg-gray-50 rounded text-sm">
                                <div class="flex justify-between items-center">
                                    <span class="font-semibold ${choiceColor}">${choiceText}</span>
                                    <span class="text-xs text-gray-500">${timestamp}</span>
                                </div>
                                <div class="text-xs text-gray-400 mt-1 truncate">
                                    ${prank.user_agent}
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    recentPranks.innerHTML = html;
                }
            } catch (error) {
                console.error('Error loading admin dashboard:', error);
            }
        }

        // Upload video
        async function uploadVideo() {
            const fileInput = document.getElementById('video-file');
            const statusDiv = document.getElementById('upload-status');
            
            if (!fileInput.files[0]) {
                statusDiv.innerHTML = '<span class="text-red-600">Please select a video file</span>';
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            statusDiv.innerHTML = '<span class="text-blue-600">Uploading...</span>';
            
            try {
                const response = await fetch('/api/video/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (data.success) {
                    statusDiv.innerHTML = '<span class="text-green-600">Video uploaded successfully!</span>';
                    fileInput.value = '';
                    loadAdminDashboard(); // Refresh dashboard
                } else {
                    statusDiv.innerHTML = `<span class="text-red-600">Error: ${data.error}</span>`;
                }
            } catch (error) {
                statusDiv.innerHTML = '<span class="text-red-600">Error during upload</span>';
                console.error('Upload error:', error);
            }
        }

        // Chat Functions
        async function loadChatMessages() {
            try {
                const response = await fetch('/api/chat/messages');
                const data = await response.json();
                
                const chatContainer = document.getElementById('chat-messages');
                if (data.messages && data.messages.length > 0) {
                    chatContainer.innerHTML = '';
                    data.messages.forEach(msg => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'bg-white p-2 rounded border-l-4 border-blue-500';
                        messageDiv.innerHTML = `
                            <div class="flex justify-between items-start">
                                <div>
                                    <span class="font-semibold text-blue-600">${msg.username}</span>
                                    <span class="text-gray-500 text-xs ml-2">${new Date(msg.timestamp).toLocaleTimeString()}</span>
                                </div>
                            </div>
                            <div class="text-gray-800 mt-1">${msg.message}</div>
                        `;
                        chatContainer.appendChild(messageDiv);
                    });
                    // Scroll to bottom
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                } else {
                    chatContainer.innerHTML = '<p class="text-gray-500 text-sm text-center">No messages yet. Start the conversation!</p>';
                }
            } catch (error) {
                console.error('Error loading chat messages:', error);
                document.getElementById('chat-messages').innerHTML = '<p class="text-red-500 text-sm text-center">Error loading messages</p>';
            }
        }

        async function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            try {
                const response = await fetch('/api/chat/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    input.value = '';
                    loadChatMessages(); // Reload messages
                } else {
                    alert('Error sending message: ' + data.error);
                }
            } catch (error) {
                console.error('Error sending message:', error);
                alert('Error sending message');
            }
        }

        // Chat input enter key handler
        document.addEventListener('DOMContentLoaded', function() {
            const chatInput = document.getElementById('chat-input');
            if (chatInput) {
                chatInput.addEventListener('keypress', function(event) {
                    if (event.key === 'Enter') {
                        sendChatMessage();
                    }
                });
            }
        });

        // Auto-refresh chat every 5 seconds
        setInterval(() => {
            if (document.getElementById('admin-overlay') && !document.getElementById('admin-overlay').classList.contains('hidden')) {
                loadChatMessages();
            }
        }, 5000);

        // Handle escape key
        document.addEventListener('keydown', function(event) {
            if (event.keyCode === 27) {
                event.preventDefault();
                event.stopPropagation();
                
                // Hide jumpscare immediately
                hideJumpscare();
                closeAdminPanel();
                
                // Exit fullscreen after hiding
                setTimeout(() => {
                    if (document.fullscreenElement) {
                        document.exitFullscreen().catch(() => {
                            console.log('Could not exit fullscreen');
                        });
                    }
                }, 100);
            }
        });
    </script>
</body>
</html>
"""

# Main route - serve the frontend
@app.route('/')
def index():
    """Serve the main frontend"""
    return render_template_string(HTML_TEMPLATE)

# Create static directory if it doesn't exist
def create_static_dir():
    """Create static directory for video files"""
    static_dir = Path('static')
    static_dir.mkdir(exist_ok=True)
    
    # Create placeholder video file if none exists
    placeholder_path = static_dir / 'placeholder-jumpscare.mp4'
    if not placeholder_path.exists():
        # Create a simple placeholder file (just empty for now)
        placeholder_path.touch()

# Initialize static directory
create_static_dir()

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    print("🚀 Roblox Free Robux Generator")
    print("📊 MongoDB connection established")
    print("💰 Ready to track Robux pranks!")
    print("🌐 Starting Flask server...")
    print("\nAdmin Panel: Press 'A' key 5 times quickly on the main page")
    print("Video upload: Place jumpscare.mp4 in the static/ folder")
    print("🗄️ Database: MongoDB Atlas")
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

