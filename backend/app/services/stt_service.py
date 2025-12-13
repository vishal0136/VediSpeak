"""
Enhanced Speech-to-Text service with Azure Speech Services and Google fallback
Supports multilingual recognition including Bengali and other Indian languages
"""
import os
import base64
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
from flask import current_app

# Import Azure Speech Services
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_STT_AVAILABLE = True
except ImportError:
    AZURE_STT_AVAILABLE = False
    print("Warning: Azure Speech SDK not available. Install with: pip install azure-cognitiveservices-speech")

def speech_to_text_service(audio_data, lang='en'):
    """
    Enhanced speech-to-text with Azure Speech Services and Google fallback
    Supports multilingual recognition including Bengali and other Indian languages
    
    Args:
        audio_data: Base64 encoded audio data
        lang: Language code ('hi', 'bn', 'ta', 'te', 'en', etc.)
    
    Returns:
        dict: {"status": "success", "text": "transcribed text", "method": "azure/google", "confidence": float}
    """
    temp_mp3 = None
    temp_wav = None
    
    try:
        if not audio_data:
            return {"status": "error", "message": "No audio data received"}
        
        # Decode base64 audio
        if "," in audio_data:
            _, b64 = audio_data.split(",", 1)
        else:
            b64 = audio_data
        
        audio_bytes = base64.b64decode(b64)
        
        # Check size limit (25 MB for better quality)
        if len(audio_bytes) > (25 * 1024 * 1024):
            return {"status": "error", "message": "Audio file too large (max 25MB)"}
        
        # Write to temporary MP3 file
        tmp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_mp3.write(audio_bytes)
        tmp_mp3.flush()
        tmp_mp3.close()
        temp_mp3 = tmp_mp3.name
        
        # Convert to WAV using pydub (16kHz mono for better recognition)
        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_wav.close()
        temp_wav = tmp_wav.name
        
        sound = AudioSegment.from_file(temp_mp3).set_channels(1).set_frame_rate(16000)
        sound.export(temp_wav, format="wav")
        
        # Try Azure Speech Services first (better multilingual support)
        azure_result = try_azure_stt(temp_wav, lang)
        if azure_result["status"] == "success":
            return azure_result
        
        # Fallback to Google Speech Recognition
        current_app.logger.info("Azure STT failed, falling back to Google Speech Recognition")
        google_result = try_google_stt(temp_wav, lang)
        return google_result
    
    except Exception as e:
        current_app.logger.error(f"STT error: {e}")
        return {"status": "error", "message": "Speech recognition failed"}
    
    finally:
        # Cleanup temporary files
        for temp_file in [temp_mp3, temp_wav]:
            if temp_file:
                try:
                    os.remove(temp_file)
                except Exception:
                    pass


def try_azure_stt(wav_file_path, lang='en'):
    """
    Try Azure Speech-to-Text recognition with multilingual support
    """
    try:
        if not AZURE_STT_AVAILABLE:
            return {"status": "error", "message": "Azure Speech SDK not available"}
        
        # Get Azure credentials
        speech_key = os.getenv('AZURE_SPEECH_KEY')
        speech_region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
        
        if not speech_key:
            return {"status": "error", "message": "Azure Speech key not configured"}
        
        # Map language codes to Azure Speech locale codes
        azure_lang_map = {
            'auto': 'en-US',  # Default for auto-detect
            'en': 'en-US',
            'hi': 'hi-IN',
            'hinglish': 'hi-IN',  # Use Hindi for Hinglish
            'bn': 'bn-IN',     # Bengali (India)
            'ta': 'ta-IN',     # Tamil (India)
            'te': 'te-IN',     # Telugu (India)
            'gu': 'gu-IN',     # Gujarati (India)
            'kn': 'kn-IN',     # Kannada (India)
            'ml': 'ml-IN',     # Malayalam (India)
            'mr': 'mr-IN',     # Marathi (India)
            'pa': 'pa-IN',     # Punjabi (India)
            'ur': 'ur-IN',     # Urdu (India)
            'or': 'or-IN',     # Odia (India)
            'as': 'as-IN',     # Assamese (India)
        }
        
        azure_locale = azure_lang_map.get(lang.lower(), 'en-US')
        
        # Configure Azure Speech
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_recognition_language = azure_locale
        
        # Enable detailed results for confidence scores
        speech_config.output_format = speechsdk.OutputFormat.Detailed
        
        # Create audio config from file
        audio_config = speechsdk.audio.AudioConfig(filename=wav_file_path)
        
        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )
        
        # Perform recognition
        result = speech_recognizer.recognize_once()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Extract confidence score if available
            confidence = 0.9  # Default confidence for Azure
            if hasattr(result, 'json') and result.json:
                try:
                    import json
                    result_json = json.loads(result.json)
                    if 'NBest' in result_json and len(result_json['NBest']) > 0:
                        confidence = result_json['NBest'][0].get('Confidence', 0.9)
                except:
                    pass
            
            return {
                "status": "success", 
                "text": result.text,
                "method": "azure",
                "confidence": confidence,
                "language_detected": azure_locale
            }
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return {
                "status": "success", 
                "text": "",
                "method": "azure",
                "confidence": 0.0,
                "message": "No speech detected"
            }
        else:
            error_details = result.cancellation_details
            current_app.logger.error(f"Azure STT failed: {error_details.reason}")
            return {"status": "error", "message": f"Azure recognition failed: {error_details.reason}"}
    
    except Exception as e:
        current_app.logger.error(f"Azure STT error: {e}")
        return {"status": "error", "message": f"Azure STT error: {str(e)}"}


