"""
Create demo DICOM file from regular image
Requires: pip install pydicom pillow
"""
import numpy as np
from PIL import Image
import datetime

try:
    import pydicom
    from pydicom.dataset import Dataset, FileDataset
    
    print("=" * 70)
    print("CREATE DEMO DICOM FILE")
    print("=" * 70)
    print()
    
    # Load a regular image (grayscale)
    img_path = input("Enter image path (or press Enter for demo): ").strip()
    
    if not img_path:
        # Create a simple demo image
        print("Creating demo grayscale image...")
        img_array = np.random.randint(0, 255, (512, 512), dtype=np.uint16)
    else:
        # Load from file
        print(f"Loading image: {img_path}")
        img = Image.open(img_path).convert('L')  # Convert to grayscale
        img_array = np.array(img, dtype=np.uint16)
    
    print(f"Image size: {img_array.shape}")
    
    # Create DICOM dataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = '1.2.3.4'
    file_meta.ImplementationClassUID = '1.2.3.4'
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    
    ds = FileDataset("demo.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # Patient info
    ds.PatientName = "Demo^Patient"
    ds.PatientID = "123456"
    ds.PatientBirthDate = "19900101"
    ds.PatientSex = "M"
    
    # Study info
    ds.StudyDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.StudyTime = datetime.datetime.now().strftime("%H%M%S")
    ds.StudyDescription = "Demo Study"
    ds.Modality = "CT"
    
    # Image info
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.Rows = img_array.shape[0]
    ds.Columns = img_array.shape[1]
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    
    # Windowing
    ds.WindowCenter = 40
    ds.WindowWidth = 400
    
    # Pixel data
    ds.PixelData = img_array.tobytes()
    
    # Save
    output_path = "dicom_samples/demo.dcm"
    import os
    os.makedirs('dicom_samples', exist_ok=True)
    
    ds.save_as(output_path)
    
    print()
    print(f"✓ DICOM file created: {output_path}")
    print()
    print("You can now:")
    print("1. Go to http://localhost:5000/dicom")
    print("2. Upload demo.dcm")
    print("3. Test windowing/leveling")
    print()
    print("=" * 70)

except ImportError:
    print("=" * 70)
    print("ERROR: pydicom not installed")
    print("=" * 70)
    print()
    print("Install with:")
    print("  py -m pip install pydicom pillow")
    print()
    print("=" * 70)
except Exception as e:
    print(f"Error: {e}")
