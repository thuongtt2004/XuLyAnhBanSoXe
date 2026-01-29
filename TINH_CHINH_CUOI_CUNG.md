# ⚖️ TINH CHỈNH CÂN BẰNG - FINAL TUNING

**Ngày:** 29/01/2026  
**Mục tiêu:** Cân bằng giữa độ chính xác và không bỏ sót

---

## 🎯 CHIẾN LƯỢC

**Balanced Approach:**
- ✅ Lọc garbage text (false positives)
- ✅ Không bỏ sót biển số thật (false negatives)
- ✅ Validation thông minh
- ✅ Thresholds hợp lý

---

## ⚙️ CÁC THÔNG SỐ ĐÃ TINH CHỈNH

### 1. YOLO Detection
```python
# Threshold: 0.08 → 0.10 (cân bằng)
conf_threshold = 0.10

# Padding: 0.2 (giữ nguyên - tốt)
padding = 0.2
```

### 2. OCR Thresholds
```python
# Trong extract_license_number():
confidence > 0.2  # Balanced (không quá cao/thấp)

# Trong YOLO detector:
ocr_conf > 0.2    # Consistent

# Trong OCR settings:
text_threshold = 0.25  # Moderate
low_text = 0.1         # Moderate
```

### 3. Validation Rules

**Độ dài:**
```python
# Clean text: 7-10 ký tự
# Raw text: 6-15 ký tự (có dấu)
```

**Thành phần:**
```python
# Chữ cái: 1-3 ký tự
# Chữ số: 6-8 ký tự
# Mã tỉnh: 01-99
```

**Patterns:**
```python
r'^\d{2}[A-Z]{1}\d{4,6}$'      # 29A1234
r'^\d{2}[A-Z]{2}\d{4,6}$'      # 29AB1234
r'^\d{2}[A-Z]{1}[A-Z]{1}\d{4,6}$'  # 29AA1234
```

---

## 📊 SO SÁNH THÔNG SỐ

| Parameter | Too Loose | Balanced ✅ | Too Strict |
|-----------|-----------|-------------|------------|
| **YOLO threshold** | 0.05 | **0.10** | 0.20 |
| **OCR threshold** | 0.1 | **0.2** | 0.4 |
| **Min length** | 4 | **6-7** | 8 |
| **Max length** | 20 | **12-15** | 10 |
| **Letter count** | Any | **1-3** | 1-2 |
| **Digit count** | Any | **6-8** | 6 |

---

## 🔍 VALIDATION LOGIC

### Level 1: Quick Filters (Fast)
```python
✓ Length: 6-15 characters
✓ Has letters: Yes
✓ Has digits: Yes
```

### Level 2: Format Check (Medium)
```python
✓ Clean length: 7-10
✓ Letter count: 1-3
✓ Digit count: 6-8
✓ Starts with 2 digits: 01-99
```

### Level 3: Pattern Match (Strict)
```python
✓ Match Vietnamese plate patterns
✓ Correct structure: 2 digits + letters + digits
```

---

## 🎯 EXPECTED BEHAVIOR

### Case 1: Valid Plate
```
Input: "61F0797" (OCR conf: 0.85)
↓
Clean: "61F0797"
Has letter: ✓ (F)
Has digit: ✓ (6,1,0,7,9,7)
Length: ✓ (7)
Pattern: ✓ (61F0797 → 61F-0797)
↓
Output: "61F-0797" ✅
```

### Case 2: Garbage Text
```
Input: "KHNGPHTHINCBINS" (OCR conf: 0.45)
↓
Clean: "KHNGPHTHINCBINS"
Has letter: ✓
Has digit: ✗ (NO DIGITS!)
↓
Rejected: Not a plate ❌
```

### Case 3: Low Confidence
```
Input: "61F0797" (OCR conf: 0.15)
↓
Threshold check: 0.15 < 0.2
↓
Rejected: Too low confidence ❌
```

### Case 4: Partial Detection
```
Input OCR results:
  - "61F" (conf: 0.8)
  - "0797" (conf: 0.75)
↓
Combine: "61F0797"
Validate: ✓
Format: "61F-0797"
↓
Output: "61F-0797" ✅
```

---

## 📈 CONFIDENCE CALCULATION

### Formula (Unchanged - Good)
```python
confidence = (
    yolo_conf × 0.25 +
    best_ocr_conf × 0.35 +
    avg_ocr_conf × 0.20 +
    vote_bonus +
    consistency_bonus
)
```

### Expected Ranges
```
Excellent: 85-95%  (Clear image, good detection)
Good:      75-85%  (Normal image)
Fair:      65-75%  (Poor image, but valid)
Poor:      <65%    (Very poor image or invalid)
```

---

## 🧪 TEST SCENARIOS

### Scenario 1: Clear Image
```
Expected:
✅ Detect: Yes
✅ Confidence: 85-95%
✅ Result: Correct plate number
```

### Scenario 2: Blurry Image
```
Expected:
✅ Detect: Yes (with multiple variants)
✅ Confidence: 70-80%
✅ Result: Correct plate number
```

### Scenario 3: No Plate
```
Expected:
❌ Detect: No
❌ Result: "Không phát hiện được biển số"
```

### Scenario 4: Garbage Text
```
Expected:
❌ Detect: No (filtered by validation)
❌ Result: "Không phát hiện được biển số"
```

---

## ⚠️ EDGE CASES

### 1. Biển số đặc biệt
```
80A-00001  ✅ (Biển ngũ quý)
29AA-1234  ✅ (Biển 2 chữ giống nhau)
```

### 2. Biển số cũ
```
29A-1234   ✅ (4 số)
29A-12345  ✅ (5 số)
29A-123456 ✅ (6 số)
```

### 3. OCR errors
```
61F-O797 → 61F-0797  ✅ (O → 0)
61F-l797 → 61F-1797  ✅ (l → 1)
6lF-0797 → 61F-0797  ✅ (l → 1)
```

---

## 📝 SUMMARY OF CHANGES

### Thresholds
- YOLO: 0.08 → **0.10** (balanced)
- OCR extract: 0.3 → **0.2** (balanced)
- OCR YOLO: 0.3 → **0.2** (consistent)
- OCR settings: 0.2 → **0.25** (moderate)

### Validation
- ✅ Check letter count (1-3)
- ✅ Check digit count (6-8)
- ✅ Check province code (01-99)
- ✅ Multiple patterns support
- ✅ Format before validate

### Logic
- ✅ Try format if validation fails
- ✅ Combine similar confidence results
- ✅ Sort by confidence first, then length
- ✅ Consistent thresholds across modules

---

## 🚀 READY TO TEST

```bash
py main_yolo.py
```

### Expected Improvements:
- ✅ No more garbage text (KHNGPHTHINCBINS)
- ✅ Still detect valid plates
- ✅ Better confidence scores
- ✅ Consistent behavior

---

**Đã tinh chỉnh cân bằng! Test ngay! 🎯✨**
