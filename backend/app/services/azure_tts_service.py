"""
Microsoft Azure Cognitive Services Text-to-Speech service
Supports multiple languages with high-quality neural voices
"""
import os
import base64
import requests
import time
from io import BytesIO
from flask import current_app

class AzureTTSService:
    def __init__(self):
        self.subscription_key = os.getenv('AZURE_SPEECH_KEY')
        self.region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
        self.base_url = f"https://{self.region}.tts.speech.microsoft.com/"
        
        # Enhanced voice mapping with more voice types
        self.voice_mapping = {
            'en': {
                'man': 'en-US-DavisNeural',
                'woman': 'en-US-JennyNeural',
                'child': 'en-US-AnaNeural',
                'elderly_man': 'en-US-GuyNeural',
                'elderly_woman': 'en-US-AriaNeural',
                'male': 'en-US-DavisNeural',
                'female': 'en-US-JennyNeural',
                'default': 'en-US-AriaNeural'
            },
            'hi': {
                'man': 'hi-IN-MadhurNeural',
                'woman': 'hi-IN-SwaraNeural',
                'child': 'hi-IN-SwaraNeural',  # Using female voice for child
                'elderly_man': 'hi-IN-MadhurNeural',
                'elderly_woman': 'hi-IN-SwaraNeural',
                'male': 'hi-IN-MadhurNeural',
                'female': 'hi-IN-SwaraNeural', 
                'default': 'hi-IN-SwaraNeural'
            },
            'hinglish': {
                'man': 'en-IN-PrabhatNeural',
                'woman': 'en-IN-NeerjaNeural',
                'child': 'en-IN-NeerjaNeural',
                'elderly_man': 'en-IN-PrabhatNeural',
                'elderly_woman': 'en-IN-NeerjaNeural',
                'male': 'en-IN-PrabhatNeural',
                'female': 'en-IN-NeerjaNeural',
                'default': 'en-IN-NeerjaNeural'
            },
            'bn': {
                'man': 'bn-IN-BashkarNeural',
                'woman': 'bn-IN-TanishaaNeural',
                'child': 'bn-IN-TanishaaNeural',
                'elderly_man': 'bn-IN-BashkarNeural',
                'elderly_woman': 'bn-IN-TanishaaNeural',
                'male': 'bn-IN-BashkarNeural',
                'female': 'bn-IN-TanishaaNeural',
                'default': 'bn-IN-TanishaaNeural'
            },
            'ta': {
                'man': 'ta-IN-ValluvarNeural',
                'woman': 'ta-IN-PallaviNeural',
                'child': 'ta-IN-PallaviNeural',
                'elderly_man': 'ta-IN-ValluvarNeural',
                'elderly_woman': 'ta-IN-PallaviNeural',
                'male': 'ta-IN-ValluvarNeural',
                'female': 'ta-IN-PallaviNeural',
                'default': 'ta-IN-PallaviNeural'
            },
            'te': {
                'man': 'te-IN-MohanNeural',
                'woman': 'te-IN-ShrutiNeural',
                'child': 'te-IN-ShrutiNeural',
                'elderly_man': 'te-IN-MohanNeural',
                'elderly_woman': 'te-IN-ShrutiNeural',
                'male': 'te-IN-MohanNeural',
                'female': 'te-IN-ShrutiNeural',
                'default': 'te-IN-ShrutiNeural'
            },
            'gu': {
                'man': 'gu-IN-NiranjanNeural',
                'woman': 'gu-IN-DhwaniNeural',
                'child': 'gu-IN-DhwaniNeural',
                'elderly_man': 'gu-IN-NiranjanNeural',
                'elderly_woman': 'gu-IN-DhwaniNeural',
                'male': 'gu-IN-NiranjanNeural',
                'female': 'gu-IN-DhwaniNeural',
                'default': 'gu-IN-DhwaniNeural'
            },
            'kn': {
                'man': 'kn-IN-GaganNeural',
                'woman': 'kn-IN-SapnaNeural',
                'child': 'kn-IN-SapnaNeural',
                'elderly_man': 'kn-IN-GaganNeural',
                'elderly_woman': 'kn-IN-SapnaNeural',
                'male': 'kn-IN-GaganNeural',
                'female': 'kn-IN-SapnaNeural',
                'default': 'kn-IN-SapnaNeural'
            },
            'ml': {
                'man': 'ml-IN-MidhunNeural',
                'woman': 'ml-IN-SobhanaNeural',
                'child': 'ml-IN-SobhanaNeural',
                'elderly_man': 'ml-IN-MidhunNeural',
                'elderly_woman': 'ml-IN-SobhanaNeural',
                'male': 'ml-IN-MidhunNeural',
                'female': 'ml-IN-SobhanaNeural',
                'default': 'ml-IN-SobhanaNeural'
            },
            'mr': {
                'man': 'mr-IN-ManoharNeural',
                'woman': 'mr-IN-AarohiNeural',
                'child': 'mr-IN-AarohiNeural',
                'elderly_man': 'mr-IN-ManoharNeural',
                'elderly_woman': 'mr-IN-AarohiNeural',
                'male': 'mr-IN-ManoharNeural',
                'female': 'mr-IN-AarohiNeural',
                'default': 'mr-IN-AarohiNeural'
            },
            'pa': {
                'man': 'pa-IN-GianNeural',
                'woman': 'pa-IN-MahiNeural',
                'child': 'pa-IN-MahiNeural',
                'elderly_man': 'pa-IN-GianNeural',
                'elderly_woman': 'pa-IN-MahiNeural',
                'male': 'pa-IN-GianNeural',
                'female': 'pa-IN-MahiNeural',
                'default': 'pa-IN-MahiNeural'
            },
            'ur': {
                'man': 'ur-IN-SalmanNeural',
                'woman': 'ur-IN-GulNeural',
                'child': 'ur-IN-GulNeural',
                'elderly_man': 'ur-IN-SalmanNeural',
                'elderly_woman': 'ur-IN-GulNeural',
                'male': 'ur-IN-SalmanNeural',
                'female': 'ur-IN-GulNeural',
                'default': 'ur-IN-GulNeural'
            },
            'as': {
                'man': 'as-IN-BiswajitNeural',
                'woman': 'as-IN-PriyomNeural',
                'child': 'as-IN-PriyomNeural',
                'elderly_man': 'as-IN-BiswajitNeural',
                'elderly_woman': 'as-IN-PriyomNeural',
                'male': 'as-IN-BiswajitNeural',
                'female': 'as-IN-PriyomNeural',
                'default': 'as-IN-PriyomNeural'
            },
            'or': {
                'man': 'or-IN-SubhasishNeural',
                'woman': 'or-IN-SukanyaNeural',
                'child': 'or-IN-SukanyaNeural',
                'elderly_man': 'or-IN-SubhasishNeural',
                'elderly_woman': 'or-IN-SukanyaNeural',
                'male': 'or-IN-SubhasishNeural',
                'female': 'or-IN-SukanyaNeural',
                'default': 'or-IN-SukanyaNeural'
            }
        }
        
        # Language names for display
        self.language_names = {
            'en': 'English',
            'hi': 'Hindi (हिंदी)',
            'hinglish': 'Hinglish',
            'bn': 'Bengali (বাংলা)',
            'ta': 'Tamil (தமிழ்)',
            'te': 'Telugu (తెలుగు)',
            'gu': 'Gujarati (ગુજરાતી)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'mr': 'Marathi (मराठी)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)',
            'ur': 'Urdu (اردو)',
            'as': 'Assamese (অসমীয়া)',
            'or': 'Odia (ଓଡ଼ିଆ)'
        }

    def get_access_token(self):
        """Get access token for Azure Speech Services"""
        if not self.subscription_key:
            raise Exception("Azure Speech subscription key not configured")
            
        token_url = f"https://{self.region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        
        response = requests.post(token_url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to get access token: {response.status_code}")

    def create_ssml(self, text, language='en', voice_gender='default', speech_rate='medium', pitch='medium'):
        """Create enhanced SSML with voice-specific adjustments"""
        
        # Get voice name
        voice_name = self.voice_mapping.get(language, {}).get(voice_gender, 
                     self.voice_mapping.get(language, {}).get('default', 'en-US-AriaNeural'))
        
        # Enhanced rate mapping
        rate_mapping = {
            'x-slow': '-50%',
            'slow': '-25%',
            'medium': '0%',
            'fast': '+25%',
            'x-fast': '+50%'
        }
        
        # Enhanced pitch mapping with voice-specific adjustments
        pitch_mapping = {
            'x-low': '-30%',
            'low': '-15%',
            'medium': '0%',
            'high': '+15%',
            'x-high': '+30%'
        }
        
        # Voice-specific adjustments
        if voice_gender == 'child':
            # Higher pitch and slightly faster rate for child voice
            base_pitch = '+20%'
            base_rate = '+10%'
        elif voice_gender == 'elderly_man' or voice_gender == 'elderly_woman':
            # Slightly lower pitch and slower rate for elderly voices
            base_pitch = '-10%'
            base_rate = '-15%'
        elif voice_gender == 'man':
            # Slightly lower pitch for masculine voice
            base_pitch = '-5%'
            base_rate = '0%'
        else:
            # Default adjustments
            base_pitch = '0%'
            base_rate = '0%'
        
        # Combine base adjustments with user preferences
        rate = rate_mapping.get(speech_rate, '0%')
        pitch_value = pitch_mapping.get(pitch, '0%')
        
        # Handle special characters in text
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Enhanced SSML with voice-specific styling
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
            <voice name="{voice_name}">
                <prosody rate="{rate}" pitch="{pitch_value}">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        
        return ssml.strip()

    def detect_and_translate_text(self, text, target_language):
        """Detect source language and translate if needed"""
        try:
            from googletrans import Translator
            from langdetect import detect
            
            # Detect source language
            detected_lang = detect(text)
            current_app.logger.info(f"Detected language: {detected_lang}, Target: {target_language}")
            
            # Language code mapping
            lang_mapping = {
                'hi': 'hi', 'en': 'en', 'bn': 'bn', 'ta': 'ta', 'te': 'te',
                'gu': 'gu', 'kn': 'kn', 'ml': 'ml', 'mr': 'mr', 'pa': 'pa', 'ur': 'ur'
            }
            
            # If source and target are the same, no translation needed
            if detected_lang == target_language or detected_lang == lang_mapping.get(target_language):
                return {
                    'translated_text': text,
                    'source_language': detected_lang,
                    'target_language': target_language,
                    'translation_needed': False
                }
            
            # Translate text
            translator = Translator()
            
            # Handle special case for Hinglish
            if target_language == 'hinglish':
                # For Hinglish, translate to Hindi first, then romanize
                if detected_lang != 'hi':
                    translated = translator.translate(text, src=detected_lang, dest='hi')
                    translated_text = translated.text
                else:
                    translated_text = text
                    
                # Add some English words for Hinglish feel (basic implementation)
                hinglish_text = self.make_hinglish(translated_text)
                
                return {
                    'translated_text': hinglish_text,
                    'source_language': detected_lang,
                    'target_language': target_language,
                    'translation_needed': True
                }
            else:
                # Direct translation
                target_code = lang_mapping.get(target_language, target_language)
                translated = translator.translate(text, src=detected_lang, dest=target_code)
                
                return {
                    'translated_text': translated.text,
                    'source_language': detected_lang,
                    'target_language': target_language,
                    'translation_needed': True
                }
                
        except Exception as e:
            current_app.logger.error(f"Translation error: {e}")
            # Return original text if translation fails
            return {
                'translated_text': text,
                'source_language': 'unknown',
                'target_language': target_language,
                'translation_needed': False,
                'error': str(e)
            }

    def make_hinglish(self, hindi_text):
        """Convert Hindi text to Hinglish (basic implementation)"""
        # This is a basic implementation - can be enhanced with better transliteration
        try:
            from indic_transliteration import sanscript
            # Transliterate Hindi to Roman
            romanized = sanscript.transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS)
            return romanized
        except:
            # Fallback: return original text
            return hindi_text

    def synthesize_speech(self, text, language='en', voice_gender='default', 
                         speech_rate='medium', pitch='medium', audio_format='mp3', auto_translate=True):
        """
        Convert text to speech with auto-translation support
        
        Args:
            text: Text to convert
            language: Target language code
            voice_gender: 'man', 'woman', 'child', 'elderly_man', 'elderly_woman', 'male', 'female', 'default'
            speech_rate: 'x-slow', 'slow', 'medium', 'fast', 'x-fast'
            pitch: 'x-low', 'low', 'medium', 'high', 'x-high'
            audio_format: 'mp3', 'wav', 'ogg'
            auto_translate: Whether to auto-translate text to target language
            
        Returns:
            dict: {"status": "success", "audio_data": "data:audio/mp3;base64,..."}
        """
        try:
            # Validate inputs
            if not text or not text.strip():
                return {"status": "error", "message": "No text provided"}
                
            if len(text) > 5000:
                return {"status": "error", "message": "Text too long (max 5000 characters)"}
            
            # Auto-translate if needed
            translation_info = None
            final_text = text
            
            if auto_translate:
                translation_result = self.detect_and_translate_text(text, language)
                final_text = translation_result['translated_text']
                translation_info = translation_result
                
                current_app.logger.info(f"Translation: {translation_result['source_language']} -> {language}")
                if translation_result.get('translation_needed'):
                    current_app.logger.info(f"Translated: '{text[:50]}...' -> '{final_text[:50]}...'")
            
            # Get access token
            access_token = self.get_access_token()
            
            # Create SSML with final text
            ssml = self.create_ssml(final_text, language, voice_gender, speech_rate, pitch)
            
            # Set audio format
            format_mapping = {
                'mp3': 'audio-24khz-48kbitrate-mono-mp3',
                'wav': 'riff-24khz-16bit-mono-pcm',
                'ogg': 'ogg-24khz-16bit-mono-opus'
            }
            
            output_format = format_mapping.get(audio_format, 'audio-24khz-48kbitrate-mono-mp3')
            
            # Make TTS request
            tts_url = f"{self.base_url}cognitiveservices/v1"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': output_format,
                'User-Agent': 'VediSpeak-TTS'
            }
            
            response = requests.post(tts_url, headers=headers, data=ssml.encode('utf-8'))
            
            if response.status_code == 200:
                # Convert to base64
                audio_content = response.content
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                
                # Create data URL
                mime_type = f"audio/{audio_format}"
                audio_data_url = f"data:{mime_type};base64,{audio_base64}"
                
                result = {
                    "status": "success", 
                    "audio_data": audio_data_url,
                    "voice_name": self.voice_mapping.get(language, {}).get(voice_gender, 'default'),
                    "voice_type": voice_gender,
                    "language": self.language_names.get(language, language),
                    "duration": len(final_text) * 0.1,  # Rough estimate
                    "format": audio_format,
                    "original_text": text,
                    "final_text": final_text
                }
                
                # Add translation info if translation occurred
                if translation_info:
                    result["translation"] = translation_info
                    
                return result
            else:
                error_msg = f"Azure TTS API error: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text}"
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            current_app.logger.error(f"Azure TTS error: {e}")
            return {"status": "error", "message": f"TTS conversion failed: {str(e)}"}

    def get_available_voices(self):
        """Get list of available voices for each language"""
        try:
            access_token = self.get_access_token()
            voices_url = f"{self.base_url}cognitiveservices/voices/list"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(voices_url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            current_app.logger.error(f"Failed to get voices: {e}")
            return []

    def get_supported_languages(self):
        """Get list of supported languages"""
        return {
            'languages': self.language_names,
            'voice_options': {
                'genders': ['default', 'male', 'female'],
                'rates': ['x-slow', 'slow', 'medium', 'fast', 'x-fast'],
                'pitches': ['x-low', 'low', 'medium', 'high', 'x-high'],
                'formats': ['mp3', 'wav', 'ogg']
            }
        }

# Global instance
azure_tts_service = AzureTTSService()

def azure_text_to_speech_service(text, lang='en', voice_gender='default', 
                                speech_rate='medium', pitch='medium', audio_format='mp3', auto_translate=True):
    """
    Enhanced wrapper function for Azure TTS service with auto-translation
    """
    return azure_tts_service.synthesize_speech(
        text=text,
        language=lang,
        voice_gender=voice_gender,
        speech_rate=speech_rate,
        pitch=pitch,
        audio_format=audio_format,
        auto_translate=auto_translate
    )