"""
Test OpenCV method to ensure validation works
"""
import cv2
from license_plate_detector import LicensePlateDetector
from preprocess_image import ImagePreprocessor

print("=" * 70)
print("OPENCV METHOD TEST")
print("=" * 70)
print()

# Initialize
print("Initializing...")
detector = LicensePlateDetector()
preprocessor = ImagePreprocessor()
print()

# Test with demo image
img_path = "demo_plate_1.jpg"
print(f"Testing: {img_path}")
print("-" * 70)

image = cv2.imread(img_path)
if image is None:
    print("✗ Cannot read image")
else:
    print(f"✓ Image loaded: {image.shape}")
    
    # Preprocess
    print("  Preprocessing...")
    plate_images, coords, processed = preprocessor.preprocess_for_ocr(image)
    
    if not plate_images:
        print("  ✗ No plate detected by OpenCV")
    else:
        print(f"  ✓ Detected {len(plate_images)} variants")
        
        # OCR
        print("  Running OCR...")
        license_text, confidence, ocr_results = detector.detect_plate(plate_images)
        
        print(f"  Result: {license_text}")
        print(f"  Confidence: {confidence:.1%}")
        
        if license_text != "Không phát hiện được biển số":
            print("  ✓ SUCCESS!")
        else:
            print("  ✗ No valid plate detected")

print()
print("=" * 70)
