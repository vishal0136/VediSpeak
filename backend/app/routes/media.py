"""
Enhanced Media routes: /text_to_speech, /speech_to_text, /translate, /tts_capabilities, /stt_capabilities
"""
from flask import Blueprint, request, jsonify
from ..utils.decorators import login_required
from ..services.tts_service import text_to_speech_service, get_tts_capabilities
from ..services.stt_service import speech_to_text_service, get_stt_capabilities
from ..services.translation_service import get_translation_service

media_bp = Blueprint("media", __name__)

@media_bp.route("/text_to_speech", methods=["POST"])
@login_required
def text_to_speech():
    """Enhanced text-to-speech with Azure TTS and advanced options"""
    try:
        data = request.get_json() or {}
        text = data.get("text", "")
        lang = data.get("lang", "hi")
        
        # Enhanced options for Azure TTS
        voice_gender = data.get("voice_gender", "default")
        speech_rate = data.get("speech_rate", "medium") 
        pitch = data.get("pitch", "medium")
        audio_format = data.get("audio_format", "mp3")
        use_azure = data.get("use_azure", None)  # None for auto-detect
        auto_translate = data.get("auto_translate", True)  # Enable auto-translation by default
        
        result = text_to_speech_service(
            text=text,
            lang=lang,
            voice_gender=voice_gender,
            speech_rate=speech_rate,
            pitch=pitch,
            audio_format=audio_format,
            use_azure=use_azure,
            auto_translate=auto_translate
        )
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"TTS failed: {str(e)}"}), 500

@media_bp.route("/tts_capabilities", methods=["GET"])
@login_required
def tts_capabilities():
    """Get available TTS capabilities and supported languages"""
    try:
        capabilities = get_tts_capabilities()
        return jsonify({
            "status": "success",
            "capabilities": capabilities
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to get capabilities: {str(e)}"}), 500

@media_bp.route("/speech_to_text", methods=["POST"])
@login_required
def speech_to_text():
    """Convert speech to text"""
    try:
        data = request.get_json() or {}
        audio_data = data.get("audio_data", "")
        lang = data.get("lang", "en")
        
        result = speech_to_text_service(audio_data, lang)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({"status": "error", "message": "STT failed"}), 500

@media_bp.route("/translate", methods=["POST"])
@login_required
def translate():
    """Translate text between languages"""
    try:
        data = request.get_json() or {}
        text = data.get("text", "")
        from_lang = data.get("from_lang", "auto")
        to_lang = data.get("to_lang", "hi")
        
        if not text.strip():
            return jsonify({
                "status": "error", 
                "message": "Text is required for translation"
            }), 400
        
        if from_lang == to_lang and from_lang != "auto":
            return jsonify({
                "status": "error", 
                "message": "Source and target languages cannot be the same"
            }), 400
        
        # Get translation service
        translation_service = get_translation_service()
        
        # Handle auto-detect
        source_lang = "en" if from_lang == "auto" else from_lang
        
        # Perform translation
        result = translation_service.translate_text(
            text=text, 
            target_lang=to_lang, 
            source_lang=source_lang
        )
        
        if result and result.get("translated_text"):
            return jsonify({
                "status": "success",
                "translated_text": result["translated_text"],
                "source_language": result.get("source_language", source_lang),
                "target_language": result.get("target_language", to_lang),
                "translation_method": result.get("translation_method", "unknown"),
                "confidence": result.get("confidence", 0.8)
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Translation failed - no result returned"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Translation service error: {str(e)}"
        }), 500
@media_bp.route("/stt_capabilities", methods=["GET"])
@login_required
def stt_capabilities():
    """Get available STT capabilities and supported languages"""
    try:
        capabilities = get_stt_capabilities()
        return jsonify({
            "status": "success",
            "capabilities": capabilities
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to get STT capabilities: {str(e)}"}), 500