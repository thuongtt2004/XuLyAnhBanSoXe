"""
License Plate Recognition App với YOLO Detection - Modern UI
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
from pathlib import Path

# Import detectors
from license_plate_detector import LicensePlateDetector
try:
    from yolo_detector import YOLOPlateDetector, integrate_yolo_detection
    YOLO_AVAILABLE = True
except:
    YOLO_AVAILABLE = False

class ModernButton(tk.Canvas):
    """Custom modern button with hover effect"""
    def __init__(self, parent, text, command, bg_color, hover_color, **kwargs):
        super().__init__(parent, height=50, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text = text
        
        # Draw button
        self.rect = self.create_rectangle(0, 0, 200, 50, fill=bg_color, outline="")
        self.text_id = self.create_text(100, 25, text=text, fill="white", 
                                        font=("Segoe UI", 11, "bold"))
        
        # Bind events
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.config(cursor="hand2")
    
    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_color)
    
    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.bg_color)

class LicensePlateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 Nhận Diện Biển Số Xe - AI Enhanced")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f5f6fa")
        
        # Modern colors
        self.colors = {
            'primary': '#667eea',
            'primary_dark': '#5568d3',
            'success': '#48bb78',
            'success_dark': '#38a169',
            'warning': '#ed8936',
            'warning_dark': '#dd6b20',
            'danger': '#f56565',
            'bg': '#f5f6fa',
            'card': '#ffffff',
            'text': '#2d3748',
            'text_light': '#718096'
        }
        
        # Check for YOLO model
        self.yolo_model_path = "d:/game/runs/license_plate/weights/best.pt"
        self.use_yolo = YOLO_AVAILABLE and Path(self.yolo_model_path).exists()
        
        # Initialize detectors
        self.ocr_detector = LicensePlateDetector(languages=['en', 'vi'], gpu=False)
        
        if self.use_yolo:
            self.yolo_detector = YOLOPlateDetector(self.yolo_model_path)
            detection_method = "YOLO AI Model"
            method_icon = "🚀"
        else:
            self.yolo_detector = None
            detection_method = "OpenCV Detection"
            method_icon = "🔧"
        
        self.setup_ui(detection_method, method_icon)
        
        self.image_path = None
        self.detected_text = None
    
    def setup_ui(self, detection_method, method_icon):
        """Setup modern UI"""
        
        # ===== HEADER =====
        header = tk.Frame(self.root, bg=self.colors['primary'], height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(
            header,
            text="🚗 NHẬN DIỆN BIỂN SỐ XE",
            font=("Segoe UI", 24, "bold"),
            bg=self.colors['primary'],
            fg="white"
        )
        title.pack(pady=(15, 5))
        
        # Subtitle
        subtitle = tk.Label(
            header,
            text=f"{method_icon} {detection_method} • Độ chính xác cao • Xử lý nhanh",
            font=("Segoe UI", 10),
            bg=self.colors['primary'],
            fg="#e0e7ff"
        )
        subtitle.pack()
        
        # ===== MAIN CONTENT =====
        content = tk.Frame(self.root, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Image
        left_panel = tk.Frame(content, bg=self.colors['card'], relief=tk.FLAT)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Image header
        img_header = tk.Frame(left_panel, bg=self.colors['card'])
        img_header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(
            img_header,
            text="📸 Ảnh đầu vào",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor=tk.W)
        
        # Image display area
        self.image_frame = tk.Frame(left_panel, bg="#f7fafc", relief=tk.FLAT)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.image_label = tk.Label(
            self.image_frame,
            text="Chưa có ảnh\n\n📁 Nhấn 'Tải ảnh' để bắt đầu",
            font=("Segoe UI", 11),
            fg=self.colors['text_light'],
            bg="#f7fafc"
        )
        self.image_label.pack(expand=True)
        
        # Right panel - Results
        right_panel = tk.Frame(content, bg=self.colors['card'], width=350, relief=tk.FLAT)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Results header
        result_header = tk.Frame(right_panel, bg=self.colors['card'])
        result_header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(
            result_header,
            text="📋 Kết quả nhận diện",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor=tk.W)
        
        # Result display
        result_container = tk.Frame(right_panel, bg="#f7fafc")
        result_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(result_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(
            result_container,
            font=("Consolas", 10),
            bg="#f7fafc",
            fg=self.colors['text'],
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)
        
        # Initial message
        self.result_text.insert(tk.END, "Chờ xử lý...\n\n")
        self.result_text.insert(tk.END, "� Hướng dẫn:\n")
        self.result_text.insert(tk.END, "1. Tải ảnh lên\n")
        self.result_text.insert(tk.END, "2. Nhấn 'Nhận diện'\n")
        self.result_text.insert(tk.END, "3. Xem kết quả\n")
        self.result_text.config(state=tk.DISABLED)
        
        # ===== BUTTON BAR =====
        button_bar = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        button_bar.pack(fill=tk.X, padx=20, pady=(0, 20))
        button_bar.pack_propagate(False)
        
        # Center buttons
        button_container = tk.Frame(button_bar, bg=self.colors['bg'])
        button_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Upload button
        self.upload_btn = ModernButton(
            button_container,
            "📁 Tải ảnh lên",
            self.upload_image,
            self.colors['primary'],
            self.colors['primary_dark'],
            width=200
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Detect button
        self.detect_btn = ModernButton(
            button_container,
            "🔍 Nhận diện",
            self.detect_license_plate,
            self.colors['success'],
            self.colors['success_dark'],
            width=200
        )
        self.detect_btn.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_btn = ModernButton(
            button_container,
            "💾 Lưu kết quả",
            self.save_result,
            self.colors['warning'],
            self.colors['warning_dark'],
            width=200
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # ===== STATUS BAR =====
        status_bar = tk.Frame(self.root, bg=self.colors['card'], height=30)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_bar,
            text="✅ Sẵn sàng",
            font=("Segoe UI", 9),
            bg=self.colors['card'],
            fg=self.colors['text_light'],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=15)
    
    def update_result(self, text, clear=True):
        """Update result text"""
        self.result_text.config(state=tk.NORMAL)
        if clear:
            self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END)
    
    def upload_image(self):
        """Tải ảnh từ máy tính"""
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh biển số xe",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.update_result("✅ Ảnh đã được tải!\n\n📸 File: " + Path(file_path).name + "\n\n💡 Nhấn 'Nhận diện' để bắt đầu xử lý.")
            self.status_label.config(text=f"📁 Đã tải: {Path(file_path).name}")
    
    def display_image(self, image_path):
        """Hiển thị ảnh trong giao diện"""
        image = Image.open(image_path)
        
        # Resize to fit
        max_width = 600
        max_height = 500
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(image)
        
        self.image_label.config(image=photo, text="", bg="#f7fafc")
        self.image_label.image = photo
    
    def detect_license_plate(self):
        """Nhận diện biển số xe"""
        if not self.image_path:
            messagebox.showwarning("⚠️ Cảnh báo", "Vui lòng tải ảnh lên trước!")
            return
        
        self.update_result("⏳ Đang xử lý...\n\n🔄 Vui lòng đợi...")
        self.status_label.config(text="⏳ Đang xử lý...")
        self.root.update()
        
        try:
            if self.use_yolo and self.yolo_detector.available:
                # Sử dụng YOLO
                license_text, confidence, method = self.detect_with_yolo()
                
                if license_text:
                    self.detected_text = license_text
                    result = f"✅ PHÁT HIỆN THÀNH CÔNG!\n\n"
                    result += f"{'='*35}\n"
                    result += f"📋 BIỂN SỐ: {license_text}\n"
                    result += f"{'='*35}\n\n"
                    result += f"🎯 Độ tin cậy: {confidence:.1%}\n"
                    result += f"🔧 Phương pháp: {method}\n"
                    result += f"🚀 Engine: YOLO AI\n\n"
                    result += f"💡 Kết quả đã được tối ưu với:\n"
                    result += f"  • Smart digit correction\n"
                    result += f"  • Auto format dấu\n"
                    result += f"  • 11 preprocessing variants\n"
                    self.update_result(result)
                    self.status_label.config(text=f"✅ Hoàn tất: {license_text}")
                else:
                    # Fallback to OpenCV
                    self.update_result("⚠️ YOLO không phát hiện\n\n🔄 Đang thử OpenCV...\n")
                    self.root.update()
                    self.detect_with_opencv()
            else:
                # Sử dụng OpenCV
                self.detect_with_opencv()
                
        except Exception as e:
            result = f"❌ LỖI XẢY RA!\n\n"
            result += f"Chi tiết: {str(e)}\n\n"
            result += f"💡 Gợi ý:\n"
            result += f"  • Kiểm tra ảnh có hợp lệ\n"
            result += f"  • Thử ảnh khác\n"
            result += f"  • Khởi động lại ứng dụng\n"
            self.update_result(result)
            self.status_label.config(text="❌ Lỗi xử lý")
    
    def detect_with_yolo(self):
        """Nhận diện bằng YOLO"""
        return integrate_yolo_detection(
            self.image_path,
            self.ocr_detector,
            self.yolo_model_path
        )
    
    def detect_with_opencv(self):
        """Nhận diện bằng OpenCV"""
        from preprocess_image import ImagePreprocessor
        import cv2
        
        image = cv2.imread(self.image_path)
        if image is None:
            self.update_result("❌ Không thể đọc ảnh!\n\nVui lòng thử ảnh khác.")
            self.status_label.config(text="❌ Lỗi đọc ảnh")
            return
        
        preprocessor = ImagePreprocessor()
        plate_images, coords, processed = preprocessor.preprocess_for_ocr(image)
        
        if not plate_images:
            result = "❌ KHÔNG PHÁT HIỆN BIỂN SỐ\n\n"
            result += "💡 Gợi ý cải thiện:\n\n"
            result += "✓ Đảm bảo ảnh rõ nét\n"
            result += "✓ Biển số không bị che khuất\n"
            result += "✓ Ánh sáng đủ, không quá tối/sáng\n"
            result += "✓ Góc chụp thẳng, không nghiêng\n"
            result += "✓ Biển số chiếm phần lớn ảnh\n"
            self.update_result(result)
            self.status_label.config(text="❌ Không phát hiện")
            return
        
        license_text, confidence, ocr_results = self.ocr_detector.detect_plate(plate_images)
        
        if license_text and license_text != "Không phát hiện được biển số":
            self.detected_text = license_text
            result = f"✅ PHÁT HIỆN THÀNH CÔNG!\n\n"
            result += f"{'='*35}\n"
            result += f"📋 BIỂN SỐ: {license_text}\n"
            result += f"{'='*35}\n\n"
            result += f"🎯 Độ tin cậy: {confidence:.1%}\n"
            result += f"🔧 Phương pháp: OpenCV\n"
            result += f"📊 Đã xử lý: {len(plate_images)} variants\n\n"
            result += f"💡 Tính năng đã sử dụng:\n"
            result += f"  • Smart digit correction (5/6)\n"
            result += f"  • Auto format dấu\n"
            result += f"  • Enhanced sharpening\n"
            result += f"  • Multi-variant processing\n"
            self.update_result(result)
            self.status_label.config(text=f"✅ Hoàn tất: {license_text}")
        else:
            result = "❌ KHÔNG ĐỌC ĐƯỢC BIỂN SỐ\n\n"
            result += "Đã phát hiện vùng biển số nhưng\n"
            result += "không thể đọc được ký tự.\n\n"
            result += "💡 Thử:\n"
            result += "  • Chụp lại với ánh sáng tốt hơn\n"
            result += "  • Zoom vào biển số\n"
            result += "  • Làm sạch biển số\n"
            self.update_result(result)
            self.status_label.config(text="⚠️ Không đọc được")
    
    def save_result(self):
        """Lưu kết quả vào file"""
        if not self.detected_text:
            messagebox.showwarning("⚠️ Cảnh báo", "Chưa có kết quả để lưu!")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"bien_so_{self.detected_text.replace('-', '').replace('.', '')}.txt"
        )
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(f"KẾT QUẢ NHẬN DIỆN BIỂN SỐ XE\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"Biển số xe: {self.detected_text}\n")
                f.write(f"Ảnh gốc: {self.image_path}\n")
                f.write(f"Phương pháp: {'YOLO AI' if self.use_yolo else 'OpenCV'}\n")
                f.write(f"\n{'='*50}\n")
                f.write(f"Tạo bởi: License Plate Recognition App\n")
            
            messagebox.showinfo("✅ Thành công", f"Đã lưu kết quả!\n\n📁 {Path(save_path).name}")
            self.status_label.config(text=f"💾 Đã lưu: {Path(save_path).name}")

def main():
    root = tk.Tk()
    
    # Set window icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = LicensePlateApp(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
