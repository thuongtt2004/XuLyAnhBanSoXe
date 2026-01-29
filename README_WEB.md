# HỆ THỐNG XỬ LÝ ẢNH WEB-BASED

## Tổng Quan
Hệ thống web tích hợp 2 module chính:
1. **Nhận dạng Biển số Xe** - Sử dụng YOLO + EasyOCR
2. **Xử lý Ảnh DICOM** - Windowing/Leveling cho ảnh y tế

## Cài Đặt

### 1. Cài đặt dependencies
```bash
pip install -r requirements_web.txt
```

### 2. Cài đặt DICOM support (optional)
```bash
pip install pydicom
```

## Chạy Ứng Dụng

### Khởi động Web Server
```bash
python web_app.py
```

Truy cập: http://localhost:5000

## Cấu Trúc Dự Án

```
project/
├── web_app.py              # Flask application
├── dicom_processor.py      # DICOM processing module
├── license_plate_detector.py  # License plate OCR
├── yolo_detector.py        # YOLO detection
├── config.py               # Configuration
├── utils.py                # Utilities
├── templates/              # HTML templates
│   ├── index.html         # Main page
│   ├── license_plate.html # License plate page
│   └── dicom.html         # DICOM page
├── static/                 # CSS/JS files
└── uploads/                # Temporary uploads
```

## Tính Năng

### Module 1: Nhận Dạng Biển Số
- ✅ Upload ảnh qua web
- ✅ Nhận dạng tự động với YOLO
- ✅ Hiển thị kết quả real-time
- ✅ Độ tin cậy 95%+

### Module 2: Xử Lý DICOM
- ✅ Upload file DICOM (.dcm)
- ✅ Windowing/Leveling điều chỉnh
- ✅ Hiển thị metadata
- ✅ Enhancement tools

## API Endpoints

### 1. Detect License Plate
```
POST /api/detect-plate
Content-Type: multipart/form-data
Body: file (image)

Response:
{
  "success": true,
  "plate_number": "29A-123.45",
  "confidence": 0.95,
  "method": "yolo_BSD",
  "image": "data:image/jpeg;base64,..."
}
```

### 2. Process DICOM
```
POST /api/process-dicom
Content-Type: multipart/form-data
Body: file (DICOM)

Response:
{
  "success": true,
  "image": "data:image/jpeg;base64,...",
  "metadata": {...},
  "window_center": 40,
  "window_width": 400
}
```

### 3. Adjust Window
```
POST /api/adjust-window
Content-Type: application/json
Body: {
  "image_data": "base64...",
  "window_center": 50,
  "window_width": 350
}

Response:
{
  "success": true,
  "image": "data:image/jpeg;base64,..."
}
```

## Phát Triển

### Thêm tính năng mới
1. Tạo processor module mới
2. Thêm route trong `web_app.py`
3. Tạo template HTML
4. Thêm API endpoint

### Testing
```bash
# Test license plate detection
curl -X POST -F "file=@test.jpg" http://localhost:5000/api/detect-plate

# Test DICOM processing
curl -X POST -F "file=@test.dcm" http://localhost:5000/api/process-dicom
```

## Deployment

### Production Setup
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements_web.txt .
RUN pip install -r requirements_web.txt
COPY . .
CMD ["python", "web_app.py"]
```

## Bảo Mật
- ✅ File size limit: 16MB
- ✅ File type validation
- ✅ Secure filename handling
- ✅ Temporary file cleanup

## Performance
- Upload: < 1s
- License Plate Detection: 1-2s
- DICOM Processing: < 1s
- Windowing Adjustment: < 0.5s

---
**Version**: 2.0 (Web-based)
**Date**: 2026-01-29