def try_google_stt(wav_file_path, lang='en'):
    """
    Fallback Google Speech Recognition with enhanced language support
    """
    try:
        # Map language codes to Google Speech locale codes
        google_lang_map = {
            'auto': 'en-US',
            'en': 'en-US',
            'hi': 'hi-IN',
            'hinglish': 'hi-IN',
            'bn': 'bn-IN',     # Bengali (India)
            'ta': 'ta-IN',     # Tamil (India)
            'te': 'te-IN',     # Telugu (India)
            'gu': 'gu-IN',     # Gujarati (India)
            'kn': 'kn-IN',     # Kannada (India)
            'ml': 'ml-IN',     # Malayalam (India)
            'mr': 'mr-IN',     # Marathi (India)
            'pa': 'pa-Guru-IN', # Punjabi (India)
            'ur': 'ur-PK',     # Urdu (Pakistan - better support)
            'or': 'hi-IN',     # Fallback to Hindi for Odia
            'as': 'hi-IN',     # Fallback to Hindi for Assamese
        }
        
        google_locale = google_lang_map.get(lang.lower(), 'en-US')
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source)
            
            try:
                text = recognizer.recognize_google(audio, language=google_locale)
                return {
                    "status": "success", 
                    "text": text,
                    "method": "google",
                    "confidence": 0.8,  # Google doesn't provide confidence scores
                    "language_detected": google_locale
                }
            except sr.UnknownValueError:
                return {
                    "status": "success", 
                    "text": "",
                    "method": "google",
                    "confidence": 0.0,
                    "message": "No speech detected"
                }
            except sr.RequestError as e:
                current_app.logger.error(f"Google STT request error: {e}")
                return {"status": "error", "message": "Google Speech recognition service unavailable"}
    
    except Exception as e:
        current_app.logger.error(f"Google STT error: {e}")
        return {"status": "error", "message": f"Google STT error: {str(e)}"}


def get_stt_capabilities():
    """
    Get available STT capabilities and supported languages
    """
    azure_key = os.getenv('AZURE_SPEECH_KEY')
    azure_available = AZURE_STT_AVAILABLE and azure_key is not None
    
    capabilities = {
        "azure_available": azure_available,
        "google_available": True,  # Always available with speech_recognition
        "supported_languages": [
            {"code": "auto", "name": "Auto-detect", "azure": False, "google": False},
            {"code": "en", "name": "English", "azure": True, "google": True},
            {"code": "hi", "name": "Hindi (हिंदी)", "azure": True, "google": True},
            {"code": "hinglish", "name": "Hinglish", "azure": True, "google": True},
            {"code": "bn", "name": "Bengali (বাংলা)", "azure": True, "google": True},
            {"code": "ta", "name": "Tamil (தமிழ்)", "azure": True, "google": True},
            {"code": "te", "name": "Telugu (తెలుగు)", "azure": True, "google": True},
            {"code": "gu", "name": "Gujarati (ગુજરાતી)", "azure": True, "google": True},
            {"code": "kn", "name": "Kannada (ಕನ್ನಡ)", "azure": True, "google": True},
            {"code": "ml", "name": "Malayalam (മലയാളം)", "azure": True, "google": True},
            {"code": "mr", "name": "Marathi (मराठी)", "azure": True, "google": True},
            {"code": "pa", "name": "Punjabi (ਪੰਜਾਬੀ)", "azure": True, "google": True},
            {"code": "ur", "name": "Urdu (اردو)", "azure": True, "google": True},
            {"code": "or", "name": "Odia (ଓଡ଼ିଆ)", "azure": True, "google": False},
            {"code": "as", "name": "Assamese (অসমীয়া)", "azure": True, "google": False},
        ],
        "max_file_size_mb": 25,
        "supported_formats": ["mp3", "wav", "m4a", "ogg", "flac"],
        "recommended_sample_rate": 16000
    }
    
    return capabilities
