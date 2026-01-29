"""
YOLO Detector - Optimized Version
- Uses config file
- Uses utils for shared functions
- Reduced variants (15 → 10)
- Early stopping
- Better organized
"""
import cv2
import numpy as np
import re
from pathlib import Path
from collections import Counter

# Import configs and utils
from config import (
    DetectionConfig, OCRConfig, PreprocessingConfig,
    ValidationConfig, ConfidenceConfig
)
from utils import (
    validate_vietnamese_plate, format_vietnamese_plate,
    clean_text, has_valid_components, calculate_image_quality,
    resize_if_needed, ensure_bgr, clamp
)


class YOLOPlateDetector:
    """YOLO-based license plate detector"""
    
    def __init__(self, model_path=None):
        """Initialize YOLO detector"""
        if model_path is None:
            model_path = DetectionConfig.YOLO_MODEL_PATH
            
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.available = True
            print(f"✓ YOLO model loaded: {model_path}")
        except Exception as e:
            print(f"⚠️ Cannot load YOLO model: {e}")
            self.model = None
            self.available = False
    
    def detect_plates(self, image):
        """Detect license plates in image"""
        if not self.available:
            return []
        
        results = self.model(image, conf=DetectionConfig.YOLO_CONF_THRESHOLD, verbose=False)
        
        plates = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                cls_name = 'BSD' if cls == 0 else 'BSV'
                
                # Validate bounding box
                width = x2 - x1
                height = y2 - y1
                aspect_ratio = width / height if height > 0 else 0
                
                if (DetectionConfig.YOLO_ASPECT_RATIO_MIN <= aspect_ratio <= DetectionConfig.YOLO_ASPECT_RATIO_MAX and
                    width > DetectionConfig.YOLO_MIN_WIDTH and 
                    height > DetectionConfig.YOLO_MIN_HEIGHT):
                    plates.append((int(x1), int(y1), int(x2), int(y2), conf, cls_name))
        
        return plates
    
    def extract_plate_region(self, image, x1, y1, x2, y2):
        """Extract plate region with padding"""
        h, w = image.shape[:2]
        
        pad_w = int((x2 - x1) * DetectionConfig.YOLO_PADDING)
        pad_h = int((y2 - y1) * DetectionConfig.YOLO_PADDING)
        
        x1 = max(0, x1 - pad_w)
        y1 = max(0, y1 - pad_h)
        x2 = min(w, x2 + pad_w)
        y2 = min(h, y2 + pad_h)
        
        return image[y1:y2, x1:x2]


