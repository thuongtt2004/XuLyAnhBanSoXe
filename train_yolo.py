"""
Script tự động train YOLO model cho license plate detection
"""
import os
from pathlib import Path

def prepare_dataset():
    """Chuẩn bị dataset.yaml với đường dẫn tuyệt đối"""
    dataset_config = f"""
# License Plate Detection Dataset
path: d:/game/archive  # Dataset root directory
train: images/train  # Train images
val: images/val      # Validation images

# Classes
nc: 2  # Number of classes
names: ['BSD', 'BSV']  # Class names (Biển Số Dài, Biển Số Vuông)
"""
    
    with open("d:/game/dataset_config.yaml", "w", encoding="utf-8") as f:
        f.write(dataset_config)
    
    print("✓ Dataset config đã được tạo")
    return "d:/game/dataset_config.yaml"

def train_model():
    """Train YOLOv8 model"""
    try:
        from ultralytics import YOLO
        
        print("\n=== BẮT ĐẦU TRAINING YOLO MODEL ===\n")
        
        # Chuẩn bị dataset
        config_path = prepare_dataset()
        
        # Load YOLOv8 nano model (nhanh, nhẹ)
        print("📥 Đang tải YOLOv8n model...")
        model = YOLO('yolov8n.pt')
        
        # Train model
        print("\n🚀 Bắt đầu training...\n")
        results = model.train(
            data=config_path,
            epochs=10,              # 10 epochs cho nhanh
            imgsz=416,              # Giảm size để train nhanh hơn
            batch=24,               # Tăng batch size
            device='cpu',           # Dùng CPU (đổi thành '0' nếu có GPU)
            workers=2,              # Giảm workers để tránh overhead
            project='d:/game/runs', # Nơi lưu kết quả
            name='license_plate',   # Tên experiment
            patience=5,             # Early stopping patience
            save=True,              # Lưu checkpoints
            exist_ok=True,          # Ghi đè nếu đã tồn tại
            pretrained=True,        # Dùng pretrained weights
            optimizer='Adam',       # Optimizer
            verbose=True,           # Hiển thị chi tiết
            seed=42,                # Random seed
            deterministic=True,     # Reproducible results
            single_cls=False,       # Multi-class detection
            rect=False,             # Rectangular training
            cos_lr=True,            # Cosine learning rate scheduler
            close_mosaic=10,        # Disable mosaic trong 10 epochs cuối
            amp=False,              # Tắt AMP cho CPU
            fraction=1.0,           # Dùng 100% dataset
            profile=False,          # Tắt profiling
            freeze=None,            # Không freeze layers
            lr0=0.01,               # Initial learning rate
            lrf=0.01,               # Final learning rate
            momentum=0.937,         # SGD momentum
            weight_decay=0.0005,    # Weight decay
            warmup_epochs=3,        # Warmup epochs
            warmup_momentum=0.8,    # Warmup momentum
            box=7.5,                # Box loss gain
            cls=0.5,                # Classification loss gain
            dfl=1.5,                # Distribution Focal Loss gain
            plots=False,            # Tắt plots để nhanh hơn
            cache='ram',            # Cache vào RAM để đọc nhanh hơn
        )
        
        print("\n✓ TRAINING HOÀN TẤT!\n")
        print(f"📊 Kết quả lưu tại: {results.save_dir}")
        print(f"🎯 Best weights: {results.save_dir}/weights/best.pt")
        
        # Validate model
        print("\n📈 Đang validate model...")
        metrics = model.val()
        print(f"\nmAP50: {metrics.box.map50:.4f}")
        print(f"mAP50-95: {metrics.box.map:.4f}")
        
        return results.save_dir
        
    except ImportError:
        print("❌ Chưa cài đặt ultralytics!")
        print("📥 Đang cài đặt...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'ultralytics'])
        print("✓ Đã cài đặt. Vui lòng chạy lại script.")
        return None
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_model(model_path="d:/game/runs/license_plate/weights/best.pt"):
    """Test model với một số ảnh mẫu"""
    try:
        from ultralytics import YOLO
        import cv2
        import random
        
        print(f"\n=== TEST MODEL: {model_path} ===\n")
        
        # Load trained model
        model = YOLO(model_path)
        
        # Lấy ngẫu nhiên 5 ảnh từ val set
        val_images = list(Path("d:/game/archive/images/val").glob("*.jpg"))
        test_images = random.sample(val_images, min(5, len(val_images)))
        
        print(f"🔍 Testing trên {len(test_images)} ảnh...\n")
        
        for img_path in test_images:
            results = model(str(img_path), conf=0.25, verbose=False)
            
            # Hiển thị kết quả
            detections = results[0].boxes
            print(f"📸 {img_path.name}: {len(detections)} biển số phát hiện")
            
            for i, box in enumerate(detections):
                conf = box.conf[0]
                cls = int(box.cls[0])
                cls_name = 'BSD' if cls == 0 else 'BSV'
                print(f"   └─ [{cls_name}] Confidence: {conf:.2%}")
        
        print("\n✓ Test hoàn tất!")
        
    except Exception as e:
        print(f"❌ Lỗi test: {e}")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════╗
║   🚗 YOLO LICENSE PLATE DETECTION TRAINING 🚗        ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # Train model
    save_dir = train_model()
    
    if save_dir:
        print("\n" + "="*60)
        print("🎉 TRAINING THÀNH CÔNG!")
        print("="*60)
        
        # Test model
        model_path = f"{save_dir}/weights/best.pt"
        if os.path.exists(model_path):
            test_model(model_path)
        
        print(f"""
📂 KẾT QUẢ:
   - Best model: {model_path}
   - Training logs: {save_dir}
   
📝 BƯỚC TIẾP THEO:
   1. Kiểm tra metrics trong {save_dir}
   2. Integrate model vào main.py
   3. So sánh với phương pháp cũ
        """)
