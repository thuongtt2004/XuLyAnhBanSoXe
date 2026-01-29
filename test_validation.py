"""
Test validation logic to ensure garbage text is rejected
"""
from utils import validate_vietnamese_plate, format_vietnamese_plate

# Test cases
test_cases = [
    # Valid plates
    ("29A12345", True, "Valid 7-digit plate"),
    ("30L1234", True, "Valid 6-digit plate"),
    ("61F0797", True, "Valid plate from demo"),
    ("29AB12345", True, "Valid 2-letter plate"),
    ("51G12345", True, "Valid plate"),
    
    # Invalid plates (garbage)
    ("KHNGPHTHINCBINS", False, "Garbage text - no valid pattern"),
    ("ABCDEFGH", False, "Only letters"),
    ("12345678", False, "Only numbers"),
    ("A1234", False, "Too short"),
    ("29A", False, "Too short"),
    ("29A123456789", False, "Too long"),
    ("00A1234", False, "Invalid province code (00)"),
    ("100A1234", False, "Invalid province code (100)"),
    ("29ABCD1234", False, "Too many letters"),
    ("29A123", False, "Too few digits"),
]

print("=" * 70)
print("VALIDATION TEST - Checking if garbage text is properly rejected")
print("=" * 70)
print()

passed = 0
failed = 0

for text, expected_valid, description in test_cases:
    # Test raw text
    is_valid = validate_vietnamese_plate(text)
    
    # Also test formatted version
    formatted = format_vietnamese_plate(text)
    is_valid_formatted = validate_vietnamese_plate(formatted)
    
    # Check result
    test_passed = (is_valid == expected_valid) or (is_valid_formatted == expected_valid)
    
    status = "✓ PASS" if test_passed else "✗ FAIL"
    
    if test_passed:
        passed += 1
    else:
        failed += 1
    
    print(f"{status} | {description}")
    print(f"      Input: '{text}'")
    print(f"      Formatted: '{formatted}'")
    print(f"      Expected: {expected_valid}, Got: {is_valid} (raw) / {is_valid_formatted} (formatted)")
    print()

print("=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 70)

if failed == 0:
    print("✓ ALL TESTS PASSED! Validation is working correctly.")
else:
    print(f"✗ {failed} TESTS FAILED! Validation needs fixing.")
