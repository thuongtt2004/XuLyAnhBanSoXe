"""
Demo test với ảnh thật - không cần EasyOCR
"""
import cv2
from pathlib import Path
from preprocess_image import ImagePreprocessor

print("=" * 70)
print("DEMO: PHÁT HIỆN BIỂN SỐ XE (Chỉ detection, không OCR)")
print("=" * 70)

# Khởi tạo preprocessor
preprocessor = ImagePreprocessor()

# Test với 3 ảnh đầu tiên
test_images = [
    "archive/images/val/carlong_0004.png",
    "archive/images/val/Dieu_0003.png",
    "archive/images/val/greenpack_0002.png"
]

for i, img_path in enumerate(test_images, 1):
    print(f"\n[{i}] Testing: {Path(img_path).name}")
    
    if not Path(img_path).exists():
        print("  ✗ File not found")
        continue
    
    # Đọc ảnh
    image = cv2.imread(img_path)
    if image is None:
        print("  ✗ Cannot read image")
        continue
    
    print(f"  ✓ Image size: {image.shape[1]}x{image.shape[0]}")
    
    # Phát hiện biển số
    try:
        plate_variants, coords, processed = preprocessor.preprocess_for_ocr(image)
        
        if plate_variants and coords:
            x, y, w, h = coords
            print(f"  ✓ License plate detected!")
            print(f"    Position: x={x}, y={y}, w={w}, h={h}")
            print(f"    Generated {len(plate_variants)} variants for OCR")
            
            # Vẽ khung và lưu kết quả
            result_img = processed.copy()
            cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(result_img, "License Plate Detected", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            output_path = f"demo_result_{i}.jpg"
            cv2.imwrite(output_path, result_img)
            print(f"  ✓ Saved: {output_path}")
            
            # Lưu plate crop
            plate_path = f"demo_plate_{i}.jpg"
            cv2.imwrite(plate_path, plate_variants[0])
            print(f"  ✓ Saved plate: {plate_path}")
        else:
            print("  ⚠ No license plate detected")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("DEMO COMPLETED!")
print("=" * 70)
print("\nKết quả:")
print("- Ảnh có khung biển số: demo_result_1.jpg, demo_result_2.jpg, ...")
print("- Ảnh biển số đã cắt: demo_plate_1.jpg, demo_plate_2.jpg, ...")
print("\nĐể test OCR đầy đủ, chạy: py main_yolo.py")
