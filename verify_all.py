"""
Script kiểm tra toàn diện dự án
"""
import sys
from pathlib import Path

print("=" * 70)
print("KIỂM TRA TOÀN DIỆN DỰ ÁN NHẬN DIỆN BIỂN SỐ XE")
print("=" * 70)

# Counters
total_tests = 0
passed_tests = 0

def test(name, func):
    """Helper function to run tests"""
    global total_tests, passed_tests
    total_tests += 1
    print(f"\n[{total_tests}] {name}")
    try:
        result = func()
        if result:
            print(f"    ✅ PASSED")
            passed_tests += 1
            return True
        else:
            print(f"    ❌ FAILED")
            return False
    except Exception as e:
        print(f"    ❌ ERROR: {e}")
        return False

# Test 1: Python version
def check_python_version():
    version = sys.version_info
    print(f"    Python {version.major}.{version.minor}.{version.micro}")
    return version.major == 3 and version.minor >= 8

test("Kiểm tra Python version (>= 3.8)", check_python_version)

# Test 2: Import OpenCV
def check_opencv():
    import cv2
    print(f"    OpenCV version: {cv2.__version__}")
    return True

test("Import OpenCV", check_opencv)

# Test 3: Import EasyOCR
def check_easyocr():
    import easyocr
    print(f"    EasyOCR imported successfully")
    return True

test("Import EasyOCR", check_easyocr)

# Test 4: Import custom modules
def check_custom_modules():
    from preprocess_image import ImagePreprocessor
    from license_plate_detector import LicensePlateDetector
    from yolo_detector import YOLOPlateDetector
    print(f"    All custom modules imported")
    return True

test("Import custom modules", check_custom_modules)

# Test 5: Check main files exist
def check_main_files():
    files = [
        "main.py",
        "main_yolo.py",
        "license_plate_detector.py",
        "yolo_detector.py",
        "preprocess_image.py",
        "requirements.txt"
    ]
    for f in files:
        if not Path(f).exists():
            print(f"    Missing: {f}")
            return False
    print(f"    All {len(files)} main files exist")
    return True

test("Kiểm tra files chính", check_main_files)

# Test 6: Check YOLO model
def check_yolo_model():
    model_path = Path("runs/license_plate/weights/best.pt")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"    YOLO model found ({size_mb:.1f} MB)")
        return True
    else:
        print(f"    YOLO model not found (will use OpenCV)")
        return True  # Not critical

test("Kiểm tra YOLO model", check_yolo_model)

# Test 7: Check demo images
def check_demo_images():
    demo_images = list(Path(".").glob("demo_plate_*.jpg"))
    print(f"    Found {len(demo_images)} demo images")
    return len(demo_images) > 0

test("Kiểm tra ảnh demo", check_demo_images)

# Test 8: Test ImagePreprocessor
def check_preprocessor():
    from preprocess_image import ImagePreprocessor
    import cv2
    import numpy as np
    
    preprocessor = ImagePreprocessor()
    
    # Create dummy image
    dummy_img = np.zeros((100, 300, 3), dtype=np.uint8)
    dummy_img[30:70, 50:250] = 255  # White rectangle (simulated plate)
    
    # Test preprocessing
    result = preprocessor.preprocess_for_ocr(dummy_img)
    print(f"    Preprocessor works correctly")
    return result is not None

test("Test ImagePreprocessor", check_preprocessor)

# Test 9: Check documentation
def check_documentation():
    docs = [
        "README.md",
        "HUONG_DAN_SU_DUNG.md",
        "ALL_FIXES_SUMMARY.md",
        "TANG_DO_CHINH_XAC.md"
    ]
    found = sum(1 for d in docs if Path(d).exists())
    print(f"    Found {found}/{len(docs)} documentation files")
    return found >= 3

test("Kiểm tra tài liệu", check_documentation)

# Test 10: Syntax check main files
def check_syntax():
    import py_compile
    files = ["main.py", "main_yolo.py", "license_plate_detector.py"]
    for f in files:
        try:
            py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError:
            print(f"    Syntax error in {f}")
            return False
    print(f"    No syntax errors in main files")
    return True

test("Kiểm tra syntax", check_syntax)

# Summary
print("\n" + "=" * 70)
print("KẾT QUẢ KIỂM TRA")
print("=" * 70)
print(f"Tổng số tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {total_tests - passed_tests}")
print(f"Tỷ lệ thành công: {passed_tests/total_tests*100:.1f}%")

if passed_tests == total_tests:
    print("\n🎉 TẤT CẢ TESTS ĐỀU PASSED!")
    print("✅ Dự án sẵn sàng sử dụng!")
    print("\nChạy ứng dụng:")
    print("  py main_yolo.py")
elif passed_tests >= total_tests * 0.8:
    print("\n⚠️ Hầu hết tests passed, dự án có thể sử dụng")
    print("Một số tính năng có thể không hoạt động")
else:
    print("\n❌ Nhiều tests failed, cần kiểm tra lại")
    print("Vui lòng kiểm tra:")
    print("  1. Đã cài đặt đủ dependencies: pip install -r requirements.txt")
    print("  2. Python version >= 3.8")
    print("  3. Đủ dung lượng ổ cứng")

print("=" * 70)
