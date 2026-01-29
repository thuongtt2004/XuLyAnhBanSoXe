"""
Utility functions for License Plate Recognition
Shared functions to avoid code duplication
"""
import re
import cv2
import numpy as np
from config import ValidationConfig


def validate_vietnamese_plate(text):
    """
    Validate Vietnamese license plate format
    Centralized validation logic
    
    Args:
        text: License plate text
        
    Returns:
        bool: True if valid
    """
    if not text or len(text) < ValidationConfig.MIN_LENGTH_RAW:
        return False
    
    # Clean text
    clean = text.replace('-', '').replace('.', '').replace(' ', '').upper()
    
    # Length check
    if len(clean) < ValidationConfig.MIN_LENGTH_CLEAN or len(clean) > ValidationConfig.MAX_LENGTH_CLEAN:
        return False
    
    # Component count check
    letter_count = sum(1 for c in clean if c.isalpha())
    digit_count = sum(1 for c in clean if c.isdigit())
    
    if letter_count < ValidationConfig.MIN_LETTERS or letter_count > ValidationConfig.MAX_LETTERS:
        return False
    if digit_count < ValidationConfig.MIN_DIGITS or digit_count > ValidationConfig.MAX_DIGITS:
        return False
    
    # Province code check
    if not (clean[:2].isdigit() and 
            ValidationConfig.MIN_PROVINCE_CODE <= int(clean[:2]) <= ValidationConfig.MAX_PROVINCE_CODE):
        return False
    
    # Pattern matching
    patterns = [
        r'^\d{2}[A-Z]{1}\d{4,6}$',
        r'^\d{2}[A-Z]{2}\d{4,6}$',
        r'^\d{2}[A-Z]{1}[A-Z]{1}\d{4,6}$',
    ]
    
    return any(re.match(pattern, clean) for pattern in patterns)


def format_vietnamese_plate(text):
    """
    Format Vietnamese license plate with dashes and dots
    Centralized formatting logic
    
    Args:
        text: Raw plate text
        
    Returns:
        str: Formatted plate
    """
    # Clean text
    text = re.sub(r'[^A-Z0-9.\-]', '', text.upper())
    
    # Remove duplicate marks
    text = text.strip('.-')
    text = re.sub(r'-+', '-', text)
    text = re.sub(r'\.+', '.', text)
    
    # If no marks, try to add automatically
    if '-' not in text and '.' not in text:
        clean = text.replace('-', '').replace('.', '')
        match = re.match(r'^(\d{2})([A-Z]{1,2})(\d+)$', clean)
        
        if match:
            province = match.group(1)
            letter = match.group(2)
            numbers = match.group(3)
            
            # Add dash after letters
            text = f"{province}{letter}-{numbers}"
            
            # Add dot in numbers
            if len(numbers) == 5:
                text = f"{province}{letter}-{numbers[:3]}.{numbers[3:]}"
            elif len(numbers) == 6:
                text = f"{province}{letter}-{numbers[:4]}.{numbers[4:]}"
    
    # Fix wrong position marks
    elif '-' in text or '.' in text:
        clean = text.replace('-', '').replace('.', '')
        match = re.match(r'^(\d{2})([A-Z]{1,2})(\d+)$', clean)
        
        if match:
            province = match.group(1)
            letter = match.group(2)
            numbers = match.group(3)
            
            if len(numbers) == 4:
                text = f"{province}{letter}-{numbers}"
            elif len(numbers) == 5:
                text = f"{province}{letter}-{numbers[:3]}.{numbers[3:]}"
            elif len(numbers) == 6:
                text = f"{province}{letter}-{numbers[:4]}.{numbers[4:]}"
            else:
                text = f"{province}{letter}-{numbers}"
    
    return text


def clean_text(text):
    """
    Clean OCR text
    
    Args:
        text: Raw OCR text
        
    Returns:
        str: Cleaned text
    """
    return re.sub(r'[^A-Z0-9.\-]', '', text.upper())


def has_valid_components(text):
    """
    Check if text has valid components (letters and digits)
    
    Args:
        text: Text to check
        
    Returns:
        bool: True if has both letters and digits
    """
    has_letter = any(c.isalpha() for c in text)
    has_digit = any(c.isdigit() for c in text)
    return has_letter and has_digit


def calculate_image_quality(image):
    """
    Estimate image quality using Laplacian variance
    
    Args:
        image: Input image (BGR or grayscale)
        
    Returns:
        str: 'good', 'medium', or 'poor'
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Calculate Laplacian variance (blur detection)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if laplacian_var > 500:
        return 'good'
    elif laplacian_var > 100:
        return 'medium'
    else:
        return 'poor'


def resize_if_needed(image, target_width):
    """
    Resize image if width is less than target
    
    Args:
        image: Input image
        target_width: Target width
        
    Returns:
        Resized image or original
    """
    h, w = image.shape[:2]
    if w < target_width:
        scale = target_width / w
        return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return image


def ensure_bgr(image):
    """
    Ensure image is in BGR format
    
    Args:
        image: Input image
        
    Returns:
        BGR image
    """
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def clamp(value, min_val=0.0, max_val=1.0):
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))
