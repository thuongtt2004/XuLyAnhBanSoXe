"""
So sánh YOLO vs OpenCV detection
"""
import cv2
from yolo_detector import YOLOPlateDetector
from license_plate_detector import LicensePlateDetector
from preprocess_image import ImagePreprocessor
import time
import sys

def test_image(image_path):
    """Test 1 ảnh với cả 2 phương pháp"""
    print(f"\n{'='*70}")
    print(f"[IMAGE] Testing: {image_path}")
    print(f"{'='*70}\n")
    
    image = cv2.imread(image_path)
    if image is None:
        print("❌ Không đọc được ảnh!")
        return
    
    ocr = LicensePlateDetector()
    
    # Method 1: YOLO
    print("[YOLO] AI Detection")
    print("-" * 70)
    start = time.time()
    
    yolo = YOLOPlateDetector("d:/game/runs/license_plate/weights/best.pt")
    plates = yolo.detect_plates(image, conf_threshold=0.15)
    
    yolo_time = time.time() - start
    
    if plates:
        x1, y1, x2, y2, conf, cls = plates[0]  # Best detection
        print(f"✅ Detected: {cls} (confidence: {conf:.2%})")
        
        plate_img = yolo.extract_plate_region(image, x1, y1, x2, y2, padding=0.1)
        cv2.imwrite("d:/game/temp_yolo.jpg", plate_img)
        
        results = ocr.read_text("d:/game/temp_yolo.jpg")
        if results:
            raw_text = results[0][1]  # Get text from first result
            yolo_conf = results[0][2]  # Get confidence
            # Format and validate
            from license_plate_detector import LicensePlateDetector
            detector = LicensePlateDetector()
            yolo_text = detector.format_vietnamese_plate(raw_text)
            if not detector.validate_vietnamese_plate(yolo_text):
                yolo_text = None
        else:
            yolo_text = None
            yolo_conf = 0.0
        
        print(f"📋 License Plate: {yolo_text if yolo_text else 'Không đọc được'}")
        print(f"⏱️  Time: {yolo_time:.2f}s")
    else:
        print("❌ Không phát hiện được")
        yolo_text = None
    
    # Method 2: OpenCV
    print(f"\n[OPENCV] Rule-based Detection")
    print("-" * 70)
    start = time.time()
    
    preprocessor = ImagePreprocessor()
    plate_images = preprocessor.preprocess_for_ocr(image)  # Pass image object not path
    
    opencv_time = time.time() - start
    
    if plate_images:
        opencv_text, opencv_conf, ocr_results = ocr.detect_plate(plate_images)
        print(f"✅ Detected: {len(plate_images)} variants processed")
        print(f"📋 License Plate: {opencv_text if opencv_text else 'Không đọc được'}")
        print(f"⏱️  Time: {opencv_time:.2f}s")
    else:
        print("❌ Không phát hiện được")
        opencv_text = None
    
    # Comparison
    print(f"\n[COMPARISON]")
    print("-" * 70)
    print(f"YOLO:   {('[OK] ' + yolo_text) if yolo_text else '[FAIL]':<40} ({yolo_time:.2f}s)")
    print(f"OpenCV: {('[OK] ' + opencv_text) if opencv_text else '[FAIL]':<40} ({opencv_time:.2f}s)")
    
    if yolo_text and opencv_text:
        if yolo_text == opencv_text:
            print("\n[MATCHED] Both methods got same result")
        else:
            print(f"\n[DIFFERENT] Results don't match!")
            print(f"   YOLO: {yolo_text}")
            print(f"   OpenCV: {opencv_text}")
    elif yolo_text and not opencv_text:
        print("\n[WINNER: YOLO] OpenCV failed")
    elif opencv_text and not yolo_text:
        print("\n[WINNER: OpenCV] YOLO failed")
    else:
        print("\n[BOTH FAILED]")
    
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific images
        for img_path in sys.argv[1:]:
            test_image(img_path)
    else:
        # Test random images from val set
        import glob
        images = glob.glob("d:/game/archive/images/val/*.png")[:5]
        if not images:
            images = glob.glob("d:/game/archive/images/val/*.jpg")[:5]
        
        print(f"\n[TEST] Testing {len(images)} random images...\n")
        
        for img in images:
            test_image(img)
        
        print("\n" + "="*70)
        print("✓ Testing complete!")
        print("="*70)
