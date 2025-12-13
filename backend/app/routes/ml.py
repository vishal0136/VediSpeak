"""
Machine Learning routes for ISL Recognition
- Live recognition via WebSocket and REST API
- Adaptive learning with data collection
- Session management
"""
from flask import Blueprint, request, jsonify, session
from flask_socketio import emit, join_room, leave_room
from ..utils.decorators import login_required
from ..extensions import socketio
from ..services.translation_service import get_translation_service
import logging
import os
import sys
from datetime import datetime

# Add ML module to path
ml_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ml')
if ml_path not in sys.path:
    sys.path.insert(0, ml_path)

ml_bp = Blueprint("ml", __name__)
logger = logging.getLogger(__name__)

# Global recognizer instance (lazy loaded)
_recognizer = None

def get_recognizer():
    """Get or create the enhanced ISL recognizer instance"""
    global _recognizer
    if _recognizer is None:
        try:
            # Try enhanced recognizer first
            from backend.ml.enhanced_isl_recognition import get_enhanced_recognizer
            _recognizer = get_enhanced_recognizer()
            logger.info("Enhanced ISL recognizer loaded successfully")
        except Exception as e:
            logger.warning(f"Enhanced recognizer failed, falling back to basic: {e}")
            try:
                # Fallback to basic recognizer
                from backend.ml.live_isl_recognition import get_recognizer as get_isl_recognizer
                _recognizer = get_isl_recognizer()
                logger.info("Basic ISL recognizer loaded successfully")
            except Exception as e2:
                logger.error(f"Failed to load any ISL recognizer: {e2}")
                _recognizer = None
    return _recognizer


# =====================================
# ISL RECOGNITION REST API
# =====================================

@ml_bp.route("/api/isl/status", methods=["GET"])
def isl_status():
    """Get ISL recognition system status"""
    try:
        recognizer = get_recognizer()
        if recognizer:
            return jsonify({
                "status": "success",
                "model_info": recognizer.get_model_info()
            })
        else:
            return jsonify({
                "status": "error",
                "message": "ISL recognizer not available"
            }), 503
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/predict", methods=["POST"])
def isl_predict():
    """Predict ISL sign from base64 image"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error", "message": "No image provided"}), 400
        
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        result = recognizer.process_base64_frame(data['image'])
        
        if 'error' in result:
            return jsonify({"status": "error", "message": result['error']}), 400
        
        return jsonify({
            "status": "success",
            **result
        })
        
    except Exception as e:
        logger.error(f"ISL prediction error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/text", methods=["GET"])
def get_isl_text():
    """Get current recognized text"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        return jsonify({
            "status": "success",
            **recognizer.get_text()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/clear", methods=["POST"])
def clear_isl_text():
    """Clear recognized text"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        return jsonify({
            "status": "success",
            **recognizer.clear_text()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/backspace", methods=["POST"])
def isl_backspace():
    """Remove last character"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        return jsonify({
            "status": "success",
            **recognizer.backspace()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/space", methods=["POST"])
