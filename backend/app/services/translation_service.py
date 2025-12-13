"""
Multi-Language Translation Service for ISL Recognition
Supports English to Hindi translation with complete transcript generation
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Translation libraries
try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    print("Warning: googletrans not available. Install with: pip install googletrans==4.0.0rc1")

try:
    from translate import Translator as OfflineTranslator
    OFFLINE_TRANSLATOR_AVAILABLE = True
except ImportError:
    OFFLINE_TRANSLATOR_AVAILABLE = False
    print("Warning: translate not available. Install with: pip install translate==3.6.1")

try:
    from indic_transliteration import sanscript
    INDIC_TRANSLITERATION_AVAILABLE = True
except ImportError:
    INDIC_TRANSLITERATION_AVAILABLE = False
    print("Warning: indic-transliteration not available. Install with: pip install indic-transliteration==2.3.43")

# Fallback Hindi dictionary for offline translation
ENGLISH_TO_HINDI_DICT = {
    # Common words
    'HELLO': 'नमस्ते',
    'THANK': 'धन्यवाद',
    'PLEASE': 'कृपया',
    'YES': 'हाँ',
    'NO': 'नहीं',
    'GOOD': 'अच्छा',
    'BAD': 'बुरा',
    'WATER': 'पानी',
    'FOOD': 'खाना',
    'HOME': 'घर',
    'SCHOOL': 'स्कूल',
    'BOOK': 'किताब',
    'HELP': 'मदद',
    'LOVE': 'प्रेम',
    'FAMILY': 'परिवार',
    'FRIEND': 'दोस्त',
    'WORK': 'काम',
    'TIME': 'समय',
    'DAY': 'दिन',
    'NIGHT': 'रात',
    'MORNING': 'सुबह',
    'EVENING': 'शाम',
    'MONEY': 'पैसा',
    'HAPPY': 'खुश',
    'SAD': 'उदास',
    'BEAUTIFUL': 'सुंदर',
    'IMPORTANT': 'महत्वपूर्ण',
    'LEARN': 'सीखना',
    'TEACH': 'सिखाना',
    'STUDENT': 'छात्र',
    'TEACHER': 'शिक्षक',
    'MOTHER': 'माँ',
    'FATHER': 'पिता',
    'BROTHER': 'भाई',
    'SISTER': 'बहन',
    'CHILD': 'बच्चा',
    'CHILDREN': 'बच्चे',
    'MAN': 'आदमी',
    'WOMAN': 'औरत',
    'BOY': 'लड़का',
    'GIRL': 'लड़की',
    'COME': 'आना',
    'GO': 'जाना',
    'GIVE': 'देना',
    'TAKE': 'लेना',
    'EAT': 'खाना',
    'DRINK': 'पीना',
    'SLEEP': 'सोना',
    'WAKE': 'जागना',
    'SIT': 'बैठना',
    'STAND': 'खड़ा',
    'WALK': 'चलना',
    'RUN': 'दौड़ना',
    'STOP': 'रुकना',
    'START': 'शुरू',
    'FINISH': 'समाप्त',
    'OPEN': 'खोलना',
    'CLOSE': 'बंद',
    'BIG': 'बड़ा',
    'SMALL': 'छोटा',
    'HOT': 'गर्म',
    'COLD': 'ठंडा',
    'NEW': 'नया',
    'OLD': 'पुराना',
    'FAST': 'तेज़',
    'SLOW': 'धीमा',
    'HIGH': 'ऊंचा',
    'LOW': 'नीचा',
    'NEAR': 'पास',
    'FAR': 'दूर',
    'HERE': 'यहाँ',
    'THERE': 'वहाँ',
    'WHERE': 'कहाँ',
    'WHEN': 'कब',
    'WHY': 'क्यों',
    'HOW': 'कैसे',
    'WHAT': 'क्या',
    'WHO': 'कौन',
    'WHICH': 'कौन सा',
    'RED': 'लाल',
    'BLUE': 'नीला',
    'GREEN': 'हरा',
    'YELLOW': 'पीला',
    'BLACK': 'काला',
    'WHITE': 'सफ़ेद',
    'ORANGE': 'नारंगी',
    'PURPLE': 'बैंगनी',
    'PINK': 'गुलाबी',
    'BROWN': 'भूरा',
    'GREY': 'स्लेटी',
    'ONE': 'एक',
    'TWO': 'दो',
    'THREE': 'तीन',
    'FOUR': 'चार',
    'FIVE': 'पांच',
    'SIX': 'छह',
    'SEVEN': 'सात',
    'EIGHT': 'आठ',
    'NINE': 'नौ',
    'TEN': 'दस'
}

# Hindi to English reverse mapping
HINDI_TO_ENGLISH_DICT = {v: k for k, v in ENGLISH_TO_HINDI_DICT.items()}

class TranslationService:
    """Multi-language translation service for ISL recognition"""
    
    def __init__(self):
        self.google_translator = None
        self.offline_translator = None
        self.translation_cache = {}
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi (हिंदी)',
            'hi-rom': 'Hindi (Roman)',
            'bn': 'Bengali (বাংলা)',
            'ta': 'Tamil (தமிழ்)',
            'te': 'Telugu (తెలుగు)',
            'mr': 'Marathi (मराठी)',
            'gu': 'Gujarati (ગુજરાતી)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)',
            'or': 'Odia (ଓଡ଼ିଆ)',
            'as': 'Assamese (অসমীয়া)',
            'ur': 'Urdu (اردو)'
        }
        
        # Initialize translators
        self._init_translators()
        
        # Translation history for transcript
        self.translation_history = []
        
    def _init_translators(self):
        """Initialize available translators"""
        try:
            if GOOGLETRANS_AVAILABLE:
                self.google_translator = Translator()
                print("✅ Google Translator initialized")
        except Exception as e:
            print(f"⚠️ Google Translator initialization failed: {e}")
            
        try:
            if OFFLINE_TRANSLATOR_AVAILABLE:
                self.offline_translator = OfflineTranslator(to_lang="hi", from_lang="en")
                print("✅ Offline Translator initialized")
        except Exception as e:
            print(f"⚠️ Offline Translator initialization failed: {e}")
    
    def translate_text(self, text: str, target_lang: str = 'hi', source_lang: str = 'en') -> Dict:
        """
        Translate text to target language with multiple fallback methods
        
        Args:
            text: Text to translate
            target_lang: Target language code (hi, bn, ta, etc.)
            source_lang: Source language code (default: en)
            
        Returns:
            Dict with translation results and metadata
        """
        if not text or not text.strip():
            return self._create_translation_result("", "", target_lang, source_lang, "empty_input")
        
        text = text.strip().upper()
        
        # Check cache first
        cache_key = f"{text}_{source_lang}_{target_lang}"
        if cache_key in self.translation_cache:
            cached_result = self.translation_cache[cache_key].copy()
            cached_result['from_cache'] = True
            return cached_result
        
        translation_result = None
        method_used = "none"
        
        # Method 1: Google Translate (most accurate)
        if self.google_translator and target_lang != source_lang:
            try:
                result = self.google_translator.translate(text, dest=target_lang, src=source_lang)
                if result and result.text:
                    translation_result = result.text
                    method_used = "google_translate"
            except Exception as e:
                print(f"Google Translate failed: {e}")
        
        # Method 2: Dictionary lookup for Hindi
        if not translation_result and target_lang == 'hi' and source_lang == 'en':
            words = text.split()
            translated_words = []
            
            for word in words:
                if word in ENGLISH_TO_HINDI_DICT:
                    translated_words.append(ENGLISH_TO_HINDI_DICT[word])
                else:
                    translated_words.append(word)  # Keep original if not found
            
            if translated_words:
                translation_result = ' '.join(translated_words)
                method_used = "dictionary_lookup"
        
        # Method 3: Offline translator
        if not translation_result and self.offline_translator and target_lang == 'hi':
            try:
                result = self.offline_translator.translate(text)
                if result:
                    translation_result = result
                    method_used = "offline_translator"
            except Exception as e:
                print(f"Offline translator failed: {e}")
        
        # Method 4: Transliteration for Roman Hindi
        if not translation_result and target_lang == 'hi-rom':
            translation_result = self._transliterate_to_roman_hindi(text)
            method_used = "transliteration"
        
        # Fallback: Return original text
        if not translation_result:
            translation_result = text
            method_used = "no_translation"
        
        # Create result object
        result = self._create_translation_result(
            text, translation_result, target_lang, source_lang, method_used
        )
        
        # Cache the result
        self.translation_cache[cache_key] = result.copy()
        
        # Add to translation history
        self._add_to_history(result)
        
        return result
    
    def _create_translation_result(self, original: str, translated: str, 
                                 target_lang: str, source_lang: str, method: str) -> Dict:
        """Create standardized translation result"""
        return {
            'original_text': original,
            'translated_text': translated,
            'source_language': source_lang,
            'target_language': target_lang,
            'source_language_name': self.supported_languages.get(source_lang, source_lang),
            'target_language_name': self.supported_languages.get(target_lang, target_lang),
            'translation_method': method,
            'timestamp': datetime.now().isoformat(),
            'confidence': self._calculate_confidence(method),
            'from_cache': False
        }
    
    def _calculate_confidence(self, method: str) -> float:
        """Calculate confidence score based on translation method"""
        confidence_scores = {
            'google_translate': 0.95,
            'dictionary_lookup': 0.85,
            'offline_translator': 0.75,
            'transliteration': 0.65,
            'no_translation': 0.0,
            'empty_input': 0.0
        }
        return confidence_scores.get(method, 0.5)
    
    def _transliterate_to_roman_hindi(self, text: str) -> str:
        """Convert English to Roman Hindi (Hinglish)"""
        # Simple phonetic mapping for common words
        roman_hindi_map = {
            'HELLO': 'Namaste',
            'THANK': 'Dhanyawad',
            'PLEASE': 'Kripaya',
            'YES': 'Haan',
            'NO': 'Nahin',
            'GOOD': 'Accha',
            'BAD': 'Bura',
            'WATER': 'Paani',
            'FOOD': 'Khana',
            'HOME': 'Ghar',
            'SCHOOL': 'School',
            'BOOK': 'Kitab',
            'HELP': 'Madad',
            'LOVE': 'Pyaar',
            'FAMILY': 'Parivar',
            'FRIEND': 'Dost',
            'WORK': 'Kaam',
            'TIME': 'Samay',
            'DAY': 'Din',
            'NIGHT': 'Raat'
        }
        
        words = text.split()
        transliterated = []
        
        for word in words:
            if word in roman_hindi_map:
                transliterated.append(roman_hindi_map[word])
            else:
                transliterated.append(word)
        
        return ' '.join(transliterated)
    
    def _add_to_history(self, translation_result: Dict):
        """Add translation to history for transcript generation"""
        self.translation_history.append(translation_result)
        
        # Keep only last 100 translations to manage memory
        if len(self.translation_history) > 100:
            self.translation_history = self.translation_history[-100:]
    
    def translate_sentence(self, sentence: str, target_languages: List[str] = None) -> Dict:
        """
        Translate a complete sentence to multiple languages
        
        Args:
            sentence: Complete sentence to translate
            target_languages: List of target language codes
            
        Returns:
            Dict with translations in all requested languages
        """
        if target_languages is None:
            target_languages = ['hi', 'hi-rom']
        
        translations = {}
        
        for lang in target_languages:
            result = self.translate_text(sentence, target_lang=lang)
            translations[lang] = result
        
        return {
            'original_sentence': sentence,
            'translations': translations,
            'timestamp': datetime.now().isoformat(),
            'languages_count': len(target_languages)
        }
    
    def generate_transcript(self, format_type: str = 'detailed') -> Dict:
        """
        Generate complete transcript of all translations
        
        Args:
            format_type: 'simple', 'detailed', or 'bilingual'
            
        Returns:
            Dict with formatted transcript
        """
        if not self.translation_history:
            return {
                'transcript': 'No translations available yet.',
                'format': format_type,
                'total_translations': 0,
                'generated_at': datetime.now().isoformat()
            }
        
        transcript_lines = []
        
        if format_type == 'simple':
            # Simple format: just the translated text
            for item in self.translation_history:
                transcript_lines.append(item['translated_text'])
            transcript = ' '.join(transcript_lines)
            
        elif format_type == 'bilingual':
            # Bilingual format: English | Hindi
            for item in self.translation_history:
                line = f"{item['original_text']} | {item['translated_text']}"
                transcript_lines.append(line)
            transcript = '\n'.join(transcript_lines)
            
        else:  # detailed format
            # Detailed format with timestamps and metadata
            transcript_lines.append("=== ISL Recognition Translation Transcript ===\n")
            
            for i, item in enumerate(self.translation_history, 1):
                timestamp = datetime.fromisoformat(item['timestamp']).strftime("%H:%M:%S")
                confidence = item['confidence'] * 100
                
                line = f"[{i:03d}] {timestamp} | {item['source_language_name']} → {item['target_language_name']}\n"
                line += f"      Original: {item['original_text']}\n"
                line += f"      Translation: {item['translated_text']}\n"
                line += f"      Method: {item['translation_method']} | Confidence: {confidence:.1f}%\n"
                
                transcript_lines.append(line)
            
            transcript = '\n'.join(transcript_lines)
        
        return {
            'transcript': transcript,
            'format': format_type,
            'total_translations': len(self.translation_history),
            'generated_at': datetime.now().isoformat(),
            'languages_used': list(set(item['target_language'] for item in self.translation_history))
        }
    
    def export_transcript(self, format_type: str = 'detailed', file_format: str = 'txt') -> Dict:
        """
        Export transcript to file format
        
        Args:
            format_type: Transcript format type
            file_format: 'txt', 'json', or 'csv'
            
        Returns:
            Dict with export data and metadata
        """
        transcript_data = self.generate_transcript(format_type)
        
        if file_format == 'json':
            export_data = {
                'transcript_metadata': {
                    'format': format_type,
                    'total_translations': transcript_data['total_translations'],
                    'generated_at': transcript_data['generated_at'],
                    'languages_used': transcript_data.get('languages_used', [])
                },
                'translation_history': self.translation_history
            }
            content = json.dumps(export_data, indent=2, ensure_ascii=False)
            
        elif file_format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # CSV headers
            writer.writerow(['Timestamp', 'Original', 'Translation', 'Source Lang', 'Target Lang', 'Method', 'Confidence'])
            
            # CSV data
            for item in self.translation_history:
                writer.writerow([
                    item['timestamp'],
                    item['original_text'],
                    item['translated_text'],
                    item['source_language_name'],
                    item['target_language_name'],
                    item['translation_method'],
                    f"{item['confidence']*100:.1f}%"
                ])
            
            content = output.getvalue()
            output.close()
            
        else:  # txt format
            content = transcript_data['transcript']
        
        filename = f"isl_translation_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_format}"
        
        return {
            'content': content,
            'filename': filename,
            'file_format': file_format,
            'size_bytes': len(content.encode('utf-8')),
            'generated_at': datetime.now().isoformat()
        }
    
    def get_supported_languages(self) -> Dict:
        """Get list of supported languages"""
        return self.supported_languages.copy()
    
    def clear_history(self):
        """Clear translation history"""
        self.translation_history = []
        self.translation_cache = {}
    
    def get_translation_stats(self) -> Dict:
        """Get translation statistics"""
        if not self.translation_history:
            return {
                'total_translations': 0,
                'languages_used': [],
                'methods_used': [],
                'average_confidence': 0,
                'cache_size': 0
            }
        
        languages_used = list(set(item['target_language'] for item in self.translation_history))
        methods_used = list(set(item['translation_method'] for item in self.translation_history))
        avg_confidence = sum(item['confidence'] for item in self.translation_history) / len(self.translation_history)
        
        return {
            'total_translations': len(self.translation_history),
            'languages_used': languages_used,
            'methods_used': methods_used,
            'average_confidence': avg_confidence,
            'cache_size': len(self.translation_cache),
            'most_recent_translation': self.translation_history[-1] if self.translation_history else None
        }


# Global translation service instance
_translation_service = None

def get_translation_service() -> TranslationService:
    """Get or create global translation service instance"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service