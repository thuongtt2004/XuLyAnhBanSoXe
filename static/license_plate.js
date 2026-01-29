async function detectPlate() {
    const fileInput = document.getElementById('fileInput');
    const resultDiv = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Vui lòng chọn ảnh!');
        return;
    }
    
    // Show loading
    resultDiv.style.display = 'block';
    resultContent.innerHTML = '<div class="loading"></div>';
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        // Send request
        const response = await fetch('/api/detect-plate', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success result
            resultContent.innerHTML = `
                <div class="success">
                    <h3>✅ Phát hiện thành công!</h3>
                </div>
                <img src="${data.image}" class="result-image" alt="Result">
                <div class="result-info">
                    <h3>📋 Biển số: ${data.plate_number}</h3>
                    <p>🎯 Độ tin cậy: ${(data.confidence * 100).toFixed(1)}%</p>
                    <p>🔧 Phương pháp: ${data.method}</p>
                    <p>🚀 Engine: YOLO AI + EasyOCR</p>
                </div>
            `;
        } else {
            // Show error
            resultContent.innerHTML = `
                <div class="error">
                    <h3>❌ Không phát hiện được biển số</h3>
                    <p>${data.error || 'Vui lòng thử ảnh khác'}</p>
                </div>
                ${data.image ? `<img src="${data.image}" class="result-image" alt="Input">` : ''}
            `;
        }
    } catch (error) {
        resultContent.innerHTML = `
            <div class="error">
                <h3>❌ Lỗi xử lý</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// Preview image on select
document.getElementById('fileInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        console.log('Selected file:', file.name);
    }
});
