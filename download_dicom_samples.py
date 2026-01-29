"""
Download sample DICOM files for testing
"""
import urllib.request
import os

# Create samples folder
os.makedirs('dicom_samples', exist_ok=True)

print("=" * 70)
print("DOWNLOADING SAMPLE DICOM FILES")
print("=" * 70)
print()

# Sample DICOM URLs (from public datasets)
samples = [
    {
        'name': 'chest_xray.dcm',
        'url': 'https://www.rubomedical.com/dicom_files/chest.dcm',
        'description': 'Chest X-Ray'
    },
    {
        'name': 'ct_scan.dcm', 
        'url': 'https://www.rubomedical.com/dicom_files/ct_head.dcm',
        'description': 'CT Head Scan'
    }
]

for sample in samples:
    try:
        print(f"Downloading: {sample['description']}")
        print(f"  URL: {sample['url']}")
        
        filepath = os.path.join('dicom_samples', sample['name'])
        urllib.request.urlretrieve(sample['url'], filepath)
        
        print(f"  ✓ Saved to: {filepath}")
        print()
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        print()

print("=" * 70)
print("ALTERNATIVE: Download from these sources:")
print("=" * 70)
print()
print("1. Medical Image Samples:")
print("   https://www.rubomedical.com/dicom_files/")
print()
print("2. DICOM Library:")
print("   https://www.dicomlibrary.com/")
print()
print("3. Cancer Imaging Archive:")
print("   https://www.cancerimagingarchive.net/")
print()
print("4. Sample DICOM Files:")
print("   https://barre.dev/medical/samples/")
print()
print("=" * 70)
print("HOW TO USE:")
print("=" * 70)
print("1. Download any .dcm file from above sources")
print("2. Go to http://localhost:5000/dicom")
print("3. Upload the .dcm file")
print("4. Adjust windowing/leveling")
print("=" * 70)
