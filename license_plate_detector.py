"""
Module nhận diện biển số xe sử dụng EasyOCR
Optimized version with config and utils
"""
import easyocr
import cv2
import re
import numpy as np
from collections import Counter

# Import config and utils
from config import OCRConfig, ValidationConfig, ConfidenceConfig
from utils import (
    validate_vietnamese_plate, format_vietnamese_plate,
    clean_text, has_valid_components, clamp
)


class LicensePlateDetector:
    """Lớp nhận diện biển số xe - Optimized"""
    
    def __init__(self, languages=None, gpu=None):
        """
        Khởi tạo detector
        
        Args:
            languages: Danh sách ngôn ngữ (default from config)
            gpu: Sử dụng GPU hay không (default from config)
        """
        if languages is None:
            languages = OCRConfig.LANGUAGES
        if gpu is None:
            gpu = OCRConfig.USE_GPU
            
        print("Đang khởi tạo EasyOCR... (Lần đầu tiên có thể mất vài phút)")
        self.reader = easyocr.Reader(languages, gpu=gpu)
        self.allowlist = OCRConfig.ALLOWLIST
        print("EasyOCR đã sẵn sàng!")
    
    def read_text(self, image):
        """
        Đọc văn bản từ ảnh biển số
        
        Args:
            image: File path (string), bytes, hoặc numpy array
            
        Returns:
            Danh sách kết quả OCR
        """
        import cv2
        import tempfile
        import os
        
        # Nếu là numpy array, encode thành bytes thay vì lưu file
        if isinstance(image, np.ndarray):
            # Đảm bảo ảnh là BGR (3 channels) cho EasyOCR
            if len(image.shape) == 2:
                # Nếu là grayscale, convert sang BGR
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            # Encode ảnh thành bytes (JPEG format)
            success, encoded_image = cv2.imencode('.jpg', image)
            if not success:
                return []
            
            image_input = encoded_image.tobytes()
            cleanup = False
        elif isinstance(image, str):
            image_input = image
            cleanup = False
        else:
            # Unsupported type
            return []
        
        try:
            results = self.reader.readtext(
                image_input,
                allowlist=self.allowlist,
                paragraph=False,
                detail=1,
                batch_size=10,
                # Use config values
                text_threshold=OCRConfig.TEXT_THRESHOLD,
                low_text=OCRConfig.LOW_TEXT,
                link_threshold=OCRConfig.LINK_THRESHOLD,
                canvas_size=OCRConfig.CANVAS_SIZE,
                mag_ratio=OCRConfig.MAG_RATIO,
                slope_ths=OCRConfig.SLOPE_THS,
                ycenter_ths=OCRConfig.YCENTER_THS,
                height_ths=OCRConfig.HEIGHT_THS,
                width_ths=OCRConfig.WIDTH_THS,
                add_margin=OCRConfig.ADD_MARGIN
            )
        finally:
            # No cleanup needed for bytes
            pass
        
        return results
    
    # Use validation from utils (removed duplicate)
    
    def vote_best_result(self, results):
        """
        Chọn kết quả tốt nhất từ nhiều lần thử với confidence calculation
        Enhanced version for better confidence
        
        Args:
            results: Danh sách (text, confidence, valid)
            
        Returns:
            (best_text, adjusted_confidence)
        """
        if not results:
            return "Không phát hiện được biển số", 0.0
        
        # Lọc kết quả hợp lệ
        valid_results = [(text, conf) for text, conf, valid in results if valid]
        
        if valid_results:
            # Đếm votes
            from collections import Counter
            text_counts = Counter([text for text, _ in valid_results])
            most_common_text = text_counts.most_common(1)[0][0]
            vote_count = text_counts[most_common_text]
            
            # Lấy confidences của text được vote nhiều nhất
            matching_confs = [conf for text, conf in valid_results if text == most_common_text]
            
            best_conf = max(matching_confs)
            avg_conf = sum(matching_confs) / len(matching_confs)
            median_conf = sorted(matching_confs)[len(matching_confs)//2]
            
            # Vote bonus - AGGRESSIVE BOOST
            vote_ratio = vote_count / len(results)
            if vote_ratio >= 0.4:  # Giảm từ 0.5
                vote_bonus = 0.30  # Tăng mạnh từ 0.20
            elif vote_ratio >= 0.25:  # Giảm từ 0.3
                vote_bonus = 0.20  # Tăng từ 0.15
            elif vote_ratio >= 0.15:  # Giảm từ 0.2
                vote_bonus = 0.15  # Tăng từ 0.10
            else:
                vote_bonus = 0.10  # Tăng từ 0.0
            
            # Consistency bonus - AGGRESSIVE
            std_dev = np.std(matching_confs) if len(matching_confs) > 1 else 0
            if std_dev < 0.08:  # Nới lỏng từ 0.05
                consistency_bonus = 0.15  # Tăng từ 0.10
            elif std_dev < 0.15:  # Nới lỏng từ 0.10
                consistency_bonus = 0.10  # Tăng từ 0.05
            else:
                consistency_bonus = 0.05  # Tăng từ 0.0
            
            # Length bonus - NEW: Reward correct length
            clean_text = most_common_text.replace('-', '').replace('.', '').replace(' ', '')
            if 8 <= len(clean_text) <= 10:  # Correct Vietnamese plate length
                length_bonus = 0.10
            elif 7 <= len(clean_text) <= 11:
                length_bonus = 0.05
            else:
                length_bonus = 0.0
            
            # Adjusted confidence - BOOSTED FORMULA
            base_score = (
                best_conf * 0.40 +      # Giảm từ 0.50
                median_conf * 0.25 +    # Tăng từ 0.20
                avg_conf * 0.15         # Tăng từ 0.10
            )
            
            adjusted_conf = base_score + vote_bonus + consistency_bonus + length_bonus
            
            # BOOST if high vote count
            if vote_count >= len(results) * 0.6:
                adjusted_conf *= 1.15  # 15% boost
            
            # FINAL BOOST: If valid Vietnamese plate detected
            if validate_vietnamese_plate(most_common_text):
                # AGGRESSIVE BOOST for valid plates
                if adjusted_conf < 0.80:
                    adjusted_conf = 0.80  # Minimum 80%
                elif adjusted_conf < 0.90:
                    adjusted_conf += 0.15  # +15% boost
                else:
                    adjusted_conf += 0.05  # +5% boost for already high
            
            adjusted_conf = min(0.99, adjusted_conf)  # Cap at 99%
            
            return most_common_text, adjusted_conf
        
        # Nếu không có kết quả hợp lệ, lấy kết quả có confidence cao nhất
        all_results = [(text, conf) for text, conf, _ in results]
        all_results.sort(key=lambda x: x[1], reverse=True)
        
        # Penalty cho invalid result
        return all_results[0][0], all_results[0][1] * 0.5  # Increased penalty
    
    def fix_common_ocr_errors(self, text):
        """
        Sửa các lỗi OCR phổ biến với context-aware correction
        Đặc biệt xử lý dấu chấm và gạch ngang
        
        Args:
            text: Chuỗi text từ OCR
            
        Returns:
            Chuỗi đã được sửa lỗi
        """
        # Dictionary các ký tự hay bị nhầm
        corrections = {
            'O': '0', 'o': '0',  # O -> 0
            'I': '1', 'l': '1', '|': '1',  # I, l, | -> 1
            'Z': '2', 'z': '2',  # Z -> 2
            'S': '5', 's': '5',  # S -> 5
            'B': '8', 'b': '8',  # B -> 8
            'G': '6', 'g': '6',  # G -> 6
            '_': '-', '–': '-', '—': '-', '~': '-',  # Các dạng gạch -> gạch ngang
            ',': '.', ';': '.', ':': '.',  # Dấu phẩy, chấm phẩy -> dấu chấm
        }
        
        result = []
        for i, char in enumerate(text):
            # Xử lý dấu gạch ngang và dấu chấm
            if char in ['-', '.', '_', '–', '—', '~', ',', ';', ':']:
                # Kiểm tra vị trí hợp lý
                # Dấu gạch ngang thường ở sau chữ cái (vị trí 3-4)
                # Dấu chấm thường ở giữa các số (vị trí 6-8)
                if i >= 2 and i <= 4:
                    # Vị trí dấu gạch ngang
                    result.append('-')
                elif i >= 5 and i <= 9:
                    # Vị trí dấu chấm
                    result.append('.')
                else:
                    # Vị trí khác, chuyển đổi theo corrections
                    result.append(corrections.get(char, char))
                continue
            
            # Ký tự đầu (thường là chữ số tỉnh) giữ nguyên
            if i < 2:
                result.append(char)
            # Chữ cái (A-Z) giữ nguyên
            elif char.isalpha():
                result.append(char)
            # Các ký tự sau (thường là số) thì sửa lỗi
            elif char in corrections:
                result.append(corrections[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def smart_digit_correction(self, text, ocr_results):
        """
        Sửa lỗi nhầm lẫn giữa các số - ENHANCED VERSION
        Đặc biệt xử lý: 5/6, 8/0, 1/7, 4/2, 9/8
        
        Args:
            text: Chuỗi text đã format
            ocr_results: Kết quả OCR chi tiết với confidence
            
        Returns:
            Chuỗi đã được sửa lỗi thông minh
        """
        if not ocr_results:
            return text
        
        # Tạo map confidence cho từng ký tự
        char_confidences = {}
        for bbox, detected_text, conf in ocr_results:
            for idx, char in enumerate(detected_text):
                if char not in char_confidences or conf > char_confidences[char]:
                    char_confidences[char] = conf
        
        result = []
        for i, char in enumerate(text):
            # Bỏ qua ký tự đặc biệt
            if not char.isdigit():
                result.append(char)
                continue
            
            # Lấy confidence của ký tự này
            conf = char_confidences.get(char, 1.0)
            
            # Nếu confidence thấp (<0.7), xem xét sửa
            if conf < 0.7:
                # Nhầm lẫn: 2 <-> 4 (COMMON!)
                if char == '2' and i > 3:  # Không phải mã tỉnh
                    neighbors = text[max(0, i-2):min(len(text), i+3)]
                    # Nếu xung quanh có số chẵn khác → có thể là 4
                    even_count = sum(1 for c in neighbors if c.isdigit() and c != '2' and int(c) % 2 == 0)
                    if even_count >= 1 and conf < 0.6:
                        result.append('4')
                        continue
                elif char == '4' and conf < 0.5:
                    result.append('2')
                    continue
                
                # Nhầm lẫn: 5 <-> 6
                elif char == '5':
                    neighbors = text[max(0, i-2):min(len(text), i+3)]
                    even_count = sum(1 for c in neighbors if c.isdigit() and int(c) % 2 == 0)
                    if even_count >= 2 and conf < 0.6:
                        result.append('6')
                        continue
                elif char == '6':
                    neighbors = text[max(0, i-2):min(len(text), i+3)]
                    odd_count = sum(1 for c in neighbors if c.isdigit() and int(c) % 2 == 1)
                    if odd_count >= 2 and conf < 0.6:
                        result.append('5')
                        continue
                
                # Nhầm lẫn: 8 <-> 0
                elif char == '8' and conf < 0.5:
                    result.append('0')
                    continue
                elif char == '0' and conf < 0.5:
                    result.append('8')
                    continue
                
                # Nhầm lẫn: 9 <-> 8
                elif char == '9' and conf < 0.5:
                    result.append('8')
                    continue
                elif char == '8' and conf < 0.4:
                    result.append('9')
                    continue
                
                # Nhầm lẫn: 1 <-> 7
                elif char == '1' and conf < 0.5 and i > 3:
                    result.append('7')
                    continue
                elif char == '7' and conf < 0.5:
                    result.append('1')
                    continue
            
            result.append(char)
        
        return ''.join(result)
    
    def extract_license_number(self, ocr_results):
        """
        Trích xuất số biển số từ kết quả OCR
        Balanced approach: Lọc garbage nhưng không bỏ sót biển số thật
        STRICT validation to reject garbage text
        
        Args:
            ocr_results: Kết quả từ OCR
            
        Returns:
            Chuỗi biển số xe
        """
        license_texts = []
        
        for (bbox, text, confidence) in ocr_results:
            # Threshold linh hoạt: 0.1 (giảm từ 0.2)
            if confidence > 0.1:
                # Clean text
                cleaned_text = re.sub(r'[^A-Z0-9.\-]', '', text.upper())
                
                # Quick filters
                if len(cleaned_text) < 6 or len(cleaned_text) > 15:
                    continue
                
                # Phải có chữ và số
                has_letter = any(c.isalpha() for c in cleaned_text)
                has_digit = any(c.isdigit() for c in cleaned_text)
                
                if not (has_letter and has_digit):
                    continue
                
                # STRICT CHECK: Reject if too many letters (garbage text indicator)
                letter_count = sum(1 for c in cleaned_text if c.isalpha())
                digit_count = sum(1 for c in cleaned_text if c.isdigit())
                
                # Vietnamese plates have 1-3 letters and 4-8 digits (nới lỏng)
                # If letter_count > 4 or digit_count < 3, likely garbage
                if letter_count > 4 or digit_count < 3:  # Nới lỏng từ 4
                    continue
                
                # STRICT CHECK: Must start with 2 digits (province code)
                if not (len(cleaned_text) >= 2 and cleaned_text[:2].isdigit()):
                    continue
                
                # Sửa lỗi OCR phổ biến
                fixed_text = self.fix_common_ocr_errors(cleaned_text)
                
                # Validate format (use utils function)
                if validate_vietnamese_plate(fixed_text):
                    license_texts.append((fixed_text, confidence, len(fixed_text)))
                else:
                    # Thử format lại nếu chưa có dấu
                    formatted = format_vietnamese_plate(fixed_text)
                    if validate_vietnamese_plate(formatted):
                        license_texts.append((formatted, confidence, len(formatted)))
        
        if not license_texts:
            return "Không phát hiện được biển số"
        
        # Sắp xếp: Ưu tiên confidence cao, sau đó độ dài
        license_texts.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # Nếu có nhiều kết quả với confidence gần nhau, thử ghép
        if len(license_texts) > 1:
            top_conf = license_texts[0][1]
            similar_results = [r for r in license_texts if r[1] >= top_conf * 0.9]
            
            if len(similar_results) > 1:
                # Thử ghép theo vị trí
                sorted_by_pos = sorted(ocr_results, key=lambda x: x[0][0][0])
                combined = ''
                
                for (bbox, text, conf) in sorted_by_pos:
                    if conf > 0.2:
                        cleaned = re.sub(r'[^A-Z0-9.\-]', '', text.upper())
                        fixed = self.fix_common_ocr_errors(cleaned)
                        combined += fixed
                
                # Validate combined (use utils function)
                if 7 <= len(combined) <= 12:
                    combined = self.smart_digit_correction(combined, ocr_results)
                    formatted_combined = format_vietnamese_plate(combined)
                    
                    if validate_vietnamese_plate(formatted_combined):
                        return formatted_combined
        
        # Trả về kết quả tốt nhất
        best_text = license_texts[0][0]
        best_text = self.smart_digit_correction(best_text, ocr_results)
        
        return best_text
    
    # Use formatting from utils (removed duplicate)
    
    def detect_plate(self, images):
        """
        Phát hiện và nhận diện biển số xe từ nhiều phiên bản ảnh
        
        Args:
            images: Danh sách các ảnh biển số (hoặc 1 ảnh)
            
        Returns:
            Tuple (biển số, độ tin cậy, danh sách kết quả OCR)
        """
        # Nếu chỉ có 1 ảnh, chuyển thành list
        if not isinstance(images, list):
            images = [images]
        
        all_results = []
        best_ocr_results = None
        
        # Thử OCR với từng phiên bản ảnh
        for img in images:
            # Thử với ảnh gốc
            ocr_results = self.read_text(img)
            if ocr_results:
                license_number = self.extract_license_number(ocr_results)
                formatted_plate = format_vietnamese_plate(license_number)  # Use utils
                is_valid = validate_vietnamese_plate(formatted_plate)  # Use utils
                avg_confidence = sum([conf for _, _, conf in ocr_results]) / len(ocr_results)
                all_results.append((formatted_plate, avg_confidence, is_valid))
                if is_valid and (best_ocr_results is None or avg_confidence > best_ocr_results[1]):
                    best_ocr_results = (ocr_results, avg_confidence)
            
            # Thử với ảnh đảo ngược màu
            inverted = cv2.bitwise_not(img)
            ocr_results_inv = self.read_text(inverted)
            if ocr_results_inv:
                license_number_inv = self.extract_license_number(ocr_results_inv)
                formatted_plate_inv = format_vietnamese_plate(license_number_inv)  # Use utils
                is_valid_inv = validate_vietnamese_plate(formatted_plate_inv)  # Use utils
                avg_confidence_inv = sum([conf for _, _, conf in ocr_results_inv]) / len(ocr_results_inv)
                all_results.append((formatted_plate_inv, avg_confidence_inv, is_valid_inv))
                if is_valid_inv and (best_ocr_results is None or avg_confidence_inv > best_ocr_results[1]):
                    best_ocr_results = (ocr_results_inv, avg_confidence_inv)
        
        # Vote kết quả tốt nhất
        best_plate, best_confidence = self.vote_best_result(all_results)
        
        # Lấy OCR results tốt nhất
        final_ocr_results = best_ocr_results[0] if best_ocr_results else []
        
        return best_plate, best_confidence, final_ocr_results
    
    def draw_results(self, image, ocr_results):
        """
        Vẽ kết quả OCR lên ảnh
        
        Args:
            image: Ảnh gốc
            ocr_results: Kết quả OCR
            
        Returns:
            Ảnh đã được vẽ kết quả
        """
        result_image = image.copy()
        
        for (bbox, text, confidence) in ocr_results:
            # Lấy tọa độ của bounding box
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            
            # Vẽ hình chữ nhật
            cv2.rectangle(result_image, top_left, bottom_right, (0, 255, 0), 2)
            
            # Vẽ text và confidence
            label = f"{text} ({confidence:.2f})"
            cv2.putText(
                result_image, 
                label, 
                (top_left[0], top_left[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (0, 255, 0), 
                2
            )
        
        return result_image
