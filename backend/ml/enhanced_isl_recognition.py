"""
Enhanced ISL Recognition System with Improved Accuracy and Continuity
- Advanced model architecture with attention mechanisms
- Letter-to-word-to-sentence formation with context awareness
- Improved temporal smoothing and prediction stability
- Enhanced training with data augmentation and regularization
"""

import os
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import base64
import json
import re
from datetime import datetime
from collections import deque, Counter
from PIL import Image
from torchvision import transforms
from threading import Lock
import difflib

# Enhanced Configuration for Better Accuracy
IMG_SIZE = 256  # Must match training size (256x256)
SMOOTHING_WINDOW = 7  # Increased for better stability
STABLE_THRESHOLD = 4  # Slightly higher for more reliable predictions
CONFIDENCE_THRESHOLD = 0.50  # Lowered for better responsiveness
WORD_CONFIDENCE_THRESHOLD = 0.40  # Lowered for better word formation
MIN_CONFIDENCE_THRESHOLD = 0.20  # Much lower for better detection sensitivity

# Device detection - use CPU for stability
def get_device():
    """Detect and return the best available device"""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"[Enhanced ISL] Using CUDA GPU: {device}")
        return device
    
    # DirectML can be unstable, use CPU for now
    device = torch.device("cpu")
    print(f"[Enhanced ISL] Using CPU device for stability")
    return device

DEVICE = get_device()

# Classes (0-9 + A-Z)
CLASSES = [str(i) for i in range(10)] + [chr(ord('A') + i) for i in range(26)]
NUM_CLASSES = len(CLASSES)

# Enhanced transforms with more augmentation
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomRotation(15),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
    transforms.RandomHorizontalFlip(p=0.3),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    transforms.RandomErasing(p=0.2, scale=(0.02, 0.1))
])

# Enhanced inference transform for better accuracy
inference_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE), interpolation=transforms.InterpolationMode.BILINEAR),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Disabled enhancement for maximum performance
def enhance_hand_region_simple(image):
    """Return image without enhancement for maximum speed"""
    return image

# Common English words for context-aware correction
COMMON_WORDS = {
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR',
    'HAD', 'BY', 'WORD', 'WHAT', 'SAID', 'EACH', 'WHICH', 'SHE', 'DO', 'HOW', 'THEIR', 'IF',
    'WILL', 'UP', 'OTHER', 'ABOUT', 'OUT', 'MANY', 'THEN', 'THEM', 'THESE', 'SO', 'SOME',
    'WOULD', 'MAKE', 'LIKE', 'INTO', 'HIM', 'HAS', 'TWO', 'MORE', 'GO', 'NO', 'WAY', 'COULD',
    'MY', 'THAN', 'FIRST', 'BEEN', 'CALL', 'WHO', 'ITS', 'NOW', 'FIND', 'LONG', 'DOWN', 'DAY',
    'DID', 'GET', 'COME', 'MADE', 'MAY', 'PART', 'OVER', 'NEW', 'SOUND', 'TAKE', 'ONLY', 'LITTLE',
    'WORK', 'KNOW', 'PLACE', 'YEAR', 'LIVE', 'ME', 'BACK', 'GIVE', 'MOST', 'VERY', 'AFTER', 'THING',
    'JUST', 'NAME', 'GOOD', 'SENTENCE', 'MAN', 'THINK', 'SAY', 'GREAT', 'WHERE', 'HELP', 'THROUGH',
    'MUCH', 'BEFORE', 'LINE', 'RIGHT', 'TOO', 'MEAN', 'OLD', 'ANY', 'SAME', 'TELL', 'BOY', 'FOLLOW',
    'CAME', 'WANT', 'SHOW', 'ALSO', 'AROUND', 'FORM', 'THREE', 'SMALL', 'SET', 'PUT', 'END', 'WHY',
    'AGAIN', 'TURN', 'HERE', 'OFF', 'WENT', 'OLD', 'NUMBER', 'GREAT', 'TELL', 'MEN', 'SAY', 'SMALL',
    'EVERY', 'FOUND', 'STILL', 'BETWEEN', 'MANE', 'SHOULD', 'HOME', 'BIG', 'GIVE', 'AIR', 'LINE',
    'SET', 'OWN', 'UNDER', 'READ', 'LAST', 'NEVER', 'US', 'LEFT', 'END', 'ALONG', 'WHILE', 'MIGHT',
    'NEXT', 'SOUND', 'BELOW', 'SAW', 'SOMETHING', 'THOUGHT', 'BOTH', 'FEW', 'THOSE', 'ALWAYS',
    'LOOKED', 'SHOW', 'LARGE', 'OFTEN', 'TOGETHER', 'ASKED', 'HOUSE', 'DONT', 'WORLD', 'GOING',
    'WANT', 'SCHOOL', 'IMPORTANT', 'UNTIL', 'FORM', 'FOOD', 'KEEP', 'CHILDREN', 'FEET', 'LAND',
    'SIDE', 'WITHOUT', 'BOY', 'ONCE', 'ANIMAL', 'LIFE', 'ENOUGH', 'TOOK', 'SOMETIMES', 'FOUR',
    'HEAD', 'ABOVE', 'KIND', 'BEGAN', 'ALMOST', 'LIVE', 'PAGE', 'GOT', 'EARTH', 'NEED', 'FAR',
    'HAND', 'HIGH', 'YEAR', 'MOTHER', 'LIGHT', 'COUNTRY', 'FATHER', 'LET', 'NIGHT', 'PICTURE',
    'BEING', 'STUDY', 'SECOND', 'SOON', 'STORY', 'SINCE', 'WHITE', 'EVER', 'PAPER', 'HARD',
    'NEAR', 'SENTENCE', 'BETTER', 'BEST', 'ACROSS', 'DURING', 'TODAY', 'HOWEVER', 'SURE', 'KNEW',
    'ITS', 'TRYING', 'TOLD', 'YOUNG', 'SUN', 'THING', 'WHOLE', 'HEAR', 'EXAMPLE', 'HEARD',
    'SEVERAL', 'CHANGE', 'ANSWER', 'ROOM', 'SEA', 'AGAINST', 'TOP', 'TURNED', 'LEARN', 'POINT',
    'CITY', 'PLAY', 'TOWARD', 'FIVE', 'HIMSELF', 'USUALLY', 'MONEY', 'SEEN', 'DIDNT', 'CAR',
    'MORNING', 'IM', 'BODY', 'UPON', 'FAMILY', 'LATER', 'TURN', 'MOVE', 'FACE', 'DOOR', 'CUT',
    'DONE', 'GROUP', 'TRUE', 'LEAVE', 'YOURE', 'IDEA', 'FISH', 'MOUNTAIN', 'NORTH', 'ONCE',
    'BASE', 'HEAR', 'HORSE', 'MAIN', 'SEEMS', 'TOGETHER', 'NEXT', 'WHITE', 'CHILDREN', 'OPEN',
    'EXAMPLE', 'BEGIN', 'LIFE', 'ALWAYS', 'THOSE', 'BOTH', 'PAPER', 'TOGETHER', 'GOT', 'GROUP',
    'OFTEN', 'RUN', 'IMPORTANT', 'UNTIL', 'CHILDREN', 'SIDE', 'FEET', 'CAR', 'MILE', 'NIGHT',
    'WALK', 'TOOK', 'RIVER', 'FOUR', 'CARRY', 'STATE', 'ONCE', 'BOOK', 'HEAR', 'STOP', 'WITHOUT',
    'SECOND', 'LATER', 'MISS', 'IDEA', 'ENOUGH', 'EAT', 'FACE', 'WATCH', 'FAR', 'INDIAN', 'REAL',
    'ALMOST', 'LET', 'ABOVE', 'GIRL', 'SOMETIMES', 'MOUNTAIN', 'CUT', 'YOUNG', 'TALK', 'SOON',
    'LIST', 'SONG', 'BEING', 'LEAVE', 'FAMILY', 'ITS'
}


