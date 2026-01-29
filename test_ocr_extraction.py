"""
Test OCR extraction logic to ensure garbage text is rejected
"""
from license_plate_detector import LicensePlateDetector

# Create detector
detector = LicensePlateDetector()

# Simulate OCR results with garbage text
garbage_ocr_results = [
    # Garbage text with high confidence (should be rejected)
    ([[[0, 0], [100, 0], [100, 30], [0, 30]]], "KHNGPHTHINCBINS", 0.915),
    ([[[0, 0], [100, 0], [100, 30], [0, 30]]], "ABCDEFGHIJK", 0.85),
    ([[[0, 0], [100, 0], [100, 30], [0, 30]]], "NOPLATEHERE", 0.80),
]

# Valid OCR results
valid_ocr_results = [
    ([[[0, 0], [100, 0], [100, 30], [0, 30]]], "29A12345", 0.85),
    ([[[0, 0], [100, 0], [100, 30], [0, 30]]], "61F0797", 0.90),
    ([[[0, 0], [100, 0], [100, 30], [0, 30]]], "30L1234", 0.88),
]

print("=" * 70)
print("OCR EXTRACTION TEST - Checking if garbage text is rejected")
print("=" * 70)
print()

# Test garbage text
print("Testing GARBAGE text (should be rejected):")
print("-" * 70)
for ocr_result in garbage_ocr_results:
    bbox, text, conf = ocr_result
    result = detector.extract_license_number([ocr_result])
    
    is_rejected = (result == "Không phát hiện được biển số")
    status = "✓ PASS" if is_rejected else "✗ FAIL"
    
    print(f"{status} | Input: '{text}' (conf: {conf:.1%})")
    print(f"      Result: '{result}'")
    print(f"      Expected: Rejected, Got: {'Rejected' if is_rejected else 'Accepted'}")
    print()

# Test valid text
print("Testing VALID text (should be accepted):")
print("-" * 70)
for ocr_result in valid_ocr_results:
    bbox, text, conf = ocr_result
    result = detector.extract_license_number([ocr_result])
    
    is_accepted = (result != "Không phát hiện được biển số")
    status = "✓ PASS" if is_accepted else "✗ FAIL"
    
    print(f"{status} | Input: '{text}' (conf: {conf:.1%})")
    print(f"      Result: '{result}'")
    print(f"      Expected: Accepted, Got: {'Accepted' if is_accepted else 'Rejected'}")
    print()

print("=" * 70)
print("Test completed!")
print("=" * 70)
