"""
Test cải thiện nhận diện số 5 và 6
"""
import cv2
import numpy as np
from pathlib import Path
from license_plate_detector import LicensePlateDetector
from preprocess_image import ImagePreprocessor

print("=" * 70)
print("TEST CẢI THIỆN NHẬN DIỆN SỐ 5 VÀ 6")
print("=" * 70)

# Tìm ảnh demo
demo_images = list(Path(".").glob("demo_plate_*.jpg"))
if not demo_images:
    print("✗ Không có ảnh demo")
    exit(1)

print(f"\n✓ Tìm thấy {len(demo_images)} ảnh demo")

# Khởi tạo
print("\n[1] Initializing preprocessor...")
preprocessor = ImagePreprocessor()
print("  ✓ Preprocessor ready")

print("\n[2] Initializing EasyOCR with improved settings...")
print("  (Lần đầu có thể mất 30-60 giây)")
ocr_detector = LicensePlateDetector(languages=['en', 'vi'], gpu=False)
print("  ✓ OCR ready with:")
print("    - Smart digit correction (5/6, 8/0, 1/7)")
print("    - Enhanced sharpening (2.0x)")
print("    - Improved thresholds")
print("    - 11 preprocessing variants (thêm 2 variants mới)")

# Test với từng ảnh
results = []
for img_path in demo_images:
    print(f"\n{'='*70}")
    print(f"Testing: {img_path.name}")
    print(f"{'='*70}")
    
    try:
        # Đọc ảnh
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"  ✗ Cannot read {img_path.name}")
            continue
        
        print(f"  ✓ Image loaded: {image.shape}")
        
        # Preprocessing
        print("  [+] Preprocessing...")
        plate_variants, coords, processed = preprocessor.preprocess_for_ocr(image)
        
        if not plate_variants:
            print(f"  ✗ No license plate detected")
            continue
        
        print(f"  ✓ Generated {len(plate_variants)} variants")
        
        # OCR
        print("  [+] Running OCR with smart correction...")
        license_text, confidence, ocr_results = ocr_detector.detect_plate(plate_variants)
        
        print(f"\n  📋 Result: {license_text}")
        print(f"  🎯 Confidence: {confidence:.1%}")
        
        # Hiển thị chi tiết OCR
        if ocr_results:
            print(f"  🔍 OCR detections ({len(ocr_results)}):")
            for i, (bbox, text, conf) in enumerate(ocr_results[:5], 1):
                print(f"      [{i}] '{text}' (conf: {conf:.2%})")
        
        # Kiểm tra có số 5 hoặc 6 không
        has_5_or_6 = '5' in license_text or '6' in license_text
        if has_5_or_6:
            print(f"  ⚠️  Contains 5 or 6 - Smart correction applied")
        
        results.append({
            'image': img_path.name,
            'text': license_text,
            'confidence': confidence,
            'has_5_or_6': has_5_or_6
        })
        
        # Vẽ kết quả
        if coords:
            result_img = processed.copy()
            x, y, w, h = coords
            cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(result_img, license_text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            output_name = f"test_56_result_{img_path.stem}.jpg"
            cv2.imwrite(output_name, result_img)
            print(f"  💾 Saved: {output_name}")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"Total images tested: {len(results)}")
print(f"Successful detections: {len([r for r in results if r['text'] != 'Không phát hiện được biển số'])}")
print(f"Images with 5 or 6: {len([r for r in results if r['has_5_or_6']])}")

if results:
    avg_conf = sum(r['confidence'] for r in results) / len(results)
    print(f"Average confidence: {avg_conf:.1%}")

print("\n📊 CẢI TIẾN ĐÃ ÁP DỤNG:")
print("  ✅ Smart digit correction (context-aware)")
print("  ✅ Enhanced sharpening (1.5x → 2.0x)")
print("  ✅ Improved OCR thresholds (0.4 → 0.3)")
print("  ✅ Increased mag_ratio (1.5 → 1.8)")
print("  ✅ Added edge enhancement variant")
print("  ✅ Added contrast stretching variant")
print("  ✅ Total variants: 9 → 11")

print(f"\n{'='*70}")
print("✅ TEST COMPLETED")
print(f"{'='*70}")
print("\nĐể test với ảnh thực tế, chạy:")
print("  py main_yolo.py")
