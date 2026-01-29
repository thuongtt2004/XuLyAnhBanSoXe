"""
Ứng dụng nhận diện biển số xe với giao diện đồ họa
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import os
from preprocess_image import ImagePreprocessor
from license_plate_detector import LicensePlateDetector


class LicensePlateApp:
    """Lớp ứng dụng nhận diện biển số xe"""
    
    def __init__(self, root):
        """
        Khởi tạo ứng dụng
        
        Args:
            root: Cửa sổ Tkinter chính
        """
        self.root = root
        self.root.title("Ứng Dụng Nhận Diện Biển Số Xe")
        self.root.geometry("1200x700")
        
        # Khởi tạo các biến
        self.current_image = None
        self.result_image = None
        self.preprocessor = ImagePreprocessor()
        self.detector = None
        
        # Tạo giao diện
        self.create_widgets()
        
        # Khởi tạo detector trong background
        self.initialize_detector()
    
    def initialize_detector(self):
        """Khởi tạo detector OCR"""
        self.status_label.config(text="Đang khởi tạo EasyOCR...")
        self.root.update()
        
        try:
            # Sử dụng cả tiếng Anh và tiếng Việt để tăng độ chính xác
            self.detector = LicensePlateDetector(languages=['en', 'vi'], gpu=False)
            self.status_label.config(text="Sẵn sàng! Hãy chọn ảnh để nhận diện.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi tạo EasyOCR: {str(e)}")
            self.status_label.config(text="Lỗi khởi tạo!")
    
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        
        # Frame tiêu đề
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        
        title_label = tk.Label(
            title_frame,
            text="🚗 NHẬN DIỆN BIỂN SỐ XE 🚗",
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Frame nút điều khiển
        control_frame = tk.Frame(self.root, bg='#ecf0f1', height=60)
        control_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
        
        self.upload_btn = tk.Button(
            control_frame,
            text="📁 Chọn Ảnh",
            command=self.upload_image,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        self.detect_btn = tk.Button(
            control_frame,
            text="🔍 Nhận Diện",
            command=self.detect_license_plate,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.detect_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = tk.Button(
            control_frame,
            text="💾 Lưu Kết Quả",
            command=self.save_result,
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            control_frame,
            text="🗑️ Xóa",
            command=self.clear_all,
            font=('Arial', 12, 'bold'),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame hiển thị ảnh
        image_frame = tk.Frame(self.root, bg='#ecf0f1')
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Ảnh gốc
        left_frame = tk.LabelFrame(
            image_frame,
            text="Ảnh Gốc",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_canvas = tk.Canvas(left_frame, bg='white')
        self.original_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Ảnh kết quả
        right_frame = tk.LabelFrame(
            image_frame,
            text="Kết Quả Nhận Diện",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.result_canvas = tk.Canvas(right_frame, bg='white')
        self.result_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame kết quả text
        result_text_frame = tk.Frame(self.root, bg='#ecf0f1')
        result_text_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            result_text_frame,
            text="Biển Số Xe:",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=5)
        
        self.result_label = tk.Label(
            result_text_frame,
            text="",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#e74c3c',
            relief=tk.SUNKEN,
            width=30,
            height=2
        )
        self.result_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            result_text_frame,
            text="Độ tin cậy:",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=5)
        
        self.confidence_label = tk.Label(
            result_text_frame,
            text="",
            font=('Arial', 14),
            bg='white',
            relief=tk.SUNKEN,
            width=15,
            height=2
        )
        self.confidence_label.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame,
            text="Đang khởi tạo...",
            font=('Arial', 10),
            bg='#34495e',
            fg='white',
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def upload_image(self):
        """Upload ảnh từ file"""
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh biển số xe",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Đọc ảnh
                self.current_image = cv2.imread(file_path)
                
                if self.current_image is None:
                    raise ValueError("Không thể đọc ảnh")
                
                # Hiển thị ảnh gốc
                self.display_image(self.current_image, self.original_canvas)
                
                # Kích hoạt nút nhận diện
                self.detect_btn.config(state=tk.NORMAL)
                
                # Reset kết quả
                self.result_label.config(text="")
                self.confidence_label.config(text="")
                self.result_canvas.delete("all")
                
                self.status_label.config(text=f"Đã tải ảnh: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải ảnh: {str(e)}")
    
    def detect_license_plate(self):
        """Nhận diện biển số xe"""
        if self.current_image is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh trước!")
            return
        
        if self.detector is None:
            messagebox.showwarning("Cảnh báo", "EasyOCR chưa sẵn sàng!")
            return
        
        try:
            self.status_label.config(text="Đang xử lý ảnh...")
            self.root.update()
            
            # Tiền xử lý ảnh - trả về nhiều phiên bản
            plate_images, coordinates, processed_image = self.preprocessor.preprocess_for_ocr(
                self.current_image
            )
            
            if plate_images is None or not plate_images:
                messagebox.showinfo(
                    "Thông báo",
                    "Không tìm thấy biển số xe trong ảnh!\n\n" +
                    "Gợi ý:\n" +
                    "- Đảm bảo biển số xe rõ ràng trong ảnh\n" +
                    "- Thử với ảnh khác có biển số rõ hơn"
                )
                self.status_label.config(text="Không tìm thấy biển số")
                return
            
            self.status_label.config(text="Đang nhận diện biển số...")
            self.root.update()
            
            # Nhận diện biển số với nhiều phiên bản ảnh
            license_number, confidence, ocr_results = self.detector.detect_plate(plate_images)
            
            # Hiển thị kết quả
            self.result_label.config(text=license_number)
            self.confidence_label.config(text=f"{confidence * 100:.2f}%")
            
            # Vẽ kết quả lên ảnh
            result_img = processed_image.copy()
            
            if coordinates:
                x, y, w, h = coordinates
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
            
            self.result_image = result_img
            self.display_image(result_img, self.result_canvas)
            
            # Kích hoạt nút lưu
            self.save_btn.config(state=tk.NORMAL)
            
            self.status_label.config(
                text=f"Nhận diện thành công: {license_number} (Độ tin cậy: {confidence * 100:.2f}%)"
            )
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi nhận diện: {str(e)}")
            self.status_label.config(text="Lỗi nhận diện!")
    
    def display_image(self, image, canvas):
        """
        Hiển thị ảnh lên canvas
        
        Args:
            image: Ảnh OpenCV
            canvas: Canvas Tkinter
        """
        # Chuyển đổi BGR sang RGB
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Resize ảnh để vừa với canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 500
        if canvas_height <= 1:
            canvas_height = 400
        
        img_height, img_width = image_rgb.shape[:2]
        
        # Tính tỷ lệ
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio * 0.9)
        new_height = int(img_height * ratio * 0.9)
        
        # Resize
        resized_image = cv2.resize(image_rgb, (new_width, new_height))
        
        # Chuyển sang PIL Image
        pil_image = Image.fromarray(resized_image)
        
        # Chuyển sang PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # Hiển thị lên canvas
        canvas.delete("all")
        canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=photo,
            anchor=tk.CENTER
        )
        
        # Giữ reference để tránh bị garbage collect
        canvas.image = photo
    
    def save_result(self):
        """Lưu ảnh kết quả"""
        if self.result_image is None:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả để lưu!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Lưu kết quả",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.result_image)
                messagebox.showinfo("Thành công", f"Đã lưu kết quả tại:\n{file_path}")
                self.status_label.config(text=f"Đã lưu: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu ảnh: {str(e)}")
    
    def clear_all(self):
        """Xóa tất cả"""
        self.current_image = None
        self.result_image = None
        
        self.original_canvas.delete("all")
        self.result_canvas.delete("all")
        
        self.result_label.config(text="")
        self.confidence_label.config(text="")
        
        self.detect_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        
        self.status_label.config(text="Đã xóa tất cả. Sẵn sàng cho ảnh mới.")


def main():
    """Hàm main để chạy ứng dụng"""
    root = tk.Tk()
    app = LicensePlateApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