def isl_add_space():
    """Add space to text"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        return jsonify({
            "status": "success",
            **recognizer.add_space()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/add-space", methods=["POST"])
def isl_add_space_alt():
    """Add space to text (alternative endpoint)"""
    return isl_add_space()


@ml_bp.route("/api/isl/model-info", methods=["GET"])
def get_model_info():
    """Get detailed model information"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        model_info = recognizer.get_model_info()
        return jsonify({
            "status": "success",
            "model_info": model_info
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# =====================================
# AUTO-ADAPTATION ENDPOINTS
# =====================================

@ml_bp.route("/api/isl/collect", methods=["POST"])
@login_required
def collect_sample():
    """Collect a sample for model adaptation"""
    try:
        data = request.get_json()
        if not data or 'image' not in data or 'label' not in data:
            return jsonify({"status": "error", "message": "Image and label required"}), 400
        
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        result = recognizer.collect_sample_base64(data['image'], data['label'])
        
        return jsonify({
            "status": "success" if result.get('success') else "error",
            **result
        })
        
    except Exception as e:
        logger.error(f"Sample collection error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/samples", methods=["GET"])
@login_required
def get_samples_count():
    """Get count of collected samples"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        return jsonify({
            "status": "success",
            **recognizer.get_collected_samples_count()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/adapt", methods=["POST"])
@login_required
def trigger_adaptation():
    """Trigger model adaptation with collected samples"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        result = recognizer.trigger_adaptation()
        
        # Log activity if successful
        if result.get('success'):
            from ..models.stats import UserActivity
            user_id = session.get("user_id")
            UserActivity.log_activity(user_id, "model_adapted", "Triggered ISL model adaptation", 50)
        
        return jsonify({
            "status": "success" if result.get('success') else "error",
            **result
        })
        
    except Exception as e:
        logger.error(f"Adaptation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/classes", methods=["GET"])
def get_classes():
    """Get available ISL classes"""
    try:
        recognizer = get_recognizer()
        if recognizer:
            info = recognizer.get_model_info()
            return jsonify({
                "status": "success",
                "classes": info.get('classes', [])
            })
        else:
            # Return default classes
            classes = [str(i) for i in range(10)] + [chr(ord('A') + i) for i in range(26)]
            return jsonify({
                "status": "success",
                "classes": classes
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/diagnostics", methods=["GET"])
def isl_diagnostics():
    """Comprehensive ISL system diagnostics"""
    try:
        import os
        import sys
        import torch
        
        diagnostics = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd()
            },
            "dependencies": {},
            "model": {},
            "files": {}
        }
        
        # Check dependencies
        try:
            import torch
            diagnostics["dependencies"]["torch"] = {
                "version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
            }
        except Exception as e:
            diagnostics["dependencies"]["torch"] = {"error": str(e)}
        
        try:
            import cv2
            diagnostics["dependencies"]["opencv"] = {"version": cv2.__version__}
        except Exception as e:
            diagnostics["dependencies"]["opencv"] = {"error": str(e)}
        
        try:
            import mediapipe
            diagnostics["dependencies"]["mediapipe"] = {"version": mediapipe.__version__}
        except Exception as e:
            diagnostics["dependencies"]["mediapipe"] = {"error": str(e)}
        
        try:
            import timm
            diagnostics["dependencies"]["timm"] = {"available": True}
        except Exception as e:
            diagnostics["dependencies"]["timm"] = {"error": str(e)}
        
        # Check model files
        model_files = [
            "checkpoints/best.pth",
            "checkpoints/last.pth",
            "checkpoints/train_log.csv"
        ]
        
        for file_path in model_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                diagnostics["files"][file_path] = {
                    "exists": True,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                diagnostics["files"][file_path] = {"exists": False}
        
        # Check recognizer
        try:
            recognizer = get_recognizer()
            if recognizer:
                model_info = recognizer.get_model_info()
                diagnostics["model"] = {
                    "loaded": model_info.get("model_loaded", False),
                    "device": model_info.get("device", "unknown"),
                    "classes_count": len(model_info.get("classes", [])),
                    "mediapipe_available": model_info.get("mediapipe_available", False)
                }
            else:
                diagnostics["model"] = {"loaded": False, "error": "Recognizer not initialized"}
        except Exception as e:
            diagnostics["model"] = {"loaded": False, "error": str(e)}
        
        return jsonify(diagnostics)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


# =====================================
# WEBSOCKET HANDLERS FOR LIVE RECOGNITION
# =====================================

@socketio.on('join_isl_room')
def handle_join_isl():
    """Join ISL recognition room for real-time updates"""
    room = 'isl_recognition'
    join_room(room)
    emit('isl_joined', {'message': 'Connected to ISL recognition'})


@socketio.on('leave_isl_room')
def handle_leave_isl():
    """Leave ISL recognition room"""
    room = 'isl_recognition'
    leave_room(room)
    emit('isl_left', {'message': 'Disconnected from ISL recognition'})


@socketio.on('isl_frame')
def handle_isl_frame(data):
    """Process incoming webcam frame for ISL recognition"""
    try:
        if 'image' not in data:
            emit('isl_error', {'error': 'No image data'})
            return
        
        recognizer = get_recognizer()
        if not recognizer:
            emit('isl_error', {'error': 'Recognizer not available'})
            return
        
        result = recognizer.process_base64_frame(data['image'])
        
        if 'error' in result:
            emit('isl_error', result)
        else:
            emit('isl_prediction', result)
            
    except Exception as e:
        logger.error(f"WebSocket ISL error: {e}")
        emit('isl_error', {'error': str(e)})


@socketio.on('isl_collect_sample')
def handle_collect_sample(data):
    """Collect sample via WebSocket"""
    try:
        if 'image' not in data or 'label' not in data:
            emit('isl_collect_error', {'error': 'Image and label required'})
            return
        
        recognizer = get_recognizer()
        if not recognizer:
            emit('isl_collect_error', {'error': 'Recognizer not available'})
            return
        
        result = recognizer.collect_sample_base64(data['image'], data['label'])
        emit('isl_sample_collected', result)
        
    except Exception as e:
        emit('isl_collect_error', {'error': str(e)})


@socketio.on('isl_clear_text')
def handle_clear_text():
    """Clear text via WebSocket"""
    try:
        recognizer = get_recognizer()
        if recognizer:
            result = recognizer.clear_text()
            emit('isl_text_cleared', result)
    except Exception as e:
        emit('isl_error', {'error': str(e)})


@socketio.on('isl_backspace')
def handle_backspace():
    """Backspace via WebSocket"""
    try:
        recognizer = get_recognizer()
        if recognizer:
            result = recognizer.backspace()
            emit('isl_text_updated', result)
    except Exception as e:
        emit('isl_error', {'error': str(e)})


@socketio.on('isl_add_space')
def handle_add_space():
    """Add space via WebSocket"""
    try:
        recognizer = get_recognizer()
        if recognizer:
            result = recognizer.add_space()
            emit('isl_text_updated', result)
    except Exception as e:
        emit('isl_error', {'error': str(e)})


@socketio.on('isl_force_word')
def handle_force_word(data=None):
    """Force word completion via WebSocket"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            emit('isl_error', {'error': 'Recognizer not available'})
            return
        
        # If a specific word is provided, use it
        if data and 'word' in data:
            # Clear current word and add the suggested word
            recognizer.word_engine.current_word = ""
            recognizer.word_engine.word_confidence_scores = []
            
            # Add the word directly to formed words
            recognizer.word_engine.formed_words.append({
                'word': data['word'].upper(),
                'original': data['word'].upper(),
                'confidence': 1.0,  # High confidence for user-selected word
                'timestamp': datetime.now().isoformat()
            })
            
            result = {
                'success': True,
                'current_text': recognizer.word_engine.get_sentence(),
                'current_word': recognizer.word_engine.get_current_word()
            }
        else:
            # Force completion of current word
            if hasattr(recognizer, 'force_word_completion'):
                result = recognizer.force_word_completion()
            else:
                result = recognizer.add_space()
        
        emit('isl_text_updated', result)
    except Exception as e:
        emit('isl_error', {'error': str(e)})


# =====================================
# ENHANCED FEATURES ENDPOINTS
# =====================================

@ml_bp.route("/api/isl/word/complete", methods=["POST"])
def force_word_completion():
    """Force completion of current word"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        if hasattr(recognizer, 'force_word_completion'):
            result = recognizer.force_word_completion()
            return jsonify({
                "status": "success",
                **result
            })
        else:
            # Fallback for basic recognizer
            return jsonify({
                "status": "success",
                **recognizer.add_space()
            })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/suggestions", methods=["GET"])
def get_word_suggestions():
    """Get word suggestions for current partial word"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        # Get current word and suggestions
        text_info = recognizer.get_text()
        current_word = text_info.get('current_word', '')
        
        suggestions = []
        if hasattr(recognizer, 'word_engine') and len(current_word) >= 2:
            import difflib
            from backend.ml.enhanced_isl_recognition import COMMON_WORDS
            suggestions = difflib.get_close_matches(
                current_word.upper(), COMMON_WORDS, n=5, cutoff=0.4
            )
        
        return jsonify({
            "status": "success",
            "current_word": current_word,
            "suggestions": suggestions
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/performance", methods=["GET"])
def get_performance_metrics():
    """Get performance metrics for the ISL system"""
    try:
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        model_info = recognizer.get_model_info()
        
        return jsonify({
            "status": "success",
            "performance": {
                "avg_processing_time": model_info.get('avg_processing_time', 0),
                "frames_processed": model_info.get('frames_processed', 0),
                "enhanced_features": model_info.get('enhanced_features', False),
                "temporal_smoothing": model_info.get('temporal_smoothing', False),
                "word_formation": model_info.get('word_formation', False),
                "context_awareness": model_info.get('context_awareness', False)
            }
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/word/suggestions", methods=["POST"])
def apply_word_suggestion():
    """Apply a word suggestion to complete current word"""
    try:
        data = request.get_json()
        if not data or 'word' not in data:
            return jsonify({"status": "error", "message": "Word required"}), 400
        
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "Recognizer not available"}), 503
        
        # Clear current word and add the suggested word
        recognizer.word_engine.current_word = ""
        recognizer.word_engine.word_confidence_scores = []
        
        # Add the word directly to formed words
        recognizer.word_engine.formed_words.append({
            'word': data['word'].upper(),
            'original': data['word'].upper(),
            'confidence': 1.0,  # High confidence for user-selected word
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            "status": "success",
            "current_text": recognizer.word_engine.get_sentence(),
            "current_word": recognizer.word_engine.get_current_word()
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/isl/health", methods=["GET"])
def health_check():
    """Simple health check for ISL system"""
    try:
        recognizer = get_recognizer()
        if recognizer:
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "recognizer": "available"
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "recognizer": "unavailable"
            }), 503
    except Exception as e:
        return jsonify({
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 500

# =====================================
# TRANSLATION API ENDPOINTS

@ml_bp.route("/api/translation/translate", methods=["POST"])
def translate_text():
    """Translate text to specified language"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"status": "error", "message": "Text required"}), 400
        
        text = data['text']
        target_lang = data.get('target_language', 'hi')  # Default to Hindi
        source_lang = data.get('source_language', 'en')  # Default to English
        
        translation_service = get_translation_service()
        result = translation_service.translate_text(text, target_lang, source_lang)
        
        return jsonify({
            "status": "success",
            "translation": result
        })
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/translation/sentence", methods=["POST"])
def translate_sentence():
    """Translate sentence to multiple languages"""
    try:
        data = request.get_json()
        if not data or 'sentence' not in data:
            return jsonify({"status": "error", "message": "Sentence required"}), 400
        
        sentence = data['sentence']
        target_languages = data.get('target_languages', ['hi', 'hi-rom'])
        
        translation_service = get_translation_service()
        result = translation_service.translate_sentence(sentence, target_languages)
        
        return jsonify({
            "status": "success",
            "multi_translation": result
        })
        
    except Exception as e:
        logger.error(f"Multi-translation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/translation/languages", methods=["GET"])
def get_supported_languages():
    """Get list of supported languages"""
    try:
        translation_service = get_translation_service()
        languages = translation_service.get_supported_languages()
        
        return jsonify({
            "status": "success",
            "supported_languages": languages
        })
        
    except Exception as e:
        logger.error(f"Languages error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/translation/transcript", methods=["GET"])
def get_translation_transcript():
    """Generate translation transcript"""
    try:
        format_type = request.args.get('format', 'detailed')  # simple, detailed, bilingual
        
        translation_service = get_translation_service()
        transcript = translation_service.generate_transcript(format_type)
        
        return jsonify({
            "status": "success",
            "transcript": transcript
        })
        
    except Exception as e:
        logger.error(f"Transcript error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/translation/export", methods=["POST"])
def export_translation_transcript():
    """Export translation transcript to file"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'detailed')  # simple, detailed, bilingual
        file_format = data.get('file_format', 'txt')  # txt, json, csv
        
        translation_service = get_translation_service()
        export_data = translation_service.export_transcript(format_type, file_format)
        
        return jsonify({
            "status": "success",
            "export": export_data
        })
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/translation/stats", methods=["GET"])
def get_translation_stats():
    """Get translation statistics"""
    try:
        translation_service = get_translation_service()
        stats = translation_service.get_translation_stats()
        
        return jsonify({
            "status": "success",
            "statistics": stats
        })
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/translation/clear", methods=["POST"])
def clear_translation_history():
    """Clear translation history"""
    try:
        translation_service = get_translation_service()
        translation_service.clear_history()
        
        return jsonify({
            "status": "success",
            "message": "Translation history cleared"
        })
        
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/api/translation/isl-auto", methods=["POST"])
def auto_translate_isl():
    """Auto-translate current ISL recognition text"""
    try:
        data = request.get_json()
        target_languages = data.get('target_languages', ['hi', 'hi-rom'])
        
        # Get current ISL text
        recognizer = get_recognizer()
        if not recognizer:
            return jsonify({"status": "error", "message": "ISL recognizer not available"}), 503
        
        text_info = recognizer.get_text()
        current_text = text_info.get('current_text', '')
        
        if not current_text:
            return jsonify({
                "status": "success",
                "message": "No text to translate",
                "translations": {}
            })
        
        # Translate to multiple languages
        translation_service = get_translation_service()
        result = translation_service.translate_sentence(current_text, target_languages)
        
        return jsonify({
            "status": "success",
            "isl_text": current_text,
            "translations": result
        })
        
    except Exception as e:
        logger.error(f"ISL auto-translation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# =====================================
# SYSTEM READINESS API

@ml_bp.route("/api/system/readiness", methods=["GET"])
def check_system_readiness():
    """Check if all systems are ready for ISL recognition"""
    try:
        readiness_status = {
            'overall_ready': False,
            'components': {},
            'timestamp': datetime.now().isoformat(),
            'ready_message': '',
            'issues': []
        }
        
        # Check ML Model
        try:
            recognizer = get_recognizer()
            if recognizer and recognizer.model is not None:
                model_info = recognizer.get_model_info()
                readiness_status['components']['ml_model'] = {
                    'status': 'ready',
                    'details': {
                        'model_loaded': model_info.get('model_loaded', False),
                        'device': model_info.get('device', 'unknown'),
                        'classes': model_info.get('num_classes', 0),
                        'enhanced_features': model_info.get('enhanced_features', False),
                        'mediapipe_available': model_info.get('mediapipe_available', False)
                    }
                }
            else:
                readiness_status['components']['ml_model'] = {
                    'status': 'not_ready',
                    'details': {'error': 'Model not loaded'}
                }
                readiness_status['issues'].append('ML model is not loaded')
        except Exception as e:
            readiness_status['components']['ml_model'] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
            readiness_status['issues'].append(f'ML model error: {str(e)}')
        
        # Check Translation Service
        try:
            translation_service = get_translation_service()
            languages = translation_service.get_supported_languages()
            stats = translation_service.get_translation_stats()
            
            readiness_status['components']['translation_service'] = {
                'status': 'ready',
                'details': {
                    'supported_languages': len(languages),
                    'google_translator': hasattr(translation_service, 'google_translator') and translation_service.google_translator is not None,
                    'offline_translator': hasattr(translation_service, 'offline_translator') and translation_service.offline_translator is not None,
                    'cache_size': stats.get('cache_size', 0)
                }
            }
        except Exception as e:
            readiness_status['components']['translation_service'] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
            readiness_status['issues'].append(f'Translation service error: {str(e)}')
        
        # Check Database Connection
        try:
            from ..utils.db_helpers import DB_AVAILABLE, _db_init_error
            if DB_AVAILABLE:
                readiness_status['components']['database'] = {
                    'status': 'ready',
                    'details': {'connection': 'successful'}
                }
            else:
                error_msg = str(_db_init_error) if _db_init_error else 'Database not available'
                readiness_status['components']['database'] = {
                    'status': 'not_ready',
                    'details': {'error': error_msg}
                }
                readiness_status['issues'].append(f'Database: {error_msg}')
        except Exception as e:
            readiness_status['components']['database'] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
            readiness_status['issues'].append(f'Database error: {str(e)}')
        
        # Check SocketIO
        try:
            from ..extensions import socketio
            if socketio:
                readiness_status['components']['socketio'] = {
                    'status': 'ready',
                    'details': {'websocket': 'available'}
                }
            else:
                readiness_status['components']['socketio'] = {
                    'status': 'not_ready',
                    'details': {'error': 'SocketIO not initialized'}
                }
                readiness_status['issues'].append('SocketIO not available')
        except Exception as e:
            readiness_status['components']['socketio'] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
            readiness_status['issues'].append(f'SocketIO error: {str(e)}')
        
        # Determine overall readiness
        ready_components = [comp for comp in readiness_status['components'].values() if comp['status'] == 'ready']
        total_components = len(readiness_status['components'])
        
        if len(ready_components) == total_components:
            readiness_status['overall_ready'] = True
            readiness_status['ready_message'] = '🎉 All systems ready! You can now start ISL recognition.'
        else:
            readiness_status['overall_ready'] = False
            ready_count = len(ready_components)
            readiness_status['ready_message'] = f'⏳ System loading... ({ready_count}/{total_components} components ready)'
        
        # Add performance info if ML model is ready
        if readiness_status['components'].get('ml_model', {}).get('status') == 'ready':
            try:
                recognizer = get_recognizer()
                model_info = recognizer.get_model_info()
                readiness_status['performance'] = {
                    'avg_processing_time': model_info.get('avg_processing_time', 0),
                    'frames_processed': model_info.get('frames_processed', 0),
                    'recognition_active': model_info.get('recognition_active', False)
                }
            except:
                pass
        
        return jsonify({
            "status": "success",
            "readiness": readiness_status
        })
        
    except Exception as e:
        logger.error(f"System readiness check error: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e),
            "readiness": {
                'overall_ready': False,
                'ready_message': '❌ System check failed',
                'issues': [str(e)]
            }
        }), 500


@ml_bp.route("/api/system/startup-status", methods=["GET"])
def get_startup_status():
    """Get detailed startup status for progress tracking"""
    try:
        startup_phases = []
        
        # Phase 1: ML Model Loading
        try:
            recognizer = get_recognizer()
            if recognizer and recognizer.model is not None:
                startup_phases.append({
                    'phase': 'ml_model',
                    'name': 'ML Model Loading',
                    'status': 'completed',
                    'message': '✅ Enhanced ISL model loaded successfully',
                    'progress': 100
                })
            else:
                startup_phases.append({
                    'phase': 'ml_model',
                    'name': 'ML Model Loading',
                    'status': 'loading',
                    'message': '⏳ Loading Enhanced ISL model...',
                    'progress': 50
                })
        except Exception as e:
            startup_phases.append({
                'phase': 'ml_model',
                'name': 'ML Model Loading',
                'status': 'error',
                'message': f'❌ Model loading failed: {str(e)}',
                'progress': 0
            })
        
        # Phase 2: Translation Service
        try:
            translation_service = get_translation_service()
            languages = translation_service.get_supported_languages()
            startup_phases.append({
                'phase': 'translation',
                'name': 'Translation Service',
                'status': 'completed',
                'message': f'✅ Translation service ready ({len(languages)} languages)',
                'progress': 100
            })
        except Exception as e:
            startup_phases.append({
                'phase': 'translation',
                'name': 'Translation Service',
                'status': 'error',
                'message': f'❌ Translation service failed: {str(e)}',
                'progress': 0
            })
        
        # Phase 3: MediaPipe
        try:
            recognizer = get_recognizer()
            if recognizer and hasattr(recognizer, 'mp_hands') and recognizer.mp_hands is not None:
                startup_phases.append({
                    'phase': 'mediapipe',
                    'name': 'Hand Detection (MediaPipe)',
                    'status': 'completed',
                    'message': '✅ MediaPipe hand detection ready',
                    'progress': 100
                })
            else:
                startup_phases.append({
                    'phase': 'mediapipe',
                    'name': 'Hand Detection (MediaPipe)',
                    'status': 'loading',
                    'message': '⏳ Initializing MediaPipe...',
                    'progress': 75
                })
        except Exception as e:
            startup_phases.append({
                'phase': 'mediapipe',
                'name': 'Hand Detection (MediaPipe)',
                'status': 'error',
                'message': f'❌ MediaPipe failed: {str(e)}',
                'progress': 0
            })
        
        # Phase 4: Database
        try:
            from ..utils.db_helpers import DB_AVAILABLE, _db_init_error
            if DB_AVAILABLE:
                startup_phases.append({
                    'phase': 'database',
                    'name': 'Database Connection',
                    'status': 'completed',
                    'message': '✅ Database connected successfully',
                    'progress': 100
                })
            else:
                error_msg = str(_db_init_error) if _db_init_error else 'Database not available'
                startup_phases.append({
                    'phase': 'database',
                    'name': 'Database Connection',
                    'status': 'error',
                    'message': f'❌ Database: {error_msg}',
                    'progress': 0
                })
        except Exception as e:
            startup_phases.append({
                'phase': 'database',
                'name': 'Database Connection',
                'status': 'error',
                'message': f'❌ Database error: {str(e)}',
                'progress': 0
            })
        
        # Calculate overall progress
        completed_phases = [p for p in startup_phases if p['status'] == 'completed']
        total_phases = len(startup_phases)
        overall_progress = (len(completed_phases) / total_phases) * 100 if total_phases > 0 else 0
        
        all_ready = len(completed_phases) == total_phases
        
        return jsonify({
            "status": "success",
            "startup": {
                'phases': startup_phases,
                'overall_progress': round(overall_progress, 1),
                'all_ready': all_ready,
                'completed_phases': len(completed_phases),
                'total_phases': total_phases,
                'ready_message': '🎉 System Ready! Start signing to begin ISL recognition.' if all_ready else f'⏳ Loading... ({len(completed_phases)}/{total_phases} components ready)'
            }
        })
        
    except Exception as e:
        logger.error(f"Startup status error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "startup": {
                'all_ready': False,
                'overall_progress': 0,
                'ready_message': '❌ System startup check failed'
            }
        }), 500