"""
Web Application for License Plate Recognition and DICOM Image Processing
Flask-based web interface
"""
from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image

# Import existing modules
from license_plate_detector import LicensePlateDetector
from yolo_detector import integrate_yolo_detection

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'dcm'}

# Initialize detector
ocr_detector = LicensePlateDetector()

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def encode_image_to_base64(image):
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/license-plate')
def license_plate_page():
    """License plate recognition page"""
    return render_template('license_plate.html')


@app.route('/dicom')
def dicom_page():
    """DICOM image processing page"""
    return render_template('dicom.html')


@app.route('/api/detect-plate', methods=['POST'])
def detect_plate():
    """API endpoint for license plate detection"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Try YOLO detection first
        plate_text, confidence, method = integrate_yolo_detection(
            filepath, ocr_detector
        )
        
        # If YOLO fails, try OpenCV method with MULTIPLE attempts
        if not plate_text or confidence < 0.2:  # Giảm threshold từ 0.3
            from preprocess_image import ImagePreprocessor
            from utils import validate_vietnamese_plate
            
            image = cv2.imread(filepath)
            
            # Try multiple preprocessing approaches
            attempts = []
            
            # Attempt 1: Standard preprocessing
            preprocessor = ImagePreprocessor()
            plate_images, coords, processed = preprocessor.preprocess_for_ocr(image)
            
            if plate_images:
                plate_text_1, confidence_1, ocr_results = ocr_detector.detect_plate(plate_images)
                if validate_vietnamese_plate(plate_text_1):
                    attempts.append((plate_text_1, confidence_1, "OpenCV"))
            
            # Attempt 2: Enhanced contrast
            enhanced = cv2.convertScaleAbs(image, alpha=1.5, beta=30)
            plate_images_2, coords_2, processed_2 = preprocessor.preprocess_for_ocr(enhanced)
            
            if plate_images_2:
                plate_text_2, confidence_2, ocr_results_2 = ocr_detector.detect_plate(plate_images_2)
                if validate_vietnamese_plate(plate_text_2):
                    attempts.append((plate_text_2, confidence_2, "OpenCV_Enhanced"))
            
            # Attempt 3: Gamma correction
            gamma = 1.2
            gamma_corrected = np.power(image / 255.0, gamma) * 255.0
            gamma_corrected = gamma_corrected.astype(np.uint8)
            plate_images_3, coords_3, processed_3 = preprocessor.preprocess_for_ocr(gamma_corrected)
            
            if plate_images_3:
                plate_text_3, confidence_3, ocr_results_3 = ocr_detector.detect_plate(plate_images_3)
                if validate_vietnamese_plate(plate_text_3):
                    attempts.append((plate_text_3, confidence_3, "OpenCV_Gamma"))
            
            # Choose best attempt
            if attempts:
                attempts.sort(key=lambda x: x[1], reverse=True)
                plate_text, confidence, method = attempts[0]
        
        # Read image for display
        image = cv2.imread(filepath)
        img_base64 = encode_image_to_base64(image)
        
        # Clean up
        os.remove(filepath)
        
        if plate_text and plate_text != "Không phát hiện được biển số" and confidence > 0.25:  # Giảm từ 0.3
            return jsonify({
                'success': True,
                'plate_number': plate_text,
                'confidence': float(confidence),
                'method': method,
                'image': img_base64
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Không phát hiện được biển số hợp lệ. Vui lòng thử:\n• Ảnh rõ hơn, zoom vào biển số\n• Ánh sáng tốt hơn\n• Góc chụp thẳng',
                'image': img_base64
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process-dicom', methods=['POST'])
def process_dicom():
    """API endpoint for DICOM image processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process DICOM
        from dicom_processor import DicomProcessor
        processor = DicomProcessor()
        
        result = processor.process_dicom(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/adjust-window', methods=['POST'])
def adjust_window():
    """API endpoint for DICOM windowing adjustment"""
    data = request.json
    
    try:
        from dicom_processor import DicomProcessor
        processor = DicomProcessor()
        
        result = processor.adjust_window(
            data['image_data'],
            data['window_center'],
            data['window_width']
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("WEB APPLICATION - License Plate Recognition & DICOM Processing")
    print("=" * 70)
    print("Starting Flask server...")
    print("Access at: http://localhost:5000")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)
