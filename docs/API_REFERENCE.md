# VediSpeak API Reference

## Overview

The VediSpeak API provides a comprehensive RESTful interface for Indian Sign Language recognition, multilingual speech processing, and real-time translation services. This API enables developers to integrate ISL recognition, speech-to-text, text-to-speech, and translation capabilities into their applications.

**Base URL**: `http://localhost:5000` (development)  
**Production URL**: `https://api.vedispeak.com` (when available)

**Authentication**: Session-based authentication required for most endpoints  
**API Version**: v2.1.0  
**Content Type**: `application/json`

---

## Authentication Endpoints

### User Login
**Endpoint**: `POST /login`  
**Description**: Authenticate user credentials and create a new session

**Request Headers**:
```http
Content-Type: application/json
```

**Request Body**:
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Success Response** (200 OK):
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-12-13T14:22:00Z"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded

### User Registration
**Endpoint**: `POST /register`  
**Description**: Create a new user account with email verification

**Request Body**:
```json
{
  "username": "string (required, 3-80 characters)",
  "email": "string (required, valid email format)",
  "password": "string (required, minimum 8 characters)",
  "confirm_password": "string (required, must match password)"
}
```

**Success Response** (201 Created):
```json
{
  "status": "success",
  "message": "Account created successfully",
  "user": {
    "id": 2,
    "username": "new_user",
    "email": "newuser@example.com"
  }
}
```

### User Logout
**Endpoint**: `POST /logout`  
**Description**: End current user session and clear authentication

**Success Response** (200 OK):
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

## Speech Processing Endpoints

### Text-to-Speech Conversion
**Endpoint**: `POST /text_to_speech`  
**Description**: Convert text to high-quality speech with advanced controls and multilingual support

**Request Headers**:
```http
Content-Type: application/json
Authorization: Bearer <session_token>
```

**Request Body**:
```json
{
  "text": "Hello, this is a test message (required)",
  "lang": "hi (optional, default: 'en')",
  "speech_rate": "1.2 (optional, range: 0.5-2.0)",
  "pitch": "1.0 (optional, range: 0.5-2.0)",
  "audio_format": "mp3 (optional, options: mp3, wav, ogg)",
  "auto_translate": true
}
```

**Supported Languages**:
- `en` - English
- `hi` - Hindi (हिंदी)
- `hinglish` - Hinglish
- `bn` - Bengali (বাংলা)
- `ta` - Tamil (தமிழ்)
- `te` - Telugu (తెలుగు)
- `gu` - Gujarati (ગુજરાતી)
- `kn` - Kannada (ಕನ್ನಡ)
- `ml` - Malayalam (മലയാളം)
- `mr` - Marathi (मराठी)
- `pa` - Punjabi (ਪੰਜਾਬੀ)
- `ur` - Urdu (اردو)

**Success Response** (200 OK):
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

### Speech-to-Text Conversion
**Endpoint**: `POST /speech_to_text`  
**Description**: Convert speech audio to text with multilingual support and dual-engine architecture

**Request Body**:
```json
{
  "audio_data": "data:audio/mp3;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA... (required)",
  "lang": "bn (optional, default: 'auto' for auto-detection)"
}
```

**Supported Languages**:
- `auto` - Automatic language detection
- `en` - English
- `hi` - Hindi (हिंदी)
- `bn` - Bengali (বাংলা)
- `ta` - Tamil (தமிழ்)
- `te` - Telugu (తెలుగు)
- `gu` - Gujarati (ગુજરાતી)
- `kn` - Kannada (ಕನ್ನಡ)
- `ml` - Malayalam (മലയാളം)
- `mr` - Marathi (मराठी)
- `pa` - Punjabi (ਪੰਜਾਬੀ)
- `ur` - Urdu (اردو)
- `or` - Odia (ଓଡ଼ିଆ)
- `as` - Assamese (অসমীয়া)

**Success Response** (200 OK):
```json
{
  "status": "success",
  "text": "আমি বাংলায় কথা বলছি",
  "method": "azure",
  "confidence": 0.92,
  "language_detected": "bn-IN",
  "processing_time_ms": 1250
}
```

### Real-Time Translation
**Endpoint**: `POST /translate`  
**Description**: Translate text between Indian languages with confidence scoring

**Request Body**:
```json
{
  "text": "Hello, how are you? (required)",
  "from_lang": "en (optional, default: 'auto')",
  "to_lang": "hi (required)"
}
```

**Success Response** (200 OK):
```json
{
  "status": "success",
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "en",
  "target_language": "hi",
  "translation_method": "google_translate",
  "confidence": 0.95,
  "processing_time_ms": 450
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
