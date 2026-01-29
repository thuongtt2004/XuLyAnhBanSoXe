"""
Module xử lý tiền xử lý ảnh cho nhận diện biển số xe
Optimized version with config
"""
import cv2
import numpy as np
from config import PreprocessingConfig, ValidationConfig
from utils import calculate_image_quality, resize_if_needed, ensure_bgr


class ImagePreprocessor:
    """Lớp xử lý tiền xử lý ảnh"""
    
    def __init__(self, debug=False):
        self.debug = debug
        if debug:
            import os
            self.debug_dir = "d:\\game\\debug"
            os.makedirs(self.debug_dir, exist_ok=True)
    
    def deskew_image(self, image):
        """
        Sửa ảnh bị nghêng
        
        Args:
            image: Ảnh đầu vào
            
        Returns:
            Ảnh đã được sửa nghêng
        """
        # Chuyển sang ảnh xám nếu cần
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Phát hiện cạnh
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Phát hiện các đường thẳng
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is None:
            return image
        
        # Tính góc trung bình của các đường thẳng
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            angles.append(angle)
        
        if not angles:
            return image
        
        # Lấy góc trung vị (loại bỏ outliers)
        median_angle = np.median(angles)
        
        # Chỉ xoay nếu góc nghêng đáng kể (>2 độ)
        if abs(median_angle) > 2:
            # Xoay ảnh
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        
        return image
    
    def reduce_glare(self, image):
        """
        Giảm phản chiếu ánh sáng
        
        Args:
            image: Ảnh đầu vào
            
        Returns:
            Ảnh đã giảm phản chiếu
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Phát hiện vùng sáng (glare)
        _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Inpaint vùng sáng
        result = cv2.inpaint(image, bright_mask, 3, cv2.INPAINT_TELEA)
        
        return result
    
    def sharpen_image(self, image, strength=9):
        """
        Làm sắc nét ảnh với cường độ tùy chỉnh
        
        Args:
            image: Ảnh đầu vào
            strength: Cường độ sharpen (default from config)
            
        Returns:
            Ảnh đã được làm sắc nét
        """
        # Kernel sharpen với cường độ tùy chỉnh
        kernel = np.array([[-1, -1, -1],
                          [-1, strength, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened
    
    def resize_image(self, image, width=800):
        """
        Thay đổi kích thước ảnh để xử lý nhanh hơn
        
        Args:
            image: Ảnh đầu vào
            width: Chiều rộng mong muốn
            
        Returns:
            Ảnh đã được resize
        """
        ratio = width / image.shape[1]
        height = int(image.shape[0] * ratio)
        return cv2.resize(image, (width, height))
    
    def convert_to_grayscale(self, image):
        """
        Chuyển ảnh sang ảnh xám
        
        Args:
            image: Ảnh màu đầu vào
            
        Returns:
            Ảnh xám
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def apply_bilateral_filter(self, image):
        """
        Áp dụng bộ lọc bilateral để giảm nhiễu nhưng vẫn giữ cạnh
        
        Args:
            image: Ảnh đầu vào
            
        Returns:
            Ảnh đã được lọc
        """
        return cv2.bilateralFilter(image, 11, 17, 17)
    
    def detect_edges(self, image):
        """
        Phát hiện cạnh bằng thuật toán Canny
        
        Args:
            image: Ảnh đầu vào
            
        Returns:
            Ảnh cạnh
        """
        return cv2.Canny(image, 30, 200)
    
    def find_contours(self, image):
        """
        Tìm các contour trong ảnh
        
        Args:
            image: Ảnh cạnh
            
        Returns:
            Danh sách contours
        """
        contours, _ = cv2.findContours(
            image.copy(), 
            cv2.RETR_TREE, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        # Sắp xếp contours theo diện tích giảm dần
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
        return contours
    
    def find_plate_by_color(self, image):
        """
        Tìm biển số dựa vào màu trắng (biển số VN)
        
        Args:
            image: Ảnh đầu vào (màu)
            
        Returns:
            Mask của vùng biển số hoặc None
        """
        # Chuyển sang HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Range 1: Màu trắng tiêu chuẩn
        lower_white1 = np.array([0, 0, 180])
        upper_white1 = np.array([180, 30, 255])
        mask1 = cv2.inRange(hsv, lower_white1, upper_white1)
        
        # Range 2: Màu trắng ngà (vàng nhạt)
        lower_white2 = np.array([15, 0, 170])
        upper_white2 = np.array([30, 40, 255])
        mask2 = cv2.inRange(hsv, lower_white2, upper_white2)
        
        # Range 3: Màu bạc/xám sáng
        lower_gray = np.array([0, 0, 150])
        upper_gray = np.array([180, 50, 200])
        mask3 = cv2.inRange(hsv, lower_gray, upper_gray)
        
        # Kết hợp các mask
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.bitwise_or(mask, mask3)
        
        # Morphological operations để làm sạch
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        return mask
    
    def find_license_plate_contour(self, contours):
        """
        Tìm contour của biển số xe với nhiều tiêu chí
        
        Args:
            contours: Danh sách contours
            
        Returns:
            Contour của biển số xe hoặc None
        """
        license_plate_candidates = []
        
        for contour in contours:
            # Tính chu vi và diện tích
            perimeter = cv2.arcLength(contour, True)
            area = cv2.contourArea(contour)
            
            # Bỏ qua contour quá nhỏ - GIẢM từ 500 xuống 200
            if area < 200:
                continue
            
            # Xấp xỉ hình dạng
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            # Kiểm tra tỷ lệ khung hình
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Mở RỘNG aspect ratio: 1.2 đến 6.0 (thêm cả biển số 1 dòng & 2 dòng)
            if 1.2 <= aspect_ratio <= 6.0:
                # Nếu có 4 đỉnh - ưu tiên cao
                if len(approx) == 4:
                    score = area * 2  # Bonus cho 4 cạnh
                    license_plate_candidates.append((approx, score, area))
                # Nếu có từ 3-8 đỉnh - vẫn chấp nhận
                elif 3 <= len(approx) <= 8:
                    score = area
                    license_plate_candidates.append((approx, score, area))
        
        # Nếu không tìm thấy, thử với bất kỳ contour nào có aspect ratio hợp lý
        if not license_plate_candidates:
            for contour in contours[:15]:  # Xét 15 contour lớn nhất
                area = cv2.contourArea(contour)
                if area < 200:
                    continue
                    
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                if 1.2 <= aspect_ratio <= 6.0:
                    # Tạo contour từ bounding box
                    rect_contour = np.array([
                        [[x, y]], [[x + w, y]], 
                        [[x + w, y + h]], [[x, y + h]]
                    ])
                    score = area
                    license_plate_candidates.append((rect_contour, score, area))
        
        # Sắp xếp theo điểm và trả về tốt nhất
        if license_plate_candidates:
            license_plate_candidates.sort(key=lambda x: x[1], reverse=True)
            return license_plate_candidates[0][0]
        
        return None
    
    def extract_license_plate(self, image, contour):
        """
        Trích xuất vùng biển số xe từ ảnh
        
        Args:
            image: Ảnh gốc
            contour: Contour của biển số xe
            
        Returns:
            Ảnh biển số xe đã được cắt
        """
        # Tìm bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Mở rộng bounding box một chút (padding 5%)
        padding_x = int(w * 0.05)
        padding_y = int(h * 0.15)
        
        x = max(0, x - padding_x)
        y = max(0, y - padding_y)
        w = min(image.shape[1] - x, w + 2 * padding_x)
        h = min(image.shape[0] - y, h + 2 * padding_y)
        
        # Cắt vùng biển số xe
        license_plate = image[y:y+h, x:x+w]
        
        return license_plate, (x, y, w, h)
    
    def enhance_plate(self, plate_image):
        """
        Cải thiện chất lượng ảnh biển số - ENHANCED VERSION
        Tối ưu để OCR đọc tốt hơn
        
        Args:
            plate_image: Ảnh biển số
            
        Returns:
            Ảnh biển số đã được cải thiện
        """
        # Chuyển sang ảnh xám nếu cần
        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image
        
        # Resize lên nếu ảnh quá nhỏ - AGGRESSIVE
        target_width = PreprocessingConfig.MIN_RESIZE_WIDTH * 2  # 600px
        gray = resize_if_needed(gray, target_width)
        
        # Remove border
        h, w = gray.shape
        border_size = int(min(h, w) * 0.05)
        if border_size > 2:
            gray = gray[border_size:-border_size, border_size:-border_size]
        
        # STEP 1: Denoise FIRST
        denoised = cv2.fastNlMeansDenoising(
            gray, None,
            PreprocessingConfig.DENOISE_H,
            PreprocessingConfig.DENOISE_TEMPLATE_SIZE,
            PreprocessingConfig.DENOISE_SEARCH_SIZE
        )
        
        # STEP 2: CLAHE - AGGRESSIVE
        clahe = cv2.createCLAHE(
            clipLimit=PreprocessingConfig.CLAHE_CLIP_LIMIT * 1.5,  # Boost
            tileGridSize=PreprocessingConfig.CLAHE_TILE_SIZE
        )
        enhanced = clahe.apply(denoised)
        
        # STEP 3: Unsharp mask - VERY STRONG
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 3.0)
        enhanced = cv2.addWeighted(enhanced, 2.5, gaussian, -1.5, 0)  # Very strong
        
        # STEP 4: Contrast stretching
        min_val, max_val = np.percentile(enhanced, [2, 98])  # Remove outliers
        if max_val > min_val:
            enhanced = np.clip((enhanced - min_val) * 255.0 / (max_val - min_val), 0, 255).astype(np.uint8)
        
        # STEP 5: Adaptive threshold - MULTIPLE methods
        # Method 1: Otsu
        _, thresh1 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Method 2: Adaptive Gaussian
        thresh2 = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Method 3: Adaptive Mean
        thresh3 = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Choose best threshold (most white pixels = clearest text)
        white_counts = [
            cv2.countNonZero(thresh1),
            cv2.countNonZero(thresh2),
            cv2.countNonZero(thresh3)
        ]
        best_idx = white_counts.index(max(white_counts))
        best_thresh = [thresh1, thresh2, thresh3][best_idx]
        
        # STEP 6: Morphological operations - LIGHT
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morphed = cv2.morphologyEx(best_thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # STEP 7: Final denoise
        final = cv2.fastNlMeansDenoising(morphed, None, 5, 7, 21)
        
        # STEP 8: Add border
        bordered = cv2.copyMakeBorder(
            final, 20, 20, 20, 20,  # Larger border
            cv2.BORDER_CONSTANT, value=255
        )
        
        return bordered
    
    def preprocess_for_ocr(self, image):
        """
        Xử lý đầy đủ ảnh để chuẩn bị cho OCR với nhiều phương pháp
        
        Args:
            image: Ảnh đầu vào
            
        Returns:
            Tuple (danh sách ảnh biển số, tọa độ, ảnh gốc đã resize)
        """
        # Resize ảnh
        resized = self.resize_image(image)
        
        # Sửa nghêng
        deskewed = self.deskew_image(resized)
        
        # Chuyển sang ảnh xám
        gray = self.convert_to_grayscale(deskewed)
        
        # Lọc nhiễu
        filtered = self.apply_bilateral_filter(gray)
        
        # Phát hiện cạnh
        edges = self.detect_edges(filtered)
        
        # Tìm contours
        contours = self.find_contours(edges)
        
        # Tìm contour biển số xe
        plate_contour = self.find_license_plate_contour(contours)
        
        if plate_contour is None:
            return None, None, deskewed
        
        # Trích xuất biển số
        plate_image, coordinates = self.extract_license_plate(deskewed, plate_contour)
        
        # Tạo nhiều phiên bản xử lý khác nhau
        plate_variants = []
        
        # 0. Giảm phản chiếu trước (nếu có)
        deglared = self.reduce_glare(plate_image)
        
        # 1. Phiên bản chuẩn
        enhanced_plate = self.enhance_plate(deglared)
        plate_variants.append(enhanced_plate)
        
        # 2. Phiên bản sharpen
        sharpened = self.sharpen_image(deglared)
        enhanced_sharp = self.enhance_plate(sharpened)
        plate_variants.append(enhanced_sharp)
        
        # 3. Phiên bản resize lên 2x (luôn thêm, không chỉ khi nhỏ)
        large_plate = cv2.resize(deglared, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        enhanced_large = self.enhance_plate(large_plate)
        plate_variants.append(enhanced_large)
        
        # 4. Phiên bản với CLAHE mạnh hơn
        if len(deglared.shape) == 3:
            gray_plate = cv2.cvtColor(deglared, cv2.COLOR_BGR2GRAY)
        else:
            gray_plate = deglared
        clahe_strong = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4, 4))
        clahe_applied = clahe_strong.apply(gray_plate)
        _, binary = cv2.threshold(clahe_applied, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        plate_variants.append(binary)
        
        # 5. Phiên bản gamma correction (tối)
        gamma = 1.5
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
        gamma_corrected = cv2.LUT(gray_plate, table)
        enhanced_gamma = self.enhance_plate(gamma_corrected)
        plate_variants.append(enhanced_gamma)
        
        # 6. Phiên bản với nhiều threshold khác nhau
        _, binary2 = cv2.threshold(gray_plate, 127, 255, cv2.THRESH_BINARY)
        plate_variants.append(binary2)
        
        # 7. Phiên bản với morphological gradient (làm nổi cạnh chữ)
        kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        gradient = cv2.morphologyEx(gray_plate, cv2.MORPH_GRADIENT, kernel_morph)
        _, binary_grad = cv2.threshold(gradient, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        plate_variants.append(binary_grad)
        
        # 8. Phiên bản với bilateral filter + adaptive threshold
        bilateral = cv2.bilateralFilter(gray_plate, 9, 75, 75)
        adaptive = cv2.adaptiveThreshold(
            bilateral, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        plate_variants.append(adaptive)
        
        # 9. Phiên bản resize lớn hơn (400px width cho OCR tốt hơn)
        if deglared.shape[1] < 400:
            scale = 400 / deglared.shape[1]
            large_plate = cv2.resize(deglared, None, fx=scale, fy=scale, 
                                    interpolation=cv2.INTER_CUBIC)
            enhanced_large = self.enhance_plate(large_plate)
            plate_variants.append(enhanced_large)
        
        # 10. Phiên bản với edge enhancement (giúp phân biệt 5/6 rõ hơn)
        edges = cv2.Canny(gray_plate, 50, 150)
        edges_dilated = cv2.dilate(edges, np.ones((2,2), np.uint8), iterations=1)
        combined_edges = cv2.addWeighted(gray_plate, 0.7, edges_dilated, 0.3, 0)
        enhanced_edges = self.enhance_plate(combined_edges)
        plate_variants.append(enhanced_edges)
        
        # 11. Phiên bản với contrast stretching (tăng độ tương phản tối đa)
        min_val, max_val = np.min(gray_plate), np.max(gray_plate)
        if max_val > min_val:
            stretched = ((gray_plate - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            enhanced_stretched = self.enhance_plate(stretched)
            plate_variants.append(enhanced_stretched)
        
        return plate_variants, coordinates, deskewed
