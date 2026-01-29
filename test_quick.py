"""
Script test nhanh nhận diện biển số xe với ảnh từ dataset
"""
import cv2
import sys
import os

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(__file__))

from preprocess_image import ImagePreprocessor
from license_plate_detector import LicensePlateDetector

def test_single_image(image_path):
    """Test nhận diện với 1 ảnh"""
    print(f"\n{'='*60}")
    print(f"Đang xử lý: {os.path.basename(image_path)}")
    print(f"{'='*60}")
    
    # Đọc ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Không thể đọc ảnh: {image_path}")
        return
    
    print(f"✓ Đã đọc ảnh: {image.shape}")
    
    # Khởi tạo preprocessor
    preprocessor = ImagePreprocessor()
    
    # Tiền xử lý
    print("🔄 Đang tiền xử lý ảnh...")
    plate_images, coordinates, resized = preprocessor.preprocess_for_ocr(image)
    
    if plate_images is None or not plate_images:
        print("❌ Không tìm thấy biển số trong ảnh")
        return
    
    print(f"✓ Đã tìm thấy biển số tại: {coordinates}")
    print(f"✓ Tạo được {len(plate_images)} phiên bản ảnh để nhận diện")
    
    # Khởi tạo detector (lần đầu sẽ tải models)
    print("🤖 Đang khởi tạo EasyOCR...")
    detector = LicensePlateDetector(languages=['en'], gpu=False)
    
    # Nhận diện
    print("🔍 Đang nhận diện biển số...")
    license_number, confidence, ocr_results = detector.detect_plate(plate_images)
    
    # Hiển thị kết quả
    print(f"\n{'='*60}")
    print(f"🎯 KẾT QUẢ:")
    print(f"   Biển số: {license_number}")
    print(f"   Độ tin cậy: {confidence*100:.2f}%")
    print(f"{'='*60}\n")
    
    # Vẽ kết quả lên ảnh
    if coordinates:
        x, y, w, h = coordinates
        result_img = resized.copy()
        cv2.rectangle(result_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.putText(
            result_img,
            license_number,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        
        # Lưu kết quả
        output_path = f"result_{os.path.basename(image_path)}"
        cv2.imwrite(output_path, result_img)
        print(f"💾 Đã lưu kết quả: {output_path}")

def main():
    """Main function"""
    # Ảnh test mặc định từ dataset
    test_images = [
        r"d:\game\archive\images\train\carlong_0001.png",
        r"d:\game\archive\images\train\Dieu_0001.png",
        r"d:\game\archive\images\train\greenpack_0001.png",
    ]
    
    # Cho phép test với ảnh cụ thể
    if len(sys.argv) > 1:
        test_images = [sys.argv[1]]
    
    for img_path in test_images:
        if os.path.exists(img_path):
            test_single_image(img_path)
        else:
            print(f"⚠️ Không tìm thấy ảnh: {img_path}")

if __name__ == "__main__":
    main()
