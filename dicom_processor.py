"""
DICOM Image Processor
Handles medical imaging (DICOM format) with windowing/leveling
"""
import numpy as np
import cv2
import base64
from io import BytesIO


class DicomProcessor:
    """DICOM image processing with windowing/leveling"""
    
    def __init__(self):
        """Initialize DICOM processor"""
        self.dicom_available = False
        try:
            import pydicom
            self.pydicom = pydicom
            self.dicom_available = True
            print("✓ DICOM support enabled (pydicom)")
        except ImportError:
            print("⚠ DICOM support disabled (install pydicom)")
    
    def process_dicom(self, filepath):
        """
        Process DICOM file and extract image data
        
        Args:
            filepath: Path to DICOM file
            
        Returns:
            dict: Processing result with image and metadata
        """
        if not self.dicom_available:
            return {
                'success': False,
                'error': 'DICOM support not available. Install pydicom.'
            }
        
        try:
            # Read DICOM file
            ds = self.pydicom.dcmread(filepath)
            
            # Extract pixel data
            pixel_array = ds.pixel_array
            
            # Get metadata
            metadata = {
                'patient_name': str(ds.get('PatientName', 'Unknown')),
                'patient_id': str(ds.get('PatientID', 'Unknown')),
                'study_date': str(ds.get('StudyDate', 'Unknown')),
                'modality': str(ds.get('Modality', 'Unknown')),
                'rows': int(ds.Rows),
                'columns': int(ds.Columns),
                'bits_stored': int(ds.BitsStored),
            }
            
            # Get window center/width if available
            window_center = float(ds.get('WindowCenter', 40))
            window_width = float(ds.get('WindowWidth', 400))
            
            # Apply windowing
            windowed_image = self.apply_windowing(
                pixel_array, window_center, window_width
            )
            
            # Convert to base64
            img_base64 = self.encode_image(windowed_image)
            
            return {
                'success': True,
                'image': img_base64,
                'metadata': metadata,
                'window_center': window_center,
                'window_width': window_width,
                'min_value': float(np.min(pixel_array)),
                'max_value': float(np.max(pixel_array))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process DICOM: {str(e)}'
            }
    
    def apply_windowing(self, pixel_array, center, width):
        """
        Apply windowing/leveling to DICOM image
        
        Args:
            pixel_array: Raw pixel data
            center: Window center (level)
            width: Window width
            
        Returns:
            Windowed image (0-255)
        """
        # Calculate window bounds
        lower = center - width / 2
        upper = center + width / 2
        
        # Apply windowing
        windowed = np.clip(pixel_array, lower, upper)
        
        # Normalize to 0-255
        windowed = ((windowed - lower) / (upper - lower) * 255).astype(np.uint8)
        
        return windowed
    
    def adjust_window(self, image_data, center, width):
        """
        Adjust window center/width for existing image
        
        Args:
            image_data: Base64 encoded image or pixel array
            center: New window center
            width: New window width
            
        Returns:
            dict: Adjusted image result
        """
        try:
            # Decode image if base64
            if isinstance(image_data, str):
                # Remove data URL prefix if present
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                
                # Decode base64
                img_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                pixel_array = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            else:
                pixel_array = np.array(image_data)
            
            # Apply windowing
            windowed = self.apply_windowing(pixel_array, center, width)
            
            # Encode result
            img_base64 = self.encode_image(windowed)
            
            return {
                'success': True,
                'image': img_base64
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to adjust window: {str(e)}'
            }
    
    def encode_image(self, image):
        """
        Encode image to base64 string
        
        Args:
            image: NumPy array
            
        Returns:
            Base64 encoded string
        """
        # Ensure uint8
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)
        
        # Encode to JPEG
        _, buffer = cv2.imencode('.jpg', image)
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{img_str}"
    
    def enhance_image(self, pixel_array, method='clahe'):
        """
        Enhance DICOM image using various methods
        
        Args:
            pixel_array: Raw pixel data
            method: Enhancement method ('clahe', 'histogram', 'sharpen')
            
        Returns:
            Enhanced image
        """
        # Normalize to 0-255
        normalized = cv2.normalize(pixel_array, None, 0, 255, cv2.NORM_MINMAX)
        normalized = normalized.astype(np.uint8)
        
        if method == 'clahe':
            # CLAHE enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(normalized)
        
        elif method == 'histogram':
            # Histogram equalization
            enhanced = cv2.equalizeHist(normalized)
        
        elif method == 'sharpen':
            # Sharpening
            kernel = np.array([[-1, -1, -1],
                             [-1,  9, -1],
                             [-1, -1, -1]])
            enhanced = cv2.filter2D(normalized, -1, kernel)
        
        else:
            enhanced = normalized
        
        return enhanced


if __name__ == "__main__":
    print("DICOM Processor Module")
    print("=" * 50)
    processor = DicomProcessor()
    
    if processor.dicom_available:
        print("✓ Ready to process DICOM files")
    else:
        print("✗ Install pydicom: pip install pydicom")
