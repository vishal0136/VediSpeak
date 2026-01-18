# VediSpeak Setup and Installation Guide

This comprehensive guide will help you set up VediSpeak on your local development environment or production server. Follow these step-by-step instructions to get the platform running quickly and efficiently.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [Advanced Configuration](#advanced-configuration)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Development Setup](#development-setup)
- [Next Steps](#next-steps)

---

## Prerequisites

### System Requirements

**Minimum Requirements**
- **Operating System**: Windows 10, macOS 10.14, or Ubuntu 18.04+
- **Python**: Version 3.8 or higher (Python 3.9-3.10 recommended)
- **Memory**: 4 GB RAM minimum
- **Storage**: 2 GB free disk space
- **Internet**: Stable connection for cloud services

**Recommended Requirements**
- **Operating System**: Windows 11, macOS 12+, or Ubuntu 20.04+
- **Python**: Version 3.9 or 3.10 for optimal compatibility
- **Memory**: 8 GB RAM for better performance
- **Storage**: 5 GB free disk space for models and data
- **Internet**: High-speed connection (25+ Mbps) for optimal experience

### Required Software

**Essential Tools**
- **Git**: Version control system for cloning the repository
- **Python Package Manager**: pip (usually included with Python)
- **Webcam**: For ISL recognition features (720p minimum, 1080p recommended)
- **Modern Web Browser**: Chrome (recommended), Firefox, Safari, or Edge

**Optional Tools**
- **Node.js 16+**: For frontend development and build tools
- **Docker**: For containerized deployment (optional)
- **PostgreSQL**: For production database (SQLite used by default)

---

## Quick Start Guide

### 1. Clone the Repository

```bash
git clone https://github.com/vishal0136/VediSpeak.git
cd vedispeak
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv_new

# Activate virtual environment
# On Windows:
venv_new\Scripts\activate
# On macOS/Linux:
source venv_new/bin/activate
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install additional ML dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///vedispeak.db

# Azure Speech Services Configuration (Recommended for enhanced features)
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=eastus

# Twilio SMS Configuration (Optional - for OTP via SMS)
TWILIO_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE=your-twilio-phone

# SendGrid Email Configuration (Optional - for OTP via Email)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=your-verified-email

# Database Configuration
MYSQL_HOST=127.0.0.1
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=isl_app
```

### 5. Initialize Database

```bash
# Initialize the database
python -c "from backend.app import create_app; app = create_app(); app.app_context().push(); from backend.app.models import db; db.create_all()"
```

### 6. Download ML Models

```bash
# Run the model download script
python download_models.py
```

**Note**: The download script is currently a placeholder. It will:
- Create the `checkpoints/` directory if it doesn't exist
- Display instructions for manually placing model files
- Check if required model files (`best.pth`, `last.pth`) already exist

**Required Model Files:**
- `checkpoints/best.pth` - Main ISL recognition model
- `checkpoints/last.pth` - Latest training checkpoint

**Manual Setup (if download script fails):**
1. Ensure the `checkpoints/` directory exists
2. Place your trained model files in the directory
3. Verify files are named correctly (`best.pth`, `last.pth`)

### 7. Run the Application

```bash
# Start the Flask development server
python run.py
```

The application will be available at `http://localhost:5000`

## Advanced Setup

### Azure Speech Services Integration

For enhanced multilingual STT and TTS capabilities:

1. **Create Azure Cognitive Services Account**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a new "Speech" resource
   - Note down the key and region

2. **Configure Environment Variables**
   ```env
   AZURE_SPEECH_KEY=your_azure_speech_key_here
   AZURE_SPEECH_REGION=eastus
   ```

3. **Install Azure Speech SDK**
   ```bash
   pip install azure-cognitiveservices-speech==1.34.0
   ```

4. **Restart the application** to enable enhanced features:
   - Bengali, Tamil, Telugu STT support
   - Higher accuracy speech recognition
   - Better voice synthesis quality

### Production Deployment

For production deployment:

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker Setup (Optional)

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**2. Camera Access Issues**
- Ensure webcam permissions are granted
- Check if other applications are using the camera
- Try different browsers (Chrome recommended)

**3. Model Loading Errors**
- Run `python download_models.py` to check model setup status
- Verify model files (`best.pth`, `last.pth`) are in the `checkpoints/` directory
- Check file permissions and ensure files aren't corrupted
- Ensure sufficient disk space (models require ~50MB total)

**4. Port Already in Use**
```bash
# Kill process using port 5000
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

### Performance Optimization

- **CPU Usage**: Reduce video resolution for better performance
- **Memory**: Close unnecessary applications
- **Network**: Ensure stable internet for translation features

## Development Setup

### Code Structure
```
vedispeak/
├── backend/           # Flask backend
├── frontend/          # HTML templates & static files
├── checkpoints/       # ML model files
├── data/             # Training data
├── docs/             # Documentation
└── requirements.txt  # Python dependencies
```

### Development Commands

```bash
# Run in development mode
export FLASK_ENV=development
python run.py

# Run tests (if available)
python -m pytest tests/

# Format code
black backend/ frontend/
```

## New Features & Enhancements

### Recent Updates (December 2024)

**Enhanced Speech Technologies:**
- 🎯 **Multilingual STT**: Support for Bengali, Tamil, Telugu, and 10+ Indian languages
- 🔄 **Real-time Translation**: Translate between Indian languages instantly
- 🎚️ **Live Audio Controls**: Real-time speed and pitch adjustment
- ⚡ **Dual Engine Architecture**: Azure + Google for maximum reliability

**Improved User Experience:**
- ✨ **Professional Notifications**: Beautiful animated maintenance messages
- 🎨 **Simplified Interface**: Cleaner TTS controls without voice type selection
- 📱 **Better Mobile Support**: Enhanced responsive design
- 🎯 **Smart Interactions**: Interactive module cards and notifications

## Next Steps

After successful installation:

1. 📚 **Explore Learning Modules**: Visit `/learn` (currently being enhanced with AI features)
2. 🎥 **Try ISL Recognition**: Go to `/isl-recognition` to test hand gesture recognition
3. 🔊 **Test Enhanced Voice Tools**: Check out `/stt-tool` and `/tts-tool` for new features
4. 🌐 **Try Translation**: Test real-time translation between Indian languages
5. 📊 **View Dashboard**: Monitor your progress and access all features

## Support

If you encounter issues:

1. Check this documentation
2. Review the [Technical Specifications](./TECHNICAL_SPECS.md)
3. Create an issue on GitHub
4. Contact the development team

---

**Happy Learning! 🎉**


*VediSpeak - Empowering Communication Through Technology*
