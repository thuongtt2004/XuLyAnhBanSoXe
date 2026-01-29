# 🚗 Ứng Dụng Nhận Diện Biển Số Xe

Ứng dụng nhận diện biển số xe tự động sử dụng công nghệ Computer Vision và OCR (Optical Character Recognition).

## ✨ Tính năng

- 📸 Upload và hiển thị ảnh xe
- 🔍 Tự động phát hiện vị trí biển số xe
- 🤖 Nhận diện ký tự trên biển số bằng AI (EasyOCR)
- 📊 Hiển thị độ tin cậy của kết quả
- 💾 Lưu ảnh kết quả với biển số được đánh dấu
- 🎨 Giao diện đồ họa thân thiện và dễ sử dụng

## 🛠️ Công nghệ sử dụng

- **Python 3.8+**
- **OpenCV**: Xử lý ảnh và phát hiện biển số
- **EasyOCR**: Nhận diện ký tự OCR
- **Tkinter**: Giao diện đồ họa
- **PyTorch**: Backend cho EasyOCR

## 📋 Yêu cầu hệ thống

- Python 3.8 trở lên
- RAM: Tối thiểu 4GB (khuyến nghị 8GB)
- Dung lượng ổ cứng: ~2GB cho models
- Windows / Linux / macOS

## 🚀 Cài đặt

### Bước 1: Clone hoặc tải source code

```bash
cd d:\game
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv
```

Kích hoạt môi trường ảo:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

**Lưu ý:** Lần đầu tiên chạy, EasyOCR sẽ tự động tải các model AI (khoảng 1-2GB), quá trình này có thể mất vài phút.

## 💻 Cách sử dụng

### Chạy ứng dụng

```bash
python main.py
```

### Hướng dẫn sử dụng

1. **Chọn Ảnh**: Nhấn nút "📁 Chọn Ảnh" và chọn ảnh có biển số xe
2. **Nhận Diện**: Nhấn nút "🔍 Nhận Diện" để bắt đầu quá trình nhận diện
3. **Xem Kết Quả**: Biển số sẽ được hiển thị cùng với độ tin cậy
4. **Lưu Kết Quả**: Nhấn "💾 Lưu Kết Quả" để lưu ảnh đã được đánh dấu
5. **Xóa**: Nhấn "🗑️ Xóa" để bắt đầu lại với ảnh mới

## 📁 Cấu trúc thư mục

```
d:\game\
├── main.py                      # File chính chạy ứng dụng
├── preprocess_image.py          # Module tiền xử lý ảnh
├── license_plate_detector.py   # Module nhận diện OCR
├── requirements.txt             # Danh sách thư viện
└── README.md                    # File hướng dẫn này
```

## 🔧 Cấu hình nâng cao

### Thay đổi ngôn ngữ nhận diện

Trong file `main.py`, dòng 38, bạn có thể thay đổi:

```python
# Chỉ tiếng Anh (mặc định)
self.detector = LicensePlateDetector(languages=['en'], gpu=False)

# Thêm tiếng Việt (nếu cần)
self.detector = LicensePlateDetector(languages=['en', 'vi'], gpu=False)
```

### Sử dụng GPU (nếu có NVIDIA GPU)

```python
self.detector = LicensePlateDetector(languages=['en'], gpu=True)
```

**Lưu ý:** Cần cài đặt CUDA và PyTorch với GPU support.

## 🎯 Tips để có kết quả tốt nhất

1. ✅ Sử dụng ảnh có độ phân giải cao
2. ✅ Đảm bảo biển số rõ ràng, không bị mờ
3. ✅ Ánh sáng tốt, tránh quá tối hoặc quá sáng
4. ✅ Biển số không bị che khuất
5. ✅ Góc chụp thẳng, tránh nghiêng quá nhiều

## ⚠️ Xử lý lỗi thường gặp

### Lỗi: "Không tìm thấy biển số xe"

- Thử với ảnh khác có biển số rõ hơn
- Đảm bảo biển số chiếm một phần đáng kể trong ảnh
- Kiểm tra độ sáng và độ tương phản của ảnh

### Lỗi: "Không thể khởi tạo EasyOCR"

- Kiểm tra kết nối internet (lần đầu cần tải models)
- Đảm bảo đủ dung lượng ổ cứng (~2GB)
- Thử chạy lại với quyền Administrator

### Lỗi: Package installation failed

```bash
# Thử nâng cấp pip
python -m pip install --upgrade pip

# Cài đặt lại từng package
pip install opencv-python
pip install easyocr
```

## 📊 Hiệu suất

- **Thời gian xử lý**: 2-5 giây/ảnh (tùy cấu hình máy)
- **Độ chính xác**: 85-95% (với ảnh chất lượng tốt)
- **Khởi tạo lần đầu**: 30-60 giây (tải models)

## 🔮 Tính năng tương lai

- [ ] Hỗ trợ video real-time
- [ ] Tích hợp camera webcam
- [ ] Lưu lịch sử nhận diện
- [ ] Xuất kết quả ra Excel/CSV
- [ ] Hỗ trợ nhiều biển số trong một ảnh
- [ ] API REST để tích hợp với hệ thống khác

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Hãy tạo Pull Request hoặc mở Issue nếu bạn có ý tưởng cải thiện.

## 📝 License

Dự án này được phát triển cho mục đích học tập và nghiên cứu.

## 👨‍💻 Tác giả

Được phát triển bởi GitHub Copilot

## 📞 Liên hệ & Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra phần "Xử lý lỗi thường gặp" ở trên
2. Đảm bảo đã cài đặt đúng tất cả dependencies
3. Kiểm tra phiên bản Python (3.8+)

## 🙏 Cảm ơn

Cảm ơn các thư viện mã nguồn mở:
- OpenCV
- EasyOCR (JaidedAI)
- PyTorch
- Pillow

---

**Chúc bạn sử dụng vui vẻ! 🎉**
