"""
ISL (Indian Sign Language) inference service
"""
import io
import base64
import threading
import numpy as np
from PIL import Image
from flask import current_app
from collections import deque

class ISLService:
    """Service for ISL gesture recognition"""
    
    def __init__(self):
        self.model = None
        self.lock = threading.Lock()
        self.smoothing_queue = deque(maxlen=5)
        self.classes = []
        self.infer_frame = None
        self.load_model_func = None
        self._infer_imported = False
    
    def _import_infer_module(self):
        """Dynamically import infer module"""
        if self._infer_imported:
            return
            
        try:
            import sys
            import os
            
            # Add backend/ml to path
            ml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml')
            if ml_path not in sys.path:
                sys.path.insert(0, ml_path)
            
            import infer as _infer_mod
            
            self.infer_frame = getattr(_infer_mod, "infer_frame", None)
            self.classes = getattr(_infer_mod, "classes", [])
            self.smoothing_queue = getattr(_infer_mod, "smoothing_queue", self.smoothing_queue)
            self.load_model_func = getattr(_infer_mod, "load_model", None)
            self._infer_imported = True
            
            if current_app:
                current_app.logger.info("ISL infer module loaded successfully")
        except Exception as e:
            if current_app:
                current_app.logger.warning(f"ISL infer module import failed: {e}")
            self.infer_frame = None
            self.load_model_func = None
    
    def get_model(self):
        """Lazy-load the ISL model"""
        # Import infer module if not already done
        if not self._infer_imported:
            self._import_infer_module()
            
        if self.model is not None:
            return self.model
        
        with self.lock:
            if self.model is not None:
                return self.model
            
            if not self.load_model_func:
                current_app.logger.error("ISL load_model function not available")
                return None
            
            try:
                model_path = current_app.config.get("MODEL_PATH", "checkpoints/best.pth")
                self.model = self.load_model_func(model_path)
                
                if self.model is None:
                    current_app.logger.warning(f"Model loading returned None: {model_path}")
                else:
                    current_app.logger.info(f"ISL model loaded from {model_path}")
                
                return self.model
            except Exception as e:
                current_app.logger.error(f"Failed to load ISL model: {e}")
                return None
    
    def predict(self, image_data):
        """
        Predict ISL gesture from base64 image
        
        Args:
            image_data: Base64 encoded image
        
        Returns:
            dict: {"status": "success", "prediction": "A", "confidence": 0.95}
        """
        try:
            if not image_data:
                return {"status": "error", "message": "No image data provided"}
            
            model = self.get_model()
            if model is None:
                return {"status": "error", "message": "ISL model not loaded"}
            
            if not self.infer_frame:
                return {"status": "error", "message": "Inference function not available"}
            
            # Decode base64 image
            header, encoded = image_data.split(",", 1)
            img = Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGB")
            frame = np.array(img)[:, :, ::-1]  # RGB -> BGR for OpenCV
            
            # Run inference
            idx, conf = self.infer_frame(model, frame, self.smoothing_queue)
            
            if idx is None:
                return {"status": "error", "message": "Inference failed"}
            
            # Get prediction label
            pred = self.classes[idx] if idx < len(self.classes) else str(idx)
            
            return {
                "status": "success",
                "prediction": pred,
                "confidence": round(float(conf), 3)
            }
        
        except Exception as e:
            current_app.logger.error(f"ISL prediction error: {e}")
            return {"status": "error", "message": "Prediction failed"}

# Global ISL service instance (lazy initialization)
isl_service = None

def get_isl_service():
    """Get or create ISL service instance"""
    global isl_service
    if isl_service is None:
        isl_service = ISLService()
    return isl_service
