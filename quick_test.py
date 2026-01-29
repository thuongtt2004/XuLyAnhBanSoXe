"""
Test nhanh chức năng nhận diện biển số
"""
import cv2
import os
from pathlib import Path

print("=" * 60)
print("TEST NHANH NHẬN DIỆN BIỂN SỐ XE")
print("=" * 60)

# Kiểm tra ảnh test
test_images_dir = Path("archive/images/val")
if test_images_dir.exists():
    test_images = list(test_images_dir.glob("*.jpg"))[:3]
    print(f"\n✓ Tìm thấy {len(test_images)} ảnh test")
else:
    print("\n✗ Không tìm thấy thư mục ảnh test")
    test_images = []

# Test 1: Import modules
print("\n[1] Testing imports...")
try:
    from preprocess_image import ImagePreprocessor
    from license_plate_detector import LicensePlateDetector
    print("  ✓ Modules imported successfully")
except Exception as e:
    print(f"  ✗ Import error: {e}")
    exit(1)

# Test 2: Khởi tạo preprocessor
print("\n[2] Testing ImagePreprocessor...")
try:
    preprocessor = ImagePreprocessor()
    print("  ✓ ImagePreprocessor initialized")
except Exception as e:
    print(f"  ✗ Error: {e}")
    exit(1)

# Test 3: Test với ảnh mẫu (không cần EasyOCR)
if test_images:
    print("\n[3] Testing image preprocessing...")
    test_img_path = str(test_images[0])
    print(f"  Testing with: {Path(test_img_path).name}")
    
    try:
        image = cv2.imread(test_img_path)
        if image is None:
            print("  ✗ Cannot read image")
        else:
            print(f"  ✓ Image loaded: {image.shape}")
            
            # Test preprocessing
            plate_variants, coords, processed = preprocessor.preprocess_for_ocr(image)
            
            if plate_variants:
                print(f"  ✓ Detected license plate region")
                print(f"  ✓ Generated {len(plate_variants)} image variants")
                if coords:
                    x, y, w, h = coords
                    print(f"  ✓ Coordinates: ({x}, {y}, {w}, {h})")
                
                # Lưu ảnh kết quả
                output_path = "test_detection_result.jpg"
                if coords:
                    result_img = processed.copy()
                    cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(result_img, "License Plate", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imwrite(output_path, result_img)
                    print(f"  ✓ Result saved: {output_path}")
            else:
                print("  ⚠ No license plate detected")
                
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

# Test 4: Kiểm tra YOLO model
print("\n[4] Checking YOLO model...")
yolo_model_path = "runs/license_plate/weights/best.pt"
if Path(yolo_model_path).exists():
    print(f"  ✓ YOLO model found: {yolo_model_path}")
    try:
        from yolo_detector import YOLOPlateDetector
        detector = YOLOPlateDetector(yolo_model_path)
        if detector.available:
            print("  ✓ YOLO detector initialized")
        else:
            print("  ⚠ YOLO detector not available")
    except Exception as e:
        print(f"  ⚠ YOLO error: {e}")
else:
    print(f"  ⚠ YOLO model not found (will use OpenCV)")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
print("\nNote: OCR test skipped (requires EasyOCR initialization)")
print("To test full OCR, run: py main_yolo.py")
