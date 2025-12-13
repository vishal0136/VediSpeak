"""
Enhanced Text-to-Speech service with Azure TTS and gTTS fallback
"""
import os
import time
import base64
from io import BytesIO
from gtts import gTTS
from pydub import AudioSegment
from flask import current_app

# Import Azure TTS service
try:
    from .azure_tts_service import azure_text_to_speech_service
    AZURE_TTS_AVAILABLE = True
except ImportError:
    AZURE_TTS_AVAILABLE = False

def text_to_speech_service(text, lang='hi', voice_gender='default', 
                          speech_rate='medium', pitch='medium', 
                          audio_format='mp3', use_azure=None, auto_translate=True):
    """
    Enhanced text-to-speech service with Azure TTS and gTTS fallback
    
    Args:
        text: Text to convert
        lang: Language code ('hi' for Hindi, 'en' for English, etc.)
        voice_gender: 'male', 'female', or 'default' (Azure only)
        speech_rate: 'x-slow', 'slow', 'medium', 'fast', 'x-fast' (Azure only)
        pitch: 'x-low', 'low', 'medium', 'high', 'x-high' (Azure only)
        audio_format: 'mp3', 'wav', 'ogg'
        use_azure: Force Azure TTS (True) or gTTS (False), None for auto
    
    Returns:
        dict: {"status": "success", "audio_data": "data:audio/mp3;base64,..."}
    """
    try:
        # Validate input
        if not text or not text.strip():
            return {"status": "error", "message": "No text provided"}
        
        # Determine which TTS service to use
        should_use_azure = False
        
        if use_azure is True:
            should_use_azure = True
        elif use_azure is False:
            should_use_azure = False
        else:
            # Auto-detect: Use Azure if available and configured
            azure_key = os.getenv('AZURE_SPEECH_KEY')
            should_use_azure = AZURE_TTS_AVAILABLE and azure_key is not None
        
        # Try Azure TTS first (if available and configured)
        if should_use_azure:
            try:
                current_app.logger.info(f"Using Azure TTS for language: {lang}")
                result = azure_text_to_speech_service(
                    text=text,
                    lang=lang,
                    voice_gender=voice_gender,
                    speech_rate=speech_rate,
                    pitch=pitch,
                    audio_format=audio_format,
                    auto_translate=auto_translate
                )
                
                if result["status"] == "success":
                    result["provider"] = "Azure Cognitive Services"
                    result["quality"] = "Neural Voice"
                    return result
                else:
                    current_app.logger.warning(f"Azure TTS failed: {result.get('message')}")
                    # Fall back to gTTS
                    
            except Exception as e:
                current_app.logger.error(f"Azure TTS error: {e}")
                # Fall back to gTTS
        
        # Use gTTS as fallback or primary
        current_app.logger.info(f"Using gTTS for language: {lang}")
        return gtts_text_to_speech(text, lang, audio_format)
        
    except Exception as e:
        current_app.logger.error(f"TTS service error: {e}")
        return {"status": "error", "message": "TTS conversion failed"}

def gtts_text_to_speech(text, lang='hi', audio_format='mp3'):
    """
    Google Text-to-Speech implementation (fallback)
    """
    try:
        # Limit text length for gTTS
        text = text[:2000]
        
        # Map language codes for gTTS
        gtts_lang_map = {
            'hi': 'hi',
            'hinglish': 'hi',
            'en': 'en',
            'bn': 'bn',
            'ta': 'ta',
            'te': 'te',
            'gu': 'gu',
            'kn': 'kn',
            'ml': 'ml',
            'mr': 'mr',
            'pa': 'pa',
            'ur': 'ur'
        }
        
        gtts_lang = gtts_lang_map.get(lang, 'en')
        
        # Split into chunks for better processing
        chunk_size = 120
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Combine audio chunks
        audio_combined = AudioSegment.silent(duration=0)
        
        for chunk in chunks:
            tts = gTTS(text=chunk, lang=gtts_lang, slow=False)
            buf = BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            seg = AudioSegment.from_file(buf, format="mp3")
            audio_combined += seg
            time.sleep(0.01)  # Small delay to avoid rate limiting
        
        # Convert to requested format
        final_buf = BytesIO()
        if audio_format == 'wav':
            audio_combined.export(final_buf, format="wav")
            mime_type = "audio/wav"
        elif audio_format == 'ogg':
            audio_combined.export(final_buf, format="ogg")
            mime_type = "audio/ogg"
        else:  # Default to mp3
            audio_combined.export(final_buf, format="mp3")
            mime_type = "audio/mp3"
            
        final_buf.seek(0)
        audio_base64 = base64.b64encode(final_buf.read()).decode("utf-8")
        audio_data_url = f"data:{mime_type};base64,{audio_base64}"
        
        return {
            "status": "success", 
            "audio_data": audio_data_url,
            "provider": "Google Text-to-Speech",
            "quality": "Standard",
            "language": lang,
            "format": audio_format
        }
    
    except Exception as e:
        current_app.logger.error(f"gTTS error: {e}")
        return {"status": "error", "message": "gTTS conversion failed"}

def get_tts_capabilities():
    """
    Get available TTS capabilities and supported languages
    """
    azure_key = os.getenv('AZURE_SPEECH_KEY')
    azure_available = AZURE_TTS_AVAILABLE and azure_key is not None
    
    capabilities = {
        "providers": {
            "azure": {
                "available": azure_available,
                "name": "Azure Cognitive Services",
                "quality": "Neural Voice",
                "features": ["Multiple voices", "Speed control", "Pitch control", "SSML support"]
            },
            "gtts": {
                "available": True,
                "name": "Google Text-to-Speech", 
                "quality": "Standard",
                "features": ["Basic synthesis", "Multiple languages"]
            }
        },
        "languages": {
            "en": "English",
            "hi": "Hindi (हिंदी)",
            "hinglish": "Hinglish",
            "bn": "Bengali (বাংলা)",
            "ta": "Tamil (தமிழ்)",
            "te": "Telugu (తెలుగు)",
            "gu": "Gujarati (ગુજરાતી)",
            "kn": "Kannada (ಕನ್ನಡ)",
            "ml": "Malayalam (മലയാളം)",
            "mr": "Marathi (मराठी)",
            "pa": "Punjabi (ਪੰਜਾਬੀ)",
            "ur": "Urdu (اردو)"
        },
        "voice_options": {
            "genders": ["default", "man", "woman", "child", "elderly_man", "elderly_woman", "male", "female"] if azure_available else ["default"],
            "rates": ["x-slow", "slow", "medium", "fast", "x-fast"] if azure_available else ["medium"],
            "pitches": ["x-low", "low", "medium", "high", "x-high"] if azure_available else ["medium"],
            "formats": ["mp3", "wav", "ogg"]
        },
        "recommended_provider": "azure" if azure_available else "gtts"
    }
    
    return capabilities
