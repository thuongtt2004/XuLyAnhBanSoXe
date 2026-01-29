# 🎯 CÔNG THỨC CONFIDENCE MỚI - OPTIMIZED

**Ngày:** 29/01/2026  
**Mục tiêu:** Độ tin cậy chính xác, phản ánh đúng chất lượng

---

## 📐 CÔNG THỨC MỚI

### Base Confidence (85%)
```python
base_conf = (
    yolo_conf × 0.20 +           # 20% YOLO
    best_ocr_conf × 0.40 +       # 40% Best OCR
    median_ocr_conf × 0.15 +     # 15% Median OCR (MỚI)
    avg_ocr_conf × 0.10          # 10% Average OCR
)
```

### Bonuses & Penalties (15%)
```python
+ vote_bonus          # 0-15% (dựa vào vote ratio)
+ consistency_bonus   # 0-5% (dựa vào std dev)
+ quality_penalty     # 0 đến -10% (nếu OCR kém)
```

### Final
```python
final_conf = base_conf + bonuses + penalties
final_conf = clamp(final_conf, 0.0, 1.0)
```

---

## 🔢 CHI TIẾT TỪNG THÀNH PHẦN

### 1. YOLO Confidence (20%)
```python
yolo_conf × 0.20

Ví dụ:
- YOLO: 0.85 → 0.85 × 0.20 = 0.17
```

**Giảm từ 25% → 20%** vì YOLO chỉ detect vùng, không đọc text.

### 2. Best OCR Confidence (40%)
```python
best_ocr_conf × 0.40

Ví dụ:
- Best OCR: 0.92 → 0.92 × 0.40 = 0.368
```

**Tăng từ 35% → 40%** vì đây là confidence cao nhất, quan trọng nhất.

### 3. Median OCR Confidence (15%) - MỚI
```python
median_ocr_conf × 0.15

Ví dụ:
- Confidences: [0.85, 0.88, 0.90, 0.92, 0.95]
- Median: 0.90 → 0.90 × 0.15 = 0.135
```

**Thêm mới** để giảm ảnh hưởng của outliers.

### 4. Average OCR Confidence (10%)
```python
avg_ocr_conf × 0.10

Ví dụ:
- Average: 0.88 → 0.88 × 0.10 = 0.088
```

**Giảm từ 20% → 10%** vì average dễ bị kéo xuống bởi outliers.

### 5. Vote Bonus (0-15%)
```python
if vote_ratio >= 0.6:      # 60%+ agree
    vote_bonus = 0.15
elif vote_ratio >= 0.4:    # 40-60%
    vote_bonus = 0.10
elif vote_ratio >= 0.2:    # 20-40%
    vote_bonus = 0.05
else:                      # <20%
    vote_bonus = 0.0

Ví dụ:
- 10/15 variants vote cho "61F-0797"
- vote_ratio = 10/15 = 0.67 (67%)
- vote_bonus = 0.15
```

**Thay đổi:** Từ linear → stepped để rõ ràng hơn.

### 6. Consistency Bonus (0-5%)
```python
if std_dev < 0.05:         # Very consistent
    consistency_bonus = 0.05
elif std_dev < 0.10:       # Good
    consistency_bonus = 0.03
elif std_dev < 0.15:       # Fair
    consistency_bonus = 0.01
else:                      # Poor
    consistency_bonus = 0.0

Ví dụ:
- Confidences: [0.88, 0.90, 0.92, 0.89, 0.91]
- std_dev = 0.015
- consistency_bonus = 0.05
```

**Thay đổi:** Từ linear → stepped.

### 7. Quality Penalty (0 đến -10%) - MỚI
```python
if avg_ocr_conf < 0.5:     # Poor quality
    quality_penalty = -0.10
elif avg_ocr_conf < 0.6:   # Fair quality
    quality_penalty = -0.05
else:                      # Good quality
    quality_penalty = 0.0

Ví dụ:
- avg_ocr_conf = 0.45
- quality_penalty = -0.10
```

**Thêm mới** để phạt khi OCR confidence thấp.

---

## 📊 VÍ DỤ TÍNH TOÁN

### Case 1: Excellent Detection
```
Input:
- YOLO: 0.90
- OCR results: 12/15 variants vote "61F-0797"
  Confidences: [0.88, 0.90, 0.92, 0.89, 0.91, 0.93, 0.87, 0.90, 0.92, 0.88, 0.91, 0.89]
- Best: 0.93
- Median: 0.90
- Average: 0.90
- Std dev: 0.018

Calculation:
Base = 0.90×0.20 + 0.93×0.40 + 0.90×0.15 + 0.90×0.10
     = 0.18 + 0.372 + 0.135 + 0.09
     = 0.777

Vote bonus = 0.15 (12/15 = 80%)
Consistency = 0.05 (std < 0.05)
Quality = 0.0 (avg > 0.6)

Final = 0.777 + 0.15 + 0.05 + 0.0
      = 0.977 → 0.98 (98%) ✅
```