class OptimizedPreprocessing:
    """Optimized preprocessing with smart variant selection"""
    
    @staticmethod
    def create_variants(plate_img):
        """
        Create optimized variants based on image quality
        Reduced from 15 to 10 variants
        """
        variants = []
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        # Assess image quality
        quality = calculate_image_quality(plate_img)
        
        # Always include these (Core variants)
        # 1. Original
        variants.append((plate_img, "original"))
        
        # 2. CLAHE enhanced
        clahe = cv2.createCLAHE(
            clipLimit=PreprocessingConfig.CLAHE_CLIP_LIMIT,
            tileGridSize=PreprocessingConfig.CLAHE_TILE_SIZE
        )
        enhanced = clahe.apply(gray)
        variants.append((ensure_bgr(enhanced), "clahe"))
        
        # 3. Sharpened
        denoised = cv2.fastNlMeansDenoising(gray, None, 
                                           PreprocessingConfig.DENOISE_H,
                                           PreprocessingConfig.DENOISE_TEMPLATE_SIZE,
                                           PreprocessingConfig.DENOISE_SEARCH_SIZE)
        kernel = np.array([[-1,-1,-1], 
                          [-1, PreprocessingConfig.SHARPEN_KERNEL_CENTER, -1], 
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        variants.append((ensure_bgr(sharpened), "sharp"))
        
        # 4. Otsu binary
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append((ensure_bgr(binary), "otsu"))
        
        # 5. Adaptive threshold
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
        variants.append((ensure_bgr(adaptive), "adaptive"))
        
        # Add more variants for poor quality images
        if quality in ['medium', 'poor']:
            # 6. Resize 400px
            resized = resize_if_needed(plate_img, 400)
            if resized.shape != plate_img.shape:
                variants.append((resized, "resize_400"))
            
            # 7. Gamma bright
            gamma_table = np.array([((i / 255.0) ** (1.0/PreprocessingConfig.GAMMA_BRIGHT)) * 255 
                                   for i in range(256)]).astype("uint8")
            gamma_bright = cv2.LUT(gray, gamma_table)
            variants.append((ensure_bgr(gamma_bright), "gamma_bright"))
            
            # 8. Gamma dark
            gamma_table_dark = np.array([((i / 255.0) ** (1.0/PreprocessingConfig.GAMMA_DARK)) * 255 
                                        for i in range(256)]).astype("uint8")
            gamma_dark = cv2.LUT(gray, gamma_table_dark)
            variants.append((ensure_bgr(gamma_dark), "gamma_dark"))
        
        # Add extra variants for very poor quality
        if quality == 'poor':
            # 9. Histogram equalization
            hist_eq = cv2.equalizeHist(gray)
            variants.append((ensure_bgr(hist_eq), "hist_eq"))
            
            # 10. Contrast stretching
            min_val, max_val = np.min(gray), np.max(gray)
            if max_val > min_val:
                stretched = ((gray - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                variants.append((ensure_bgr(stretched), "contrast"))
        
        return variants[:PreprocessingConfig.MAX_VARIANTS]


class OptimizedConfidenceCalculator:
    """Optimized confidence calculator with early stopping"""
    
    @staticmethod
    def calculate(yolo_conf, ocr_results, total_variants):
        """Calculate confidence with config-based weights"""
        if not ocr_results:
            return 0.0, {}
        
        # Count votes
        text_counts = Counter([r[0] for r in ocr_results])
        most_common_text = text_counts.most_common(1)[0][0]
        vote_count = text_counts[most_common_text]
        
        # Get confidences
        matching_confs = [r[1] for r in ocr_results if r[0] == most_common_text]
        
        best_ocr_conf = max(matching_confs)
        avg_ocr_conf = sum(matching_confs) / len(matching_confs)
        median_ocr_conf = sorted(matching_confs)[len(matching_confs)//2]
        std_dev = np.std(matching_confs) if len(matching_confs) > 1 else 0
        
        vote_ratio = vote_count / total_variants
        
        # Calculate bonuses (using config)
        if vote_ratio >= ConfidenceConfig.VOTE_RATIO_EXCELLENT:
            vote_bonus = ConfidenceConfig.VOTE_BONUS_EXCELLENT
        elif vote_ratio >= ConfidenceConfig.VOTE_RATIO_GOOD:
            vote_bonus = ConfidenceConfig.VOTE_BONUS_GOOD
        elif vote_ratio >= ConfidenceConfig.VOTE_RATIO_FAIR:
            vote_bonus = ConfidenceConfig.VOTE_BONUS_FAIR
        else:
            vote_bonus = 0.0
        
        if std_dev < ConfidenceConfig.STD_DEV_EXCELLENT:
            consistency_bonus = ConfidenceConfig.CONSISTENCY_BONUS_EXCELLENT
        elif std_dev < ConfidenceConfig.STD_DEV_GOOD:
            consistency_bonus = ConfidenceConfig.CONSISTENCY_BONUS_GOOD
        elif std_dev < ConfidenceConfig.STD_DEV_FAIR:
            consistency_bonus = ConfidenceConfig.CONSISTENCY_BONUS_FAIR
        else:
            consistency_bonus = 0.0
        
        if avg_ocr_conf < ConfidenceConfig.QUALITY_POOR:
            quality_penalty = ConfidenceConfig.QUALITY_PENALTY_POOR
        elif avg_ocr_conf < ConfidenceConfig.QUALITY_FAIR:
            quality_penalty = ConfidenceConfig.QUALITY_PENALTY_FAIR
        else:
            quality_penalty = 0.0
        
        # Calculate final confidence
        base_conf = (
            yolo_conf * ConfidenceConfig.WEIGHT_YOLO +
            best_ocr_conf * ConfidenceConfig.WEIGHT_BEST_OCR +
            median_ocr_conf * ConfidenceConfig.WEIGHT_MEDIAN_OCR +
            avg_ocr_conf * ConfidenceConfig.WEIGHT_AVG_OCR
        )
        
        final_conf = base_conf + vote_bonus + consistency_bonus + quality_penalty
        final_conf = clamp(final_conf)
        
        details = {
            'yolo_conf': yolo_conf,
            'best_ocr_conf': best_ocr_conf,
            'avg_ocr_conf': avg_ocr_conf,
            'median_ocr_conf': median_ocr_conf,
            'vote_count': vote_count,
            'vote_ratio': vote_ratio,
            'vote_bonus': vote_bonus,
            'consistency_bonus': consistency_bonus,
            'quality_penalty': quality_penalty,
            'std_dev': std_dev
        }
        
        return final_conf, details


def integrate_yolo_detection(image_path, ocr_detector, yolo_model_path=None):
    """
    Optimized YOLO + OCR integration
    - Smart variant selection
    - Early stopping
    - Config-based
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        return None, 0.0, "image_load_error"
    
    # Initialize YOLO
    yolo = YOLOPlateDetector(yolo_model_path)
    if not yolo.available:
        return None, 0.0, "yolo_unavailable"
    
    # Detect plates
    plates = yolo.detect_plates(image)
    if not plates:
        return None, 0.0, "no_detection"
    
    # Get best detection
    plates.sort(key=lambda x: x[4], reverse=True)
    x1, y1, x2, y2, yolo_conf, cls_name = plates[0]
    
    # Extract plate region
    plate_img = yolo.extract_plate_region(image, x1, y1, x2, y2)
    
    # Create optimized variants
    variants = OptimizedPreprocessing.create_variants(plate_img)
    
    # Run OCR with early stopping
    all_ocr_results = []
    
    for variant_img, variant_name in variants:
        ocr_results = ocr_detector.read_text(variant_img)
        
        if ocr_results:
            for bbox, raw_text, ocr_conf in ocr_results:
                if ocr_conf > OCRConfig.OCR_CONF_THRESHOLD:
                    cleaned = clean_text(raw_text)
                    
                    if len(cleaned) < ValidationConfig.MIN_LENGTH_RAW or len(cleaned) > ValidationConfig.MAX_LENGTH_RAW:
                        continue
                    
                    if not has_valid_components(cleaned):
                        continue
                    
                    license_text = format_vietnamese_plate(cleaned)
                    
                    if validate_vietnamese_plate(license_text):
                        all_ocr_results.append((license_text, ocr_conf, variant_name))
        
        # Early stopping check
        if len(all_ocr_results) >= ConfidenceConfig.EARLY_STOP_MIN_VOTES:
            text_counts = Counter([r[0] for r in all_ocr_results])
            if text_counts.most_common(1)[0][1] >= ConfidenceConfig.EARLY_STOP_MIN_VOTES:
                # Calculate temp confidence
                temp_conf, _ = OptimizedConfidenceCalculator.calculate(
                    yolo_conf, all_ocr_results, len(variants)
                )
                if temp_conf >= ConfidenceConfig.EARLY_STOP_CONFIDENCE:
                    break  # Good enough!
    
    if not all_ocr_results:
        return None, yolo_conf, "yolo_detected_but_ocr_failed"
    
    # Calculate final confidence
    final_conf, details = OptimizedConfidenceCalculator.calculate(
        yolo_conf, all_ocr_results, len(variants)
    )
    
    # Get most common text
    text_counts = Counter([r[0] for r in all_ocr_results])
    most_common_text = text_counts.most_common(1)[0][0]
    
    return most_common_text, final_conf, f"yolo_{cls_name}"


if __name__ == "__main__":
    print("YOLO Detector - Optimized Version")
    print("=" * 50)
    print("Improvements:")
    print("  ✓ Config-based settings")
    print("  ✓ Shared utils functions")
    print("  ✓ Variants: 15 → 10 (smart selection)")
    print("  ✓ Early stopping")
    print("  ✓ Better organized code")
    print("=" * 50)
