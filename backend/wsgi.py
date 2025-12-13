"""
WSGI entry point for VediSpeak application
"""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables from parent directory
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path, override=True)

# Debug: Print if .env was loaded
if os.path.exists(env_path):
    print(f"✓ Loaded .env from: {env_path}")
else:
    print(f"⚠ .env not found at: {env_path}")

from app import create_app

# Create Flask app
app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting VediSpeak on http://0.0.0.0:{port}")
    print(f"📊 Debug mode: {debug}")
    app.run(debug=debug, host="0.0.0.0", port=port)