### Case 2: Good Detection
```
Input:
- YOLO: 0.75
- OCR results: 8/15 variants vote "61F-0797"
  Confidences: [0.75, 0.78, 0.80, 0.76, 0.79, 0.77, 0.81, 0.74]
- Best: 0.81
- Median: 0.77
- Average: 0.775
- Std dev: 0.024

Calculation:
Base = 0.75×0.20 + 0.81×0.40 + 0.77×0.15 + 0.775×0.10
     = 0.15 + 0.324 + 0.1155 + 0.0775
     = 0.667

Vote bonus = 0.10 (8/15 = 53%)
Consistency = 0.05 (std < 0.05)
Quality = 0.0 (avg > 0.6)

Final = 0.667 + 0.10 + 0.05 + 0.0
      = 0.817 → 0.82 (82%) ✅
```

### Case 3: Fair Detection
```
Input:
- YOLO: 0.65
- OCR results: 5/15 variants vote "61F-0797"
  Confidences: [0.60, 0.65, 0.62, 0.68, 0.63]
- Best: 0.68
- Median: 0.63
- Average: 0.636
- Std dev: 0.029

Calculation:
Base = 0.65×0.20 + 0.68×0.40 + 0.63×0.15 + 0.636×0.10
     = 0.13 + 0.272 + 0.0945 + 0.0636
     = 0.56

Vote bonus = 0.05 (5/15 = 33%)
Consistency = 0.05 (std < 0.05)
Quality = -0.05 (avg < 0.6)

Final = 0.56 + 0.05 + 0.05 - 0.05
      = 0.61 → 0.61 (61%) ⚠️
```

### Case 4: Poor Detection
```
Input:
- YOLO: 0.55
- OCR results: 3/15 variants vote "61F-0797"
  Confidences: [0.45, 0.48, 0.42]
- Best: 0.48
- Median: 0.45
- Average: 0.45
- Std dev: 0.025

Calculation:
Base = 0.55×0.20 + 0.48×0.40 + 0.45×0.15 + 0.45×0.10
     = 0.11 + 0.192 + 0.0675 + 0.045
     = 0.4145

Vote bonus = 0.0 (3/15 = 20%)
Consistency = 0.05 (std < 0.05)
Quality = -0.10 (avg < 0.5)

Final = 0.4145 + 0.0 + 0.05 - 0.10
      = 0.3645 → 0.36 (36%) ❌
```

---

## 📈 CONFIDENCE RANGES

| Range | Quality | Meaning |
|-------|---------|---------|
| **90-100%** | Excellent | Rất chắc chắn, nhiều variants đồng ý |
| **80-90%** | Very Good | Chắc chắn, kết quả tốt |
| **70-80%** | Good | Tin cậy được, có thể dùng |
| **60-70%** | Fair | Chấp nhận được, cần xem xét |
| **50-60%** | Poor | Không chắc chắn, nên kiểm tra |
| **<50%** | Very Poor | Không tin cậy, có thể sai |

---

## 🔄 SO SÁNH VỚI CÔNG THỨC CŨ

| Component | Old | New | Change |
|-----------|-----|-----|--------|
| YOLO weight | 25% | 20% | -5% |
| Best OCR | 35% | 40% | +5% |
| Median OCR | - | 15% | NEW |
| Avg OCR | 20% | 10% | -10% |
| Vote bonus | Linear | Stepped | Better |
| Consistency | Linear | Stepped | Better |
| Quality penalty | - | 0-10% | NEW |

---

## ✅ IMPROVEMENTS

1. **Tăng trọng số Best OCR** (35% → 40%)
   - Quan trọng nhất, phản ánh kết quả tốt nhất

2. **Thêm Median OCR** (15%)
   - Giảm ảnh hưởng outliers
   - Stable hơn average

3. **Giảm Average OCR** (20% → 10%)
   - Dễ bị kéo xuống bởi outliers
   - Ít quan trọng hơn

4. **Stepped bonuses**
   - Rõ ràng hơn linear
   - Dễ hiểu, dễ tune

5. **Quality penalty**
   - Phạt khi OCR kém
   - Phản ánh đúng chất lượng

---

## 🎯 KẾT QUẢ MONG ĐỢI

**Ảnh tốt:**
```
Confidence: 85-98% ✅
```

**Ảnh trung bình:**
```
Confidence: 70-85% ✅
```

**Ảnh kém:**
```
Confidence: 50-70% ⚠️
```

**Ảnh rất kém:**
```
Confidence: <50% ❌
```

---

**Test ngay để thấy sự khác biệt! 🎯✨**
