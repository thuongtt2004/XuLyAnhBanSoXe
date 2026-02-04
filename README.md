# License Plate Recognition & DICOM Image Processing

A comprehensive computer vision application for automatic license plate recognition and DICOM medical image processing, featuring both GUI and web interfaces.

## Features

### License Plate Recognition
- Automatic license plate detection from images
- OCR (Optical Character Recognition) for text extraction
- YOLO-based object detection integration
- Support for Vietnamese and English characters
- Multiple preprocessing methods for enhanced accuracy

### DICOM Image Processing
- Medical image (DICOM) file handling and visualization
- DICOM metadata extraction
- Image preprocessing and enhancement
- Web-based DICOM viewer

### User Interfaces
- **Desktop GUI**: Tkinter-based application for standalone use
- **Web Application**: Flask-based web interface for remote access
- Real-time image processing and visualization

## Installation

### Requirements
- Python 3.8+
- OpenCV
- EasyOCR
- PyTorch
- Flask (for web app)
- Pillow
- NumPy

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd game
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

For web application:
```bash
pip install -r requirements_web.txt
```

## Usage

### Desktop Application
Run the GUI application:
```bash
python main.py
```

### Web Application
Start the Flask web server:
```bash
python web_app.py
```
Then open your browser and navigate to `http://localhost:5000`

### Command Line
For batch processing or testing:
```bash
python quick_test.py
```

## Project Structure

- `main.py` - Main GUI application
- `web_app.py` - Flask web application
- `license_plate_detector.py` - License plate detection module
- `yolo_detector.py` - YOLO-based detection
- `dicom_processor.py` - DICOM file processing
- `preprocess_image.py` - Image preprocessing utilities
- `utils.py` - Helper functions
- `config.py` - Configuration settings
- `templates/` - HTML templates for web app
- `static/` - CSS and JavaScript files
- `uploads/` - Temporary upload directory

## Configuration

Edit `config.py` or `dataset_config.yaml` to customize:
- Detection parameters
- OCR settings
- Model paths
- Processing options

## Training

To train custom YOLO models:
```bash
python train_yolo.py
```

## Testing

Run various test suites:
```bash
python test_full_detection.py
python test_ocr_extraction.py
python test_validation.py
```

## Technologies

- **Computer Vision**: OpenCV, YOLO
- **OCR**: EasyOCR
- **Deep Learning**: PyTorch
- **GUI**: Tkinter
- **Web**: Flask, HTML/CSS/JavaScript
- **Medical Imaging**: pydicom

## License

This project is for educational and research purposes.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Author

Developed as part of a computer vision and image processing project.
