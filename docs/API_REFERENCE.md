# 🔌 VediSpeak API Reference

## Overview

VediSpeak provides a comprehensive RESTful API for Indian Sign Language recognition, multilingual speech processing, and real-time translation services.

**Base URL**: `http://localhost:5000` (development)

**Authentication**: Session-based authentication required for most endpoints

---

## 🔐 Authentication Endpoints

### POST /login
Authenticate user and create session.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

### POST /register
Register new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "confirm_password": "string"
}
```

### POST /logout
End user session.

**Response:**
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

## 🗣️ Speech Processing Endpoints

### POST /text_to_speech
Convert text to speech with enhanced controls.

**Request Body:**
```json
{
  "text": "Hello, this is a test message",
  "lang": "hi",
  "speech_rate": "1.2",
  "pitch": "1.0",
  "audio_format": "mp3",
  "auto_translate": true
}
```

**Parameters:**
- `text` (required): Text to convert to speech
- `lang` (optional): Language code (en, hi, hinglish, bn, ta, te, gu, kn, ml, mr, pa, ur)
- `speech_rate` (optional): Speed multiplier (0.5-2.0)
- `pitch` (optional): Pitch multiplier (0.5-2.0)
- `audio_format` (optional): Output format (mp3, wav, ogg)
- `auto_translate` (optional): Enable automatic translation

**Response:**
```json
{
  "status": "success",
  "audio_data": "data:audio/mp3;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
  "format": "mp3",
  "duration": 3.2,
  "provider": "Azure TTS",
  "quality": "Premium",
  "translation": {
    "translation_needed": true,
    "source_language": "en",
    "target_language": "hi",
    "confidence": 0.95
  }
}
```

### POST /speech_to_text
Convert speech to text with multilingual support.

**Request Body:**
```json
{
  "audio_data": "data:audio/mp3;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
  "lang": "bn"
}
```

**Parameters:**
- `audio_data` (required): Base64 encoded audio data
- `lang` (optional): Expected language code (auto, en, hi, bn, ta, te, gu, kn, ml, mr, pa, ur, or, as)

**Response:**
```json
{
  "status": "success",
  "text": "আমি বাংলায় কথা বলছি",
  "method": "azure",
  "confidence": 0.92,
  "language_detected": "bn-IN"
}
```

### POST /translate
Translate text between Indian languages.

**Request Body:**
```json
{
  "text": "Hello, how are you?",
  "from_lang": "en",
  "to_lang": "hi"
}
```

**Parameters:**
- `text` (required): Text to translate
- `from_lang` (optional): Source language code (auto for auto-detection)
- `to_lang` (required): Target language code

**Response:**
```json
{
  "status": "success",
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "en",
  "target_language": "hi",
  "translation_method": "google_translate",
  "confidence": 0.95
}
```

---

## 📊 Capability Endpoints

### GET /tts_capabilities
Get available TTS providers and supported languages.

**Response:**
```json
{
  "status": "success",
  "capabilities": {
    "providers": {
      "azure": {
        "name": "Azure Cognitive Services",
        "available": true,
        "quality": "Premium"
      },
      "gtts": {
        "name": "Google Text-to-Speech",
        "available": true,
        "quality": "Standard"
      }
    },
    "recommended_provider": "azure",
    "languages": {
      "en": "English",
      "hi": "Hindi (हिंदी)",
      "hinglish": "Hinglish",
      "bn": "Bengali (বাংলা)"
    }
  }
}
```

### GET /stt_capabilities
Get available STT engines and supported languages.

**Response:**
```json
{
  "status": "success",
  "capabilities": {
    "azure_available": true,
    "google_available": true,
    "supported_languages": [
      {
        "code": "bn",
        "name": "Bengali (বাংলা)",
        "azure": true,
        "google": true
      },
      {
        "code": "hi",
        "name": "Hindi (हिंदी)",
        "azure": true,
        "google": true
      }
    ],
    "max_file_size_mb": 25,
    "supported_formats": ["mp3", "wav", "m4a", "ogg", "flac"]
  }
}
```

---

## 🤖 ISL Recognition Endpoints

### POST /api/recognize
Process ISL gesture recognition.

**Request Body:**
```json
{
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "session_id": "unique_session_id"
}
```

**Response:**
```json
{
  "status": "success",
  "prediction": {
    "letter": "A",
    "confidence": 0.94,
    "alternatives": [
      {"letter": "S", "confidence": 0.03},
      {"letter": "T", "confidence": 0.02}
    ]
  },
  "processing_time": 42
}
```

---

## 👤 User Management Endpoints

### GET /api/profile
Get current user profile information.

**Response:**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-12-13T14:22:00Z"
  }
}
```

### GET /api/progress
Get user learning progress and statistics.

**Response:**
```json
{
  "status": "success",
  "progress": {
    "total_modules": 12,
    "completed_modules": 6,
    "overall_progress": 50.0,
    "time_spent_minutes": 180,
    "streak_days": 7,
    "achievements": [
      {
        "id": "first_sign",
        "name": "First Sign",
        "description": "Recognized your first ISL sign",
        "earned_at": "2024-12-01T09:15:00Z"
      }
    ]
  }
}
```

---

## 📈 Analytics Endpoints

### GET /api/stats/recognition
Get ISL recognition statistics.

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_recognitions": 1250,
    "accuracy_rate": 0.952,
    "most_recognized_signs": ["A", "B", "C", "Hello", "Thank you"],
    "daily_activity": [
      {"date": "2024-12-13", "recognitions": 45},
      {"date": "2024-12-12", "recognitions": 38}
    ]
  }
}
```

---

## 🚨 Error Responses

All endpoints return consistent error responses:

```json
{
  "status": "error",
  "message": "Descriptive error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "details": {
    "field": "Additional error details if applicable"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `AUTH_REQUIRED` | Authentication required |
| `INVALID_INPUT` | Invalid request parameters |
| `FILE_TOO_LARGE` | Uploaded file exceeds size limit |
| `UNSUPPORTED_FORMAT` | File format not supported |
| `SERVICE_UNAVAILABLE` | External service temporarily unavailable |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

---

## 📝 Rate Limiting

API endpoints are rate-limited to ensure fair usage:

- **Authentication**: 10 requests per minute
- **Speech Processing**: 60 requests per hour
- **ISL Recognition**: 100 requests per hour
- **General API**: 1000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

---

## 🔧 SDK and Libraries

### JavaScript SDK
```javascript
// Initialize VediSpeak client
const vedispeak = new VediSpeakClient({
  baseURL: 'http://localhost:5000',
  apiKey: 'your-api-key'
});

// Convert text to speech
const audio = await vedispeak.textToSpeech({
  text: 'Hello world',
  lang: 'hi',
  speed: 1.2
});

// Recognize speech
const result = await vedispeak.speechToText({
  audioData: base64Audio,
  lang: 'bn'
});
```

### Python SDK
```python
from vedispeak import VediSpeakClient

# Initialize client
client = VediSpeakClient(
    base_url='http://localhost:5000',
    api_key='your-api-key'
)

# Convert text to speech
audio_data = client.text_to_speech(
    text='Hello world',
    lang='hi',
    speed=1.2
)

# Recognize speech
result = client.speech_to_text(
    audio_data=audio_bytes,
    lang='bn'
)
```


*Last Updated: December 18, 2025*

*VediSpeak API Team*
