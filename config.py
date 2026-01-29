"""
Configuration file for License Plate Recognition
Centralized settings for easy tuning
"""

class DetectionConfig:
    """YOLO Detection settings"""
    YOLO_MODEL_PATH = "d:/game/runs/license_plate/weights/best.pt"
    YOLO_CONF_THRESHOLD = 0.05  # Giảm từ 0.10 để phát hiện nhiều hơn
    YOLO_PADDING = 0.2
    YOLO_MIN_WIDTH = 50
    YOLO_MIN_HEIGHT = 20
    YOLO_ASPECT_RATIO_MIN = 1.5
    YOLO_ASPECT_RATIO_MAX = 7.0


class OCRConfig:
    """OCR settings - ULTRA OPTIMIZED"""
    # Languages
    LANGUAGES = ['en', 'vi']
    USE_GPU = False
    
    # Thresholds - VERY LOW for maximum detection
    OCR_CONF_THRESHOLD = 0.10  # Giảm từ 0.15
    TEXT_THRESHOLD = 0.15      # Giảm từ 0.20
    LOW_TEXT = 0.03            # Giảm từ 0.05
    LINK_THRESHOLD = 0.03      # Giảm từ 0.05
    
    # Canvas - MAXIMUM for best quality
    CANVAS_SIZE = 5000         # Tăng từ 4000
    MAG_RATIO = 3.0            # Tăng từ 2.5
    
    # Other
    SLOPE_THS = 0.1            # Giảm từ 0.2
    YCENTER_THS = 0.5          # Giảm từ 0.6
    HEIGHT_THS = 0.7           # Giảm từ 0.8
    WIDTH_THS = 0.5            # Giảm từ 0.6
    ADD_MARGIN = 0.3           # Tăng từ 0.2
    
    # Allowlist
    ALLOWLIST = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-.'


class PreprocessingConfig:
    """Preprocessing settings - ULTRA OPTIMIZED"""
    # Variants - MAXIMUM
    MAX_VARIANTS = 20  # Tăng từ 15
    USE_SMART_SELECTION = True
    
    # CLAHE - VERY STRONG
    CLAHE_CLIP_LIMIT = 6.0  # Tăng từ 5.0
    CLAHE_TILE_SIZE = (8, 8)
    
    # Sharpen - VERY STRONG
    SHARPEN_KERNEL_CENTER = 20  # Tăng từ 17
    
    # Resize - MORE OPTIONS
    RESIZE_WIDTHS = [300, 400, 500, 600, 800]  # Thêm 800
    MIN_RESIZE_WIDTH = 400  # Tăng từ 300
    
    # Gamma
    GAMMA_BRIGHT = 1.5
    GAMMA_DARK = 0.7
    
    # Denoise
    DENOISE_H = 10
    DENOISE_TEMPLATE_SIZE = 7
    DENOISE_SEARCH_SIZE = 21


class ValidationConfig:
    """Validation settings"""
    # Length
    MIN_LENGTH_CLEAN = 7
    MAX_LENGTH_CLEAN = 10
    MIN_LENGTH_RAW = 6
    MAX_LENGTH_RAW = 15
    
    # Components
    MIN_LETTERS = 1
    MAX_LETTERS = 3
    MIN_DIGITS = 6
    MAX_DIGITS = 8
    
    # Province code
    MIN_PROVINCE_CODE = 1
    MAX_PROVINCE_CODE = 99


class ConfidenceConfig:
    """Confidence calculation settings"""
    # Weights
    WEIGHT_YOLO = 0.20
    WEIGHT_BEST_OCR = 0.40
    WEIGHT_MEDIAN_OCR = 0.15
    WEIGHT_AVG_OCR = 0.10
    
    # Vote bonus thresholds
    VOTE_RATIO_EXCELLENT = 0.6  # 60%+
    VOTE_RATIO_GOOD = 0.4       # 40-60%
    VOTE_RATIO_FAIR = 0.2       # 20-40%
    
    # Vote bonus values
    VOTE_BONUS_EXCELLENT = 0.15
    VOTE_BONUS_GOOD = 0.10
    VOTE_BONUS_FAIR = 0.05
    
    # Consistency thresholds
    STD_DEV_EXCELLENT = 0.05
    STD_DEV_GOOD = 0.10
    STD_DEV_FAIR = 0.15
    
    # Consistency bonus values
    CONSISTENCY_BONUS_EXCELLENT = 0.05
    CONSISTENCY_BONUS_GOOD = 0.03
    CONSISTENCY_BONUS_FAIR = 0.01
    
    # Quality penalty thresholds
    QUALITY_POOR = 0.5
    QUALITY_FAIR = 0.6
    
    # Quality penalty values
    QUALITY_PENALTY_POOR = -0.10
    QUALITY_PENALTY_FAIR = -0.05
    
    # Early stopping
    EARLY_STOP_CONFIDENCE = 0.95
    EARLY_STOP_MIN_VOTES = 5


class UIConfig:
    """UI settings"""
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 750
    
    # Colors
    COLOR_PRIMARY = '#667eea'
    COLOR_PRIMARY_DARK = '#5568d3'
    COLOR_SUCCESS = '#48bb78'
    COLOR_SUCCESS_DARK = '#38a169'
    COLOR_WARNING = '#ed8936'
    COLOR_WARNING_DARK = '#dd6b20'
    COLOR_BG = '#f5f6fa'
    COLOR_CARD = '#ffffff'
    COLOR_TEXT = '#2d3748'
    COLOR_TEXT_LIGHT = '#718096'


# Export all configs
__all__ = [
    'DetectionConfig',
    'OCRConfig',
    'PreprocessingConfig',
    'ValidationConfig',
    'ConfidenceConfig',
    'UIConfig'
]
