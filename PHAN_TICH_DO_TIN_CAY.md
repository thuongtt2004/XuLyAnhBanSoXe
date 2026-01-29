# 📊 PHÂN TÍCH VÀ CẢI THIỆN ĐỘ TIN CẬY

**Ngày:** 29/01/2026  
**Vấn đề:** Độ tin cậy 57.9% - Quá thấp  
**Mục tiêu:** Tăng lên 80-90%

---

## 1️⃣ PHÂN TÍCH VẤN ĐỀ

### 1.1. Kết quả hiện tại
```
Biển số: 61F-0797
Độ tin cậy: 57.9%
Phương pháp: YOLO + OCR
```

### 1.2. Nguyên nhân độ tin cậy thấp

#### A. Về YOLO Detection
- ✗ Threshold quá cao (0.15) → bỏ sót detections
- ✗ Padding nhỏ (0.1) → cắt mất phần biển số
- ✗ Chỉ lấy 1 detection tốt nhất → không có backup

#### B. Về Preprocessing
- ✗ Chỉ 5 variants → ít góc nhìn
- ✗ CLAHE yếu (3.0) → contrast không đủ
- ✗ Sharpen yếu (kernel 9) → không đủ sắc nét
- ✗ Thiếu các phương pháp xử lý ánh sáng

#### C. Về OCR
- ✗ Threshold cao (0.3) → bỏ sót text
- ✗ Canvas nhỏ (2560) → thiếu chi tiết
- ✗ Mag ratio thấp (1.8) → không phóng to đủ
- ✗ Chỉ lấy kết quả đầu tiên → bỏ sót kết quả tốt

#### D. Về Confidence Calculation
- ✗ Công thức đơn giản: 40% YOLO + 60% OCR
- ✗ Không có vote mechanism
- ✗ Không tính average confidence
- ✗ Không có bonus cho consistency

---

## 2️⃣ THIẾT KẾ GIẢI PHÁP

### 2.1. Kiến trúc tổng thể

```
Input Image
    ↓
┌─────────────────────────────────────┐
│  STAGE 1: YOLO DETECTION            │
│  - Lower threshold (0.15 → 0.08)    │
│  - Larger padding (0.1 → 0.2)       │
│  - Multiple detections              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STAGE 2: PREPROCESSING             │
│  - 15 variants (5 → 15)             │
│  - Enhanced quality                 │
│  - Multiple techniques              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STAGE 3: OCR                       │
│  - Lower thresholds                 │
│  - Larger canvas (3200)             │
│  - Higher mag ratio (2.2)           │
│  - All results (not just first)     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STAGE 4: VOTING & CONFIDENCE       │
│  - Smart voting                     │
│  - Multi-factor confidence          │
│  - Consistency bonus                │
└─────────────────────────────────────┘
    ↓
Final Result + High Confidence
```

### 2.2. Chi tiết từng stage

#### STAGE 1: YOLO Detection
```python
Improvements:
1. conf_threshold: 0.15 → 0.08 (giảm 47%)
2. padding: 0.1 → 0.2 (tăng 100%)
3. Lấy top 3 detections (backup)
4. Validate bounding box size
```

#### STAGE 2: Preprocessing (15 variants)
```python
Group A: Basic (3 variants)
  1. Original
  2. Grayscale + CLAHE (4.5)
  3. Denoised + Sharpened (kernel 15)

Group B: Threshold (3 variants)
  4. Otsu binary
  5. Adaptive Gaussian
  6. Adaptive Mean

Group C: Resize (3 variants)
  7. 300px width
  8. 400px width
  9. 500px width

Group D: Lighting (3 variants)
  10. Gamma bright (1.5)
  11. Gamma dark (0.7)
  12. Histogram equalization

Group E: Advanced (3 variants)
  13. Edge enhancement
  14. Contrast stretching
  15. Bilateral + Morphology
```

#### STAGE 3: OCR Settings
```python
Optimized parameters:
- text_threshold: 0.3 → 0.2 (giảm 33%)
- low_text: 0.15 → 0.08 (giảm 47%)
- link_threshold: 0.15 → 0.08 (giảm 47%)
- canvas_size: 2560 → 3200 (tăng 25%)
- mag_ratio: 1.8 → 2.2 (tăng 22%)
- add_margin: 0.2 (mới)
```

