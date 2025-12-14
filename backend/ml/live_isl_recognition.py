"""
Live ISL Recognition Module
Provides backward compatibility and imports from enhanced_isl_recognition
"""

# Import the enhanced recognizer
from .enhanced_isl_recognition import get_enhanced_recognizer, EnhancedISLRecognizer

def get_recognizer():
    """Get the ISL recognizer instance"""
    return get_enhanced_recognizer()

# Export the main class for direct import
__all__ = ['get_recognizer', 'EnhancedISLRecognizer']