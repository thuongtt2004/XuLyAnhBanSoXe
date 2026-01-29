"""
Cải thiện độ chính xác nhận diện biển số xe
"""
import cv2
import numpy as np
from license_plate_detector import LicensePlateDetector
from preprocess_image import ImagePreprocessor

class ImprovedLicensePlateDetector(LicensePlateDetector):
    """
    Phiên bản cải tiến với độ chính xác cao hơn
    """
    
    def __init__(self, languages=['en', 'vi'], gpu=False):
        """
        Khởi tạo với cấu hình tối ưu
        
        Args:
            languages: Thêm 'vi' để nhận diện tốt hơn với biển số VN
            gpu: Sử dụng GPU nếu có (nhanh hơn và chính xác hơn)
        """
        super().__init__(languages=languages, gpu=gpu)
        
        # Cấu hình tối ưu cho biển số VN
        self.allowlist = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-.'
    
    def read_text_enhanced(self, image, min_confidence=0.3):
        """
        Đọc text với nhiều cấu hình khác nhau và chọn kết quả tốt nhất
        
        Args:
            image: Ảnh đầu vào
            min_confidence: Ngưỡng confidence tối thiểu
            
        Returns:
            Danh sách kết quả OCR
        """
        all_results = []
        
        # Cấu hình 1: Mặc định
        results1 = self.read_text(image)
        all_results.extend(results1)
        
        # Cấu hình 2: Tăng contrast
        if isinstance(image, np.ndarray):
            if len(image.shape) == 2:
                enhanced = cv2.equalizeHist(image)
            else:
                # Convert sang LAB, equalize L channel
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                l = cv2.equalizeHist(l)
                enhanced = cv2.merge([l, a, b])
                enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            results2 = self.read_text(enhanced)
            all_results.extend(results2)
        
        # Lọc kết quả theo confidence
        filtered = [r for r in all_results if r[2] >= min_confidence]
        
        # Loại bỏ duplicate
        unique_results = []
        seen_texts = set()
        for bbox, text, conf in filtered:
            if text not in seen_texts:
                unique_results.append((bbox, text, conf))
                seen_texts.add(text)
        
        # Sắp xếp theo confidence
        unique_results.sort(key=lambda x: x[2], reverse=True)
        
        return unique_results
    
    def detect_plate_enhanced(self, images):
        """
        Phát hiện biển số với độ chính xác cao hơn
        
        Args:
            images: Danh sách ảnh biển số
            
        Returns:
            Tuple (biển số, độ tin cậy, kết quả OCR)
        """
        if not isinstance(images, list):
            images = [images]
        
        all_results = []
        best_ocr_results = None
        
        # Thử OCR với từng phiên bản ảnh
        for img in images:
            # Sử dụng read_text_enhanced
            ocr_results = self.read_text_enhanced(img, min_confidence=0.3)
            
            if ocr_results:
                license_number = self.extract_license_number(ocr_results)
                formatted_plate = self.format_vietnamese_plate(license_number)
                is_valid = self.validate_vietnamese_plate(formatted_plate)
                avg_confidence = sum([conf for _, _, conf in ocr_results]) / len(ocr_results)
                
                all_results.append((formatted_plate, avg_confidence, is_valid))
                
                if is_valid and (best_ocr_results is None or avg_confidence > best_ocr_results[1]):
                    best_ocr_results = (ocr_results, avg_confidence)
        
        # Vote kết quả tốt nhất
        best_plate, best_confidence = self.vote_best_result(all_results)
        final_ocr_results = best_ocr_results[0] if best_ocr_results else []
        
        return best_plate, best_confidence, final_ocr_results


class ImprovedImagePreprocessor(ImagePreprocessor):
    """
    Phiên bản cải tiến của ImagePreprocessor
    """
    
    def preprocess_for_ocr(self, image):
        """
        Xử lý ảnh với nhiều kỹ thuật nâng cao hơn
        
        Returns:
            Tuple (danh sách ảnh biển số, tọa độ, ảnh gốc đã resize)
        """
        # Gọi hàm gốc
        plate_variants, coordinates, processed = super().preprocess_for_ocr(image)
        
        if not plate_variants:
            return None, None, processed
        
        # Thêm các biến thể nâng cao
        enhanced_variants = list(plate_variants)
        
        # Lấy ảnh biển số gốc
        if coordinates:
            x, y, w, h = coordinates
            plate_img = processed[y:y+h, x:x+w]
            
            # Biến thể 7: Morphological gradient (làm nổi cạnh chữ)
            if len(plate_img.shape) == 3:
                gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
            else:
                gray = plate_img
            
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
            _, binary = cv2.threshold(gradient, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            enhanced_variants.append(binary)
            
            # Biến thể 8: Bilateral filter + adaptive threshold
            bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
            adaptive = cv2.adaptiveThreshold(
                bilateral, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            enhanced_variants.append(adaptive)
            
            # Biến thể 9: Resize lớn hơn (tốt cho OCR)
            if w < 400:
                scale = 400 / w
                large = cv2.resize(plate_img, None, fx=scale, fy=scale, 
                                 interpolation=cv2.INTER_CUBIC)
                enhanced_variants.append(large)
        
        return enhanced_variants, coordinates, processed


def create_improved_detector(use_gpu=False):
    """
    Tạo detector cải tiến
    
    Args:
        use_gpu: Sử dụng GPU (nhanh hơn và chính xác hơn)
        
    Returns:
        Tuple (preprocessor, detector)
    """
    print("🚀 Khởi tạo detector cải tiến...")
    print("   - Thêm tiếng Việt")
    print("   - Tăng số biến thể ảnh")
    print("   - Cải thiện preprocessing")
    print("   - Tăng ngưỡng confidence")
    
    preprocessor = ImprovedImagePreprocessor()
    detector = ImprovedLicensePlateDetector(
        languages=['en', 'vi'],  # Thêm tiếng Việt
        gpu=use_gpu
    )
    
    print("✅ Sẵn sàng!")
    return preprocessor, detector


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    print("=" * 70)
    print("TEST DETECTOR CẢI TIẾN")
    print("=" * 70)
    
    # Tạo detector
    preprocessor, detector = create_improved_detector(use_gpu=False)
    
    # Test với ảnh
    test_image = "archive/images/train/carlong_0001.png"
    
    if not Path(test_image).exists():
        print(f"✗ Không tìm thấy ảnh: {test_image}")
        sys.exit(1)
    
    print(f"\nTest với: {Path(test_image).name}")
    
    # Đọc ảnh
    image = cv2.imread(test_image)
    
    # Preprocessing
    print("\n1. Preprocessing...")
    plate_variants, coords, processed = preprocessor.preprocess_for_ocr(image)
    
    if plate_variants:
        print(f"   ✓ Phát hiện biển số")
        print(f"   ✓ Tạo {len(plate_variants)} biến thể (nhiều hơn bản gốc)")
        
        # OCR
        print("\n2. OCR với detector cải tiến...")
        license_text, confidence, ocr_results = detector.detect_plate_enhanced(plate_variants)
        
        print(f"\n{'='*70}")
        print(f"KẾT QUẢ:")
        print(f"   Biển số: {license_text}")
        print(f"   Độ tin cậy: {confidence:.2%}")
        print(f"   Số kết quả OCR: {len(ocr_results)}")
        print(f"{'='*70}")
    else:
        print("   ✗ Không phát hiện biển số")