class AttentionModule(nn.Module):
    """Combined channel and spatial attention module - matches training checkpoint"""
    
    def __init__(self, in_channels):
        super(AttentionModule, self).__init__()
        
        # Channel attention
        self.channel_attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, in_channels // 16, 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // 16, in_channels, 1),
            nn.Sigmoid()
        )
        
        # Spatial attention
        self.spatial_attention = nn.Sequential(
            nn.Conv2d(2, 1, kernel_size=7, padding=3),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        # Channel attention
        ca = self.channel_attention(x)
        x = x * ca
        
        # Spatial attention
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        sa_input = torch.cat([avg_out, max_out], dim=1)
        sa = self.spatial_attention(sa_input)
        x = x * sa
        
        return x


class EnhancedISLModel(nn.Module):
    """Enhanced ISL model with attention and improved architecture - matches training checkpoint"""
    
    def __init__(self, num_classes=NUM_CLASSES, dropout_rate=0.3):
        super(EnhancedISLModel, self).__init__()
        
        # Use EfficientNet-B0 as backbone (matches checkpoint with 1280 features)
        try:
            import timm
            # Create model with global pooling but no classifier to get feature maps before pooling
            self.backbone = timm.create_model('efficientnet_b0', pretrained=False, num_classes=0, global_pool='')
            backbone_features = 1280  # EfficientNet-B0 features
        except ImportError:
            # Fallback to ResNet
            from torchvision.models import resnet50
            backbone = resnet50(pretrained=False)
            self.backbone = nn.Sequential(*list(backbone.children())[:-2])
            backbone_features = 2048
        
        # Attention module
        self.attention = AttentionModule(backbone_features)
        
        # Global average pooling
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        
        # Enhanced classifier with dropout and batch norm
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(backbone_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate / 2),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate / 4),
            nn.Linear(256, num_classes)
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize classifier weights"""
        for m in self.classifier.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        # Extract features
        features = self.backbone(x)
        
        # Apply attention
        features = self.attention(features)
        
        # Global pooling
        features = self.global_pool(features)
        features = features.view(features.size(0), -1)
        
        # Classification
        output = self.classifier(features)
        
        return output


class TemporalSmoother:
    """Advanced temporal smoothing with confidence weighting"""
    
    def __init__(self, window_size=SMOOTHING_WINDOW, confidence_weight=0.3):
        self.window_size = window_size
        self.confidence_weight = confidence_weight
        self.predictions = deque(maxlen=window_size)
        self.confidences = deque(maxlen=window_size)
    
    def add_prediction(self, prediction, confidence):
        """Add a new prediction with confidence"""
        self.predictions.append(prediction)
        self.confidences.append(confidence)
    
    def get_smoothed_prediction(self):
        """Get smoothed prediction using confidence weighting"""
        if not self.predictions:
            return None, 0.0
        
        # Count predictions weighted by confidence
        weighted_counts = Counter()
        total_weight = 0
        
        for pred, conf in zip(self.predictions, self.confidences):
            weight = conf ** self.confidence_weight
            weighted_counts[pred] += weight
            total_weight += weight
        
        if total_weight == 0:
            return None, 0.0
        
        # Get most likely prediction
        best_pred = weighted_counts.most_common(1)[0][0]
        best_confidence = weighted_counts[best_pred] / total_weight
        
        return best_pred, best_confidence
    
    def clear(self):
        """Clear the smoothing buffer"""
        self.predictions.clear()
        self.confidences.clear()


class WordFormationEngine:
    """Intelligent word formation with enhanced spell checking and auto-correction"""
    
    def __init__(self, max_word_length=15):
        self.max_word_length = max_word_length
        self.current_word = ""
        self.word_confidence_scores = []
        self.formed_words = []
        self.last_letter_time = None
        self.word_timeout = 3.0  # seconds
        
        # Enhanced spell checking features
        self.auto_correct_enabled = True
        self.suggestion_threshold = 0.5  # Minimum similarity for suggestions
        self.auto_correct_threshold = 0.8  # Auto-correct if similarity is above this
        self.real_time_suggestions = []
        
        # Common letter substitutions for ISL recognition errors
        self.common_substitutions = {
            'O': ['0', 'Q'],  # O often confused with 0 and Q
            '0': ['O', 'Q'],  # 0 often confused with O and Q
            'I': ['1', 'L'],  # I often confused with 1 and L
            '1': ['I', 'L'],  # 1 often confused with I and L
            'S': ['5'],       # S often confused with 5
            '5': ['S'],       # 5 often confused with S
            'B': ['8'],       # B often confused with 8
            '8': ['B'],       # 8 often confused with B
            'G': ['6'],       # G often confused with 6
            '6': ['G'],       # 6 often confused with G
            'Z': ['2'],       # Z often confused with 2
            '2': ['Z'],       # 2 often confused with Z
        }
        
        # Phonetic patterns for better matching
        self.phonetic_patterns = {
            'PH': 'F', 'GH': 'F', 'CK': 'K', 'QU': 'KW',
            'TH': 'T', 'SH': 'S', 'CH': 'C', 'WH': 'W'
        }
    
    def add_letter(self, letter, confidence):
        """Add a letter to current word formation with real-time spell checking"""
        current_time = datetime.now()
        
        # Check for word timeout
        if (self.last_letter_time and 
            (current_time - self.last_letter_time).total_seconds() > self.word_timeout):
            self._finalize_current_word()
        
        # Add letter to current word
        if len(self.current_word) < self.max_word_length:
            self.current_word += letter
            self.word_confidence_scores.append(confidence)
            self.last_letter_time = current_time
            
            # Update real-time suggestions
            self._update_real_time_suggestions()
    
    def _finalize_current_word(self):
        """Finalize current word and add to formed words"""
        if self.current_word:
            # Calculate average confidence for the word
            avg_confidence = np.mean(self.word_confidence_scores) if self.word_confidence_scores else 0
            
            # Apply word correction
            corrected_word = self._correct_word(self.current_word)
            
            self.formed_words.append({
                'word': corrected_word,
                'original': self.current_word,
                'confidence': avg_confidence,
                'timestamp': datetime.now().isoformat()
            })
            
            # Reset for next word
            self.current_word = ""
            self.word_confidence_scores = []
    
    def _correct_word(self, word):
        """Apply enhanced intelligent word correction with multiple strategies"""
        if not word:
            return word
            
        word_upper = word.upper()
        
        # Strategy 1: Direct match
        if word_upper in COMMON_WORDS:
            return word_upper
        
        # Strategy 2: Try common ISL recognition substitutions
        corrected_word = self._apply_substitutions(word_upper)
        if corrected_word != word_upper and corrected_word in COMMON_WORDS:
            return corrected_word
        
        # Strategy 3: Phonetic matching
        phonetic_word = self._apply_phonetic_patterns(word_upper)
        if phonetic_word != word_upper and phonetic_word in COMMON_WORDS:
            return phonetic_word
        
        # Strategy 4: Advanced fuzzy matching with multiple algorithms
        best_match = self._advanced_fuzzy_match(word_upper)
        if best_match:
            return best_match
        
        # Strategy 5: Partial word matching (for incomplete words)
        partial_matches = self._find_partial_matches(word_upper)
        if partial_matches:
            return partial_matches[0]  # Return best partial match
        
        # If no correction found, return original
        return word_upper
    
    def _apply_substitutions(self, word):
        """Apply common ISL recognition error substitutions"""
        corrected = word
        for original, substitutes in self.common_substitutions.items():
            if original in corrected:
                for substitute in substitutes:
                    test_word = corrected.replace(original, substitute)
                    if test_word in COMMON_WORDS:
                        return test_word
        return corrected
    
    def _apply_phonetic_patterns(self, word):
        """Apply phonetic pattern corrections"""
        corrected = word
        for pattern, replacement in self.phonetic_patterns.items():
            corrected = corrected.replace(pattern, replacement)
        return corrected
    
    def _advanced_fuzzy_match(self, word):
        """Advanced fuzzy matching using multiple similarity algorithms"""
        best_match = None
        best_score = 0
        
        for candidate in COMMON_WORDS:
            # Calculate multiple similarity scores
            ratio_score = difflib.SequenceMatcher(None, word, candidate).ratio()
            
            # Jaro-Winkler-like scoring (prioritize prefix matches)
            prefix_bonus = 0
            if len(word) >= 2 and len(candidate) >= 2:
                if word[:2] == candidate[:2]:
                    prefix_bonus = 0.1
                elif word[0] == candidate[0]:
                    prefix_bonus = 0.05
            
            # Length penalty for very different lengths
            length_penalty = abs(len(word) - len(candidate)) * 0.05
            
            # Final score
            final_score = ratio_score + prefix_bonus - length_penalty
            
            if final_score > best_score and final_score >= self.suggestion_threshold:
                best_score = final_score
                best_match = candidate
        
        # Auto-correct if score is high enough
        if best_score >= self.auto_correct_threshold:
            return best_match
        
        return None
    
    def _find_partial_matches(self, word):
        """Find words that start with the current partial word"""
        if len(word) < 2:
            return []
        
        matches = []
        for candidate in COMMON_WORDS:
            if candidate.startswith(word):
                matches.append(candidate)
        
        # Sort by length (shorter words first, more likely to be intended)
        matches.sort(key=len)
        return matches[:3]  # Return top 3 matches
    
    def force_word_completion(self):
        """Force completion of current word"""
        self._finalize_current_word()
    
    def get_current_word(self):
        """Get current word being formed"""
        return self.current_word
    
    def get_formed_words(self):
        """Get all formed words"""
        return self.formed_words
    
    def get_sentence(self):
        """Get complete sentence from formed words"""
        if not self.formed_words:
            return ""
        
        words = [word_info['word'] for word_info in self.formed_words]
        return ' '.join(words)
    
    def _update_real_time_suggestions(self):
        """Update real-time word suggestions as user types"""
        if len(self.current_word) < 2:
            self.real_time_suggestions = []
            return
        
        suggestions = []
        word_upper = self.current_word.upper()
        
        # Find exact prefix matches
        exact_matches = []
        for candidate in COMMON_WORDS:
            if candidate.startswith(word_upper):
                exact_matches.append(candidate)
        
        # Sort by length and frequency (shorter words first)
        exact_matches.sort(key=lambda x: (len(x), x))
        suggestions.extend(exact_matches[:3])
        
        # If we have fewer than 3 suggestions, add fuzzy matches
        if len(suggestions) < 3:
            fuzzy_matches = []
            for candidate in COMMON_WORDS:
                if not candidate.startswith(word_upper):
                    similarity = difflib.SequenceMatcher(None, word_upper, candidate).ratio()
                    if similarity >= 0.6:  # Lower threshold for suggestions
                        fuzzy_matches.append((candidate, similarity))
            
            # Sort by similarity score
            fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
            suggestions.extend([match[0] for match in fuzzy_matches[:3-len(suggestions)]])
        
        self.real_time_suggestions = suggestions[:5]  # Limit to 5 suggestions
    
    def get_real_time_suggestions(self):
        """Get current real-time word suggestions"""
        return self.real_time_suggestions
    
    def apply_suggestion(self, suggested_word):
        """Apply a suggested word to replace current word"""
        if suggested_word.upper() in COMMON_WORDS:
            self.current_word = suggested_word.upper()
            # Keep the confidence scores but adjust length
            if len(self.word_confidence_scores) > len(self.current_word):
                self.word_confidence_scores = self.word_confidence_scores[:len(self.current_word)]
            elif len(self.word_confidence_scores) < len(self.current_word):
                # Pad with average confidence
                avg_conf = np.mean(self.word_confidence_scores) if self.word_confidence_scores else 0.5
                while len(self.word_confidence_scores) < len(self.current_word):
                    self.word_confidence_scores.append(avg_conf)
            
            self._update_real_time_suggestions()
            return True
        return False
    
    def get_spell_check_info(self):
        """Get comprehensive spell checking information"""
        if not self.current_word:
            return {
                'current_word': '',
                'suggestions': [],
                'is_valid_word': False,
                'confidence': 0,
                'auto_correct_suggestion': None
            }
        
        word_upper = self.current_word.upper()
        is_valid = word_upper in COMMON_WORDS
        avg_confidence = np.mean(self.word_confidence_scores) if self.word_confidence_scores else 0
        
        # Get auto-correct suggestion
        auto_correct = None
        if not is_valid and self.auto_correct_enabled:
            corrected = self._correct_word(word_upper)
            if corrected != word_upper:
                auto_correct = corrected
        
        return {
            'current_word': self.current_word,
            'suggestions': self.real_time_suggestions,
            'is_valid_word': is_valid,
            'confidence': avg_confidence,
            'auto_correct_suggestion': auto_correct,
            'word_length': len(self.current_word),
            'max_length': self.max_word_length
        }
    
    def toggle_auto_correct(self):
        """Toggle auto-correction on/off"""
        self.auto_correct_enabled = not self.auto_correct_enabled
        return self.auto_correct_enabled
    
    def set_suggestion_threshold(self, threshold):
        """Set the similarity threshold for suggestions (0.0 to 1.0)"""
        self.suggestion_threshold = max(0.0, min(1.0, threshold))
    
    def clear(self):
        """Clear all word formation data"""
        self.current_word = ""
        self.word_confidence_scores = []
        self.formed_words = []
        self.last_letter_time = None
        self.real_time_suggestions = []


class EnhancedISLRecognizer:
    """Enhanced ISL Recognition class with improved accuracy and continuity"""
    
    def __init__(self, model_path="checkpoints/best.pth"):
        self.model = None
        self.model_path = model_path
        self.device = DEVICE
        
        # Enhanced components
        self.temporal_smoother = TemporalSmoother()
        self.word_engine = WordFormationEngine()
        
        # Prediction tracking
        self.prediction_history = deque(maxlen=200)
        self.last_stable_letter = None
        self.stable_count = 0
        self.last_prediction_time = None
        
        # Hand detection and state management
        self.mp_hands = None
        self._init_mediapipe()
        
        # Simple activation state
        self.recognition_active = True  # Start active by default
        self.start_sign_detected_count = 0
        self.start_sign_required_count = 3  # Need 3 consecutive "A" detections to start
        self.no_hand_warning_count = 0
        self.no_hand_warning_threshold = 30  # Show warning after 30 frames without hands
        self.last_hand_detected_time = None
        
        # Threading
        self.lock = Lock()
        self.is_running = False
        
        # Performance metrics
        self.frame_count = 0
        self.total_processing_time = 0
        
        # Load model
        self._load_model()
    
    def _init_mediapipe(self):
        """Initialize MediaPipe hands detection with very low thresholds for maximum sensitivity"""
        try:
            import mediapipe as mp
            # Very sensitive MediaPipe configuration for better detection
            self.mp_hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=2,  # Support both hands
                min_detection_confidence=0.3,  # Very low for maximum sensitivity
                min_tracking_confidence=0.3,  # Very low for better tracking
                model_complexity=1  # Higher complexity for better accuracy
            )
            
            self.mp_drawing = mp.solutions.drawing_utils
            print("[Enhanced ISL] MediaPipe initialized (maximum sensitivity, confidence: 0.3)")
        except Exception as e:
            print(f"[Enhanced ISL] MediaPipe init failed: {e}")
            self.mp_hands = None
    
    def _load_model(self):
        """Load the trained model - uses EnhancedISLModel with proper architecture"""
        try:
            model_path = "checkpoints/best.pth"
            if not os.path.exists(model_path):
                print(f"[Enhanced ISL] Model not found at {model_path}")
                return False
            
            print(f"[Enhanced ISL] Loading model from {model_path}")
            
            # Create EnhancedISLModel (matches training architecture)
            self.model = EnhancedISLModel(NUM_CLASSES)
            print(f"[Enhanced ISL] Created EnhancedISLModel")
            
            # Load checkpoint
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if "model_state_dict" in checkpoint:
                    state_dict = checkpoint["model_state_dict"]
                elif "model_state" in checkpoint:
                    state_dict = checkpoint["model_state"]
                elif "state_dict" in checkpoint:
                    state_dict = checkpoint["state_dict"]
                else:
                    state_dict = checkpoint
            else:
                state_dict = checkpoint
            
            # Load state dict
            self.model.load_state_dict(state_dict, strict=True)
            print(f"[Enhanced ISL] Model weights loaded successfully")
            
            # Move to target device
            self.model.to(self.device)
            self.model.eval()
            
            print(f"[Enhanced ISL] Model ready on {self.device}")
            return True
            
        except Exception as e:
            print(f"[Enhanced ISL] Failed to load model: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
            return False
    
    def _both_hands_detection(self, frame):
        """Enhanced hand detection supporting both hands for ISL with improved accuracy"""
        hand_crop, bbox = None, None
        hands_detected = False
        hand_count = 0
        hand_landmarks_list = []
        
        # MediaPipe hand detection
        if self.mp_hands is not None:
            try:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.mp_hands.process(img_rgb)
                h, w = frame.shape[:2]
                
                if results and results.multi_hand_landmarks:
                    hand_count = len(results.multi_hand_landmarks)
                    hands_detected = True
                    self.last_hand_detected_time = datetime.now()
                    self.no_hand_warning_count = 0
                    
                    # Convert MediaPipe landmarks to serializable format
                    for hand_landmarks in results.multi_hand_landmarks:
                        landmarks_data = []
                        for landmark in hand_landmarks.landmark:
                            landmarks_data.append({
                                'x': float(landmark.x),
                                'y': float(landmark.y),
                                'z': float(landmark.z)
                            })
                        hand_landmarks_list.append(landmarks_data)
                    
                    # Collect all hand bounding boxes with improved accuracy
                    all_boxes = []
                    hand_areas = []
                    
                    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        lm = hand_landmarks.landmark
                        xs = [int(l.x * w) for l in lm]
                        ys = [int(l.y * h) for l in lm]
                        
                        # Calculate hand size and area for better region selection
                        hand_width = max(xs) - min(xs)
                        hand_height = max(ys) - min(ys)
                        hand_area = hand_width * hand_height
                        
                        # Enhanced adaptive padding based on hand size and position
                        # Larger padding for smaller hands, smaller padding for larger hands
                        base_pad_ratio = 0.4 if hand_area < 5000 else 0.3
                        pad_x = max(int(hand_width * base_pad_ratio), 40)
                        pad_y = max(int(hand_height * base_pad_ratio), 40)
                        
                        # Ensure minimum size for very small detections
                        min_size = 80
                        if hand_width < min_size:
                            pad_x = max(pad_x, (min_size - hand_width) // 2)
                        if hand_height < min_size:
                            pad_y = max(pad_y, (min_size - hand_height) // 2)
                        
                        x1 = max(min(xs) - pad_x, 0)
                        y1 = max(min(ys) - pad_y, 0)
                        x2 = min(max(xs) + pad_x, w)
                        y2 = min(max(ys) + pad_y, h)
                        
                        # Validate bounding box
                        if x2 > x1 + 20 and y2 > y1 + 20:  # Minimum 20px size
                            all_boxes.append((x1, y1, x2, y2))
                            hand_areas.append(hand_area)
                    
                    if all_boxes:
                        if len(all_boxes) == 1:
                            # Single hand detected
                            bbox = all_boxes[0]
                            hand_crop = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                        else:
                            # Multiple hands - create optimized combined region
                            # Sort hands by area (largest first) for better processing
                            sorted_hands = sorted(zip(all_boxes, hand_areas), key=lambda x: x[1], reverse=True)
                            
                            # Take the two largest hands if more than 2 detected
                            if len(sorted_hands) > 2:
                                sorted_hands = sorted_hands[:2]
                                all_boxes = [box for box, _ in sorted_hands]
                            
                            # Find optimal bounding box that includes both hands
                            min_x = min(box[0] for box in all_boxes)
                            min_y = min(box[1] for box in all_boxes)
                            max_x = max(box[2] for box in all_boxes)
                            max_y = max(box[3] for box in all_boxes)
                            
                            # Calculate distance between hands for adaptive padding
                            hand_distance = max_x - min_x
                            adaptive_pad = min(30, hand_distance // 10)  # Smaller padding for closer hands
                            
                            x1 = max(min_x - adaptive_pad, 0)
                            y1 = max(min_y - adaptive_pad, 0)
                            x2 = min(max_x + adaptive_pad, w)
                            y2 = min(max_y + adaptive_pad, h)
                            
                            bbox = (x1, y1, x2, y2)
                            hand_crop = frame[y1:y2, x1:x2]
                        
                        return hand_crop, bbox, hands_detected, hand_count, hand_landmarks_list
                            
            except Exception as e:
                print(f"[Enhanced ISL] MediaPipe detection error: {e}")
        
        # Update warning counter if no hands detected
        if not hands_detected:
            self.no_hand_warning_count += 1
        
        return hand_crop, bbox, hands_detected, hand_count, hand_landmarks_list
    
    def _predict_single_frame(self, frame):
        """Optimized prediction on single frame for maximum performance"""
        if self.model is None:
            return None, 0.0, None, False, 0, []
        
        start_time = datetime.now()
        
        try:
            # Quick frame validation
            if frame is None or frame.size == 0 or len(frame.shape) != 3:
                return None, 0.0, None, False, 0, []
            
            # Get hand detection (optimized)
            hand_crop, bbox, hands_detected, hand_count, hand_landmarks_list = self._both_hands_detection(frame)
            
            # SINGLE PROCESSING PATH - choose best input source
            input_image = None
            
            if hand_crop is not None and hand_crop.size > 0 and len(hand_crop.shape) == 3:
                # Use hand crop (faster, more accurate)
                try:
                    crop_rgb = cv2.cvtColor(hand_crop, cv2.COLOR_BGR2RGB)
                    input_image = Image.fromarray(crop_rgb, mode='RGB')
                except Exception:
                    input_image = None
            
            # Fallback to full frame if no valid hand crop
            if input_image is None:
                try:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    input_image = Image.fromarray(frame_rgb, mode='RGB')
                except Exception:
                    return None, 0.0, None, False, 0, []
            
            # SINGLE model inference (optimized for speed)
            try:
                img_tensor = inference_transform(input_image).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    output = self.model(img_tensor)
                    probs = F.softmax(output, dim=1).cpu().numpy()[0]
                
            except Exception as e:
                print(f"[Enhanced ISL] Model inference error: {e}")
                return None, 0.0, None, False, 0, []
            
            # Enhanced prediction with confidence boosting
            idx = int(np.argmax(probs))
            raw_confidence = float(probs[idx])
            letter = CLASSES[idx]
            
            # Apply confidence boosting for better accuracy
            sorted_probs = np.sort(probs)[::-1]
            if len(sorted_probs) > 1:
                margin = sorted_probs[0] - sorted_probs[1]
                if margin > 0.2:  # Clear winner
                    confidence = min(raw_confidence * 1.1, 1.0)  # Boost by 10%
                elif margin > 0.1:  # Moderate winner
                    confidence = min(raw_confidence * 1.05, 1.0)  # Boost by 5%
                else:
                    confidence = raw_confidence  # No boost for unclear predictions
            else:
                confidence = raw_confidence
            
            # Apply class-specific confidence adjustments
            if letter.isdigit():
                confidence = min(confidence * 1.05, 1.0)  # Slight boost for numbers
            
            # Common letters that are often confused - be more conservative
            confused_letters = ['M', 'N', 'S', 'T']
            if letter in confused_letters:
                confidence = confidence * 0.95  # Slight penalty for commonly confused letters
            
            # Update performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.frame_count += 1
            self.total_processing_time += processing_time
            
            return letter, confidence, bbox, hands_detected, hand_count, hand_landmarks_list
            
        except Exception as e:
            print(f"[Enhanced ISL] Prediction error: {e}")
            return None, 0.0, None, False, 0, []
    
    def get_enhanced_prediction(self, frame):
        """Get enhanced prediction with temporal smoothing and word formation"""
        current_time = datetime.now()
        
        # Get raw prediction
        letter, confidence, bbox, hands_detected, hand_count, hand_landmarks_list = self._predict_single_frame(frame)
        
        # Generate status messages
        status_messages = []
        warning_level = "info"
        
        if not hands_detected:
            if self.no_hand_warning_count > self.no_hand_warning_threshold:
                status_messages.append("⚠️ No hands detected. Please show both hands to the camera.")
                warning_level = "warning"
            else:
                status_messages.append("👋 Looking for hands...")
        elif hand_count == 1:
            if not self.recognition_active:
                status_messages.append("🅰️ One hand detected. Show sign 'A' with both hands to start")
            else:
                status_messages.append("👋 One hand detected. Some signs may need both hands")
            warning_level = "info"
        elif hand_count >= 2:
            if not self.recognition_active:
                status_messages.append("🅰️ Both hands detected! Show sign 'A' to start recognition")
                warning_level = "info"
            else:
                status_messages.append("🙌 Both hands ready for ISL recognition")
                warning_level = "success"
        else:
            if not self.recognition_active:
                status_messages.append("🅰️ Show sign 'A' to start recognition")
                warning_level = "info"
            else:
                status_messages.append("🤟 Ready for sign recognition")
                warning_level = "success"
        
        # Handle activation with sign "A"
        if letter == 'A' and confidence > CONFIDENCE_THRESHOLD:
            self.start_sign_detected_count += 1
            if self.start_sign_detected_count >= self.start_sign_required_count:
                self.recognition_active = True
                status_messages = ["✅ Recognition activated! Start signing."]
                warning_level = "success"
        elif letter != 'A':
            self.start_sign_detected_count = 0
        
        # Return early if no prediction or very low confidence or not active
        # BUT allow processing even without hands for testing
        if (letter is None or confidence < MIN_CONFIDENCE_THRESHOLD or 
            (not self.recognition_active and letter != 'A')):
            
            # If no hands detected but we have a prediction, still show it for testing
            if letter and confidence >= MIN_CONFIDENCE_THRESHOLD:
                pass  # Continue processing
            else:
                return {
                    'letter': letter,  # Show letter even if confidence is low for debugging
                    'confidence': confidence if confidence else 0,
                    'is_stable': False,
                    'current_text': self.word_engine.get_sentence(),
                    'current_word': self.word_engine.get_current_word(),
                    'bbox': bbox,
                    'hand_detected': hands_detected,
                    'hand_count': hand_count,
                    'both_hands': hand_count >= 2,
                    'hand_landmarks': hand_landmarks_list,
                    'recognition_active': self.recognition_active,
                    'status_messages': status_messages,
                    'warning_level': warning_level,
                    'word_suggestions': [],
                    'avg_processing_time': round(self.total_processing_time / max(self.frame_count, 1), 4)
                }
        
        # Add to temporal smoother
        self.temporal_smoother.add_prediction(letter, confidence)
        
        # Get smoothed prediction
        smoothed_letter, smoothed_confidence = self.temporal_smoother.get_smoothed_prediction()
        
        # Check for stability
        is_stable = False
        if smoothed_letter and smoothed_confidence >= CONFIDENCE_THRESHOLD:
            if smoothed_letter == self.last_stable_letter:
                self.stable_count += 1
            else:
                self.last_stable_letter = smoothed_letter
                self.stable_count = 1
            
            # Check if prediction is stable enough
            if self.stable_count >= STABLE_THRESHOLD:
                is_stable = True
                self.stable_count = 0
                
                # Add to word formation
                self.word_engine.add_letter(smoothed_letter, smoothed_confidence)
                
                # Log prediction
                self.prediction_history.append({
                    'letter': smoothed_letter,
                    'confidence': smoothed_confidence,
                    'timestamp': current_time.isoformat(),
                    'processing_time': self.total_processing_time / max(self.frame_count, 1)
                })
        
        # Get enhanced spell checking information
        current_word = self.word_engine.get_current_word()
        spell_check_info = self.word_engine.get_spell_check_info()
        word_suggestions = spell_check_info['suggestions']
        
        # Get translations if text is available
        current_text = self.word_engine.get_sentence()
        translations = {}
        if current_text and len(current_text.strip()) > 0:
            try:
                from backend.app.services.translation_service import get_translation_service
                translation_service = get_translation_service()
                
                # Translate to Hindi and Roman Hindi
                hindi_result = translation_service.translate_text(current_text, 'hi', 'en')
                roman_result = translation_service.translate_text(current_text, 'hi-rom', 'en')
                
                translations = {
                    'hindi': hindi_result['translated_text'],
                    'roman_hindi': roman_result['translated_text'],
                    'english': current_text
                }
            except Exception as e:
                print(f"[Enhanced ISL] Translation error: {e}")
                translations = {
                    'hindi': current_text,
                    'roman_hindi': current_text,
                    'english': current_text
                }

        return {
            'letter': smoothed_letter,
            'confidence': round(smoothed_confidence, 3) if smoothed_confidence else 0,
            'is_stable': is_stable,
            'current_text': current_text,
            'current_word': current_word,
            'translations': translations,
            'bbox': bbox,
            'hand_detected': hands_detected,
            'hand_count': hand_count,
            'both_hands': hand_count >= 2,
            'hand_landmarks': hand_landmarks_list,
            'recognition_active': self.recognition_active,
            'status_messages': status_messages,
            'warning_level': warning_level,
            'word_suggestions': word_suggestions,
            'spell_check_info': spell_check_info,
            'avg_processing_time': round(self.total_processing_time / max(self.frame_count, 1), 4)
        }
    
    def process_base64_frame(self, base64_data):
        """Process base64 frame with enhanced pipeline"""
        try:
            # Validate input
            if not base64_data:
                return {'error': 'No image data provided'}
            
            # Decode image
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            img_bytes = base64.b64decode(base64_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {'error': 'Failed to decode image - invalid format'}
            
            # Validate decoded frame
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                return {'error': f'Invalid image shape: {frame.shape}'}
            
            if frame.shape[0] < 10 or frame.shape[1] < 10:
                return {'error': f'Image too small: {frame.shape}'}
            
            # Get enhanced prediction
            result = self.get_enhanced_prediction(frame)
            return result
            
        except Exception as e:
            import traceback
            print(f"[Enhanced ISL] process_base64_frame error: {e}")
            traceback.print_exc()
            return {'error': str(e)}
    
    def force_word_completion(self):
        """Force completion of current word"""
        self.word_engine.force_word_completion()
        return {
            'success': True,
            'current_text': self.word_engine.get_sentence(),
            'current_word': self.word_engine.get_current_word()
        }
    
    def clear_text(self):
        """Clear all text and reset state"""
        self.word_engine.clear()
        self.temporal_smoother.clear()
        self.prediction_history.clear()
        self.last_stable_letter = None
        self.stable_count = 0
        
        return {
            'success': True,
            'current_text': '',
            'current_word': ''
        }
    
    def reset_recognition(self):
        """Reset recognition state"""
        self.recognition_active = False
        self.start_sign_detected_count = 0
        self.no_hand_warning_count = 0
        self.last_hand_detected_time = None
        
        return {
            'success': True,
            'message': 'Recognition reset. Show sign "A" to reactivate.'
        }
    
    def backspace(self):
        """Remove last character/word"""
        # If currently forming a word, remove last letter
        if self.word_engine.get_current_word():
            current_word = self.word_engine.get_current_word()
            if len(current_word) > 1:
                self.word_engine.current_word = current_word[:-1]
                self.word_engine.word_confidence_scores = self.word_engine.word_confidence_scores[:-1]
            else:
                self.word_engine.current_word = ""
                self.word_engine.word_confidence_scores = []
        else:
            # Remove last formed word
            if self.word_engine.formed_words:
                self.word_engine.formed_words.pop()
        
        return {
            'success': True,
            'current_text': self.word_engine.get_sentence(),
            'current_word': self.word_engine.get_current_word()
        }
    
    def add_space(self):
        """Add space (complete current word)"""
        self.word_engine.force_word_completion()
        return {
            'success': True,
            'current_text': self.word_engine.get_sentence(),
            'current_word': self.word_engine.get_current_word()
        }
    
    def get_text(self):
        """Get current text state"""
        return {
            'current_text': self.word_engine.get_sentence(),
            'current_word': self.word_engine.get_current_word(),
            'formed_words': self.word_engine.get_formed_words()
        }
    
    def get_model_info(self):
        """Get enhanced model information"""
        return {
            'model_loaded': self.model is not None,
            'model_path': self.model_path,
            'device': str(self.device),
            'num_classes': NUM_CLASSES,
            'classes': CLASSES,
            'mediapipe_available': self.mp_hands is not None,
            'enhanced_features': True,
            'temporal_smoothing': True,
            'word_formation': True,
            'context_awareness': True,
            'both_hands_support': True,
            'max_hands': 2,
            'sign_activation': True,
            'activation_sign': 'A',
            'recognition_active': self.recognition_active,
            'start_sign_progress': f"{self.start_sign_detected_count}/{self.start_sign_required_count}",
            'avg_processing_time': round(self.total_processing_time / max(self.frame_count, 1), 4) if self.frame_count > 0 else 0,
            'frames_processed': self.frame_count
        }


# Global enhanced recognizer instance
_enhanced_recognizer = None
_enhanced_recognizer_lock = Lock()


def get_enhanced_recognizer():
    """Get or create the global enhanced ISL recognizer instance"""
    global _enhanced_recognizer
    with _enhanced_recognizer_lock:
        if _enhanced_recognizer is None:
            _enhanced_recognizer = EnhancedISLRecognizer()
        return _enhanced_recognizer


def reset_enhanced_recognizer():
    """Reset the global enhanced recognizer"""
    global _enhanced_recognizer
    with _enhanced_recognizer_lock:
        _enhanced_recognizer = None


# Backward compatibility - use enhanced recognizer by default
def get_recognizer():
    """Get recognizer (enhanced by default)"""
    return get_enhanced_recognizer()


def reset_recognizer():
    """Reset recognizer (enhanced by default)"""
    return reset_enhanced_recognizer()