#### STAGE 4: Confidence Formula
```python
New formula (5 factors):

confidence = (
    yolo_conf × 0.25 +           # 25% YOLO
    best_ocr_conf × 0.35 +       # 35% Best OCR
    avg_ocr_conf × 0.20 +        # 20% Average OCR
    vote_bonus × 0.15 +          # 15% Vote bonus
    consistency_bonus × 0.05     # 5% Consistency
)

Where:
- vote_bonus = (vote_count / total_variants) × 0.15
- consistency_bonus = (1 - std_dev(confidences)) × 0.05
```

---

## 3️⃣ IMPLEMENTATION PLAN

### Phase 1: YOLO Improvements
```python
File: yolo_detector.py
Functions to modify:
  - detect_plates() → lower threshold
  - extract_plate_region() → larger padding
  - integrate_yolo_detection() → main logic
```

### Phase 2: Preprocessing Expansion
```python
File: yolo_detector.py
Add 10 new variants:
  - Group B: 3 threshold variants
  - Group C: 2 more resize variants
  - Group D: 3 lighting variants
  - Group E: 2 advanced variants
```

### Phase 3: OCR Optimization
```python
File: license_plate_detector.py
Function: read_text()
  - Update all threshold parameters
  - Increase canvas_size
  - Increase mag_ratio
  - Add margin parameter
```

### Phase 4: Confidence Calculation
```python
File: yolo_detector.py
Function: integrate_yolo_detection()
  - Collect all OCR results
  - Calculate statistics
  - Apply new formula
  - Add consistency check
```

---

## 4️⃣ EXPECTED RESULTS

### Before vs After

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **YOLO** |
| Threshold | 0.15 | 0.08 | -47% |
| Padding | 0.1 | 0.2 | +100% |
| **Preprocessing** |
| Variants | 5 | 15 | +200% |
| CLAHE | 3.0 | 4.5 | +50% |
| Sharpen | 9 | 15 | +67% |
| **OCR** |
| Text threshold | 0.3 | 0.2 | -33% |
| Canvas | 2560 | 3200 | +25% |
| Mag ratio | 1.8 | 2.2 | +22% |
| **Confidence** |
| Formula factors | 2 | 5 | +150% |
| Vote bonus | No | Yes | New |
| Consistency | No | Yes | New |

### Confidence Improvement

```
Current:  57.9% ❌
Expected: 80-90% ✅
Gain:     +22-32%
```

---

## 5️⃣ RISK ANALYSIS

### Potential Issues

1. **Performance**
   - Risk: 15 variants → slower processing
   - Mitigation: Parallel processing (future)
   - Impact: +2-3 seconds processing time

2. **Memory**
   - Risk: More variants → more memory
   - Mitigation: Process sequentially
   - Impact: Acceptable for desktop app

3. **False Positives**
   - Risk: Lower thresholds → more noise
   - Mitigation: Strict validation + voting
   - Impact: Minimal with voting

### Success Criteria

✅ Confidence > 80% for good images  
✅ Confidence > 70% for medium images  
✅ Processing time < 10 seconds  
✅ No false positives increase  

---

## 6️⃣ TESTING PLAN

### Test Cases

1. **Good Quality Images**
   - Clear, well-lit
   - Expected: 85-95% confidence

2. **Medium Quality Images**
   - Slightly blurry or dark
   - Expected: 75-85% confidence

3. **Poor Quality Images**
   - Very blurry or bad lighting
   - Expected: 60-75% confidence

### Test Metrics

- Accuracy: % correct detections
- Confidence: Average confidence score
- Speed: Processing time
- Consistency: Std dev of results

---

## 7️⃣ ROLLBACK PLAN

If results are worse:

1. Revert to previous version
2. Keep only best improvements
3. A/B test individual changes
4. Adjust parameters incrementally

Backup files:
- `yolo_detector.py.backup`
- `license_plate_detector.py.backup`

---

## 📝 SUMMARY

**Approach:** Systematic, multi-stage improvement  
**Focus:** Quality over speed  
**Goal:** 80-90% confidence  
**Method:** Evidence-based optimization  

**Next Steps:**
1. Implement Phase 1 (YOLO)
2. Test and validate
3. Implement Phase 2 (Preprocessing)
4. Test and validate
5. Implement Phase 3 (OCR)
6. Test and validate
7. Implement Phase 4 (Confidence)
8. Final testing

---

**Ready to implement? Let's go! 🚀**
