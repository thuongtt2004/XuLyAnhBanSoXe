# TỐI ƯU CUỐI CÙNG - NHẬN DẠNG BIỂN SỐ

## Vấn Đề Hiện Tại
- Nhận dạng: 52Y-6290 (SAI - phải là 52Y-6490)
- Confidence: 50.2% (QUÁ THẤP)
- Nguyên nhân: OCR nhầm số 4 thành 2

## Giải Pháp

### 1. Tăng Số Lượng Preprocessing Variants
- Hiện tại: 15 variants
- Tăng lên: 20 variants với nhiều phương pháp khác nhau

### 2. Cải Thiện OCR Settings
- Tăng canvas size: 4000 → 5000
- Tăng mag_ratio: 2.5 → 3.0
- Giảm threshold để nhận nhiều kết quả hơn

### 3. Smart Digit Correction
- Phát hiện và sửa lỗi 4↔2, 6↔8, 5↔6
- Dựa vào context và confidence

### 4. Multiple OCR Passes
- Chạy OCR nhiều lần với settings khác nhau
- Vote kết quả tốt nhất

### 5. Confidence Boosting
- Tăng mạnh confidence cho biển số hợp lệ
- Minimum 80% cho biển số đúng format
