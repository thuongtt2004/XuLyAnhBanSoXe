"""
Full detection test with real image
"""
import cv2
from license_plate_detector import LicensePlateDetector
from yolo_detector import integrate_yolo_detection

print("=" * 70)
print("FULL DETECTION TEST")
print("=" * 70)
print()

# Test images
test_images = [
    "demo_plate_1.jpg",
    "demo_plate_2.jpg",
    "demo_plate_3.jpg",
]

# Initialize detector
print("Initializing detector...")
detector = LicensePlateDetector()
print()

for img_path in test_images:
    print(f"Testing: {img_path}")
    print("-" * 70)
    
    try:
        # Test with YOLO
        print("  Method: YOLO + OCR")
        plate_text, confidence, method = integrate_yolo_detection(
            img_path, detector
        )
        
        if plate_text:
            print(f"  ✓ Result: {plate_text}")
            print(f"  ✓ Confidence: {confidence:.1%}")
            print(f"  ✓ Method: {method}")
        else:
            print(f"  ✗ No detection")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()

print("=" * 70)
print("Test completed!")
print("=" * 70)
