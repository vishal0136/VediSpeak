#!/usr/bin/env python3
"""
VediSpeak - Application Entry Point
Run with: python run.py
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def create_application():
    """Create Flask app using the organized backend structure"""
    try:
        from app import create_app
        return create_app()
    except ImportError as e:
        print(f"Error importing backend app: {e}")
        raise

def check_ml_system():
    """Quick ML system check on startup"""
    print("🧠 Checking ML system...")
    try:
        # Quick dependency check
        import torch
        import cv2
        print(f"  ✅ PyTorch {torch.__version__} available")
        print(f"  ✅ OpenCV {cv2.__version__} available")
        
        # Check if model files exist
        if os.path.exists("checkpoints/best.pth"):
            print("  ✅ Model checkpoint found")
        else:
            print("  ⚠️  Model checkpoint not found - ISL recognition may not work")
        
        return True
    except ImportError as e:
        print(f"  ❌ ML dependencies missing: {e}")
        print("  ⚠️  ISL recognition will not be available")
        return False

def main():
    """Main application entry point"""
    flask_app = create_application()
    
    # Create necessary directories
    os.makedirs(flask_app.config.get("UPLOAD_FOLDER", "storage/uploads"), exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Quick ML system check
    check_ml_system()
    
    # Run the application
    try:
        from app.extensions import socketio
        print("Starting VediSpeak with SocketIO support...")
        print("URL: http://localhost:5000")
        socketio.run(flask_app, debug=True, host="0.0.0.0", port=5000)
    except ImportError:
        print("SocketIO not available, running with regular Flask...")
        print("URL: http://localhost:5000")
        flask_app.run(debug=True, host="0.0.0.0", port=5000)

# Export for WSGI servers (gunicorn run:application)
application = None

if __name__ == "__main__":
    main()
else:
    application = create_application()