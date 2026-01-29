let currentImageData = null;
let currentMetadata = null;

async function processDicom() {
    const fileInput = document.getElementById('dicomInput');
    const resultDiv = document.getElementById('dicomResult');
    const resultContent = document.getElementById('dicomContent');
    
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Vui lòng chọn file DICOM!');
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
        const response = await fetch('/api/process-dicom', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentImageData = data.image;
            currentMetadata = data.metadata;
            
            // Setup windowing controls
            const centerSlider = document.getElementById('windowCenter');
            const widthSlider = document.getElementById('windowWidth');
            
            centerSlider.value = data.window_center;
            widthSlider.value = data.window_width;
            centerSlider.min = data.min_value;
            centerSlider.max = data.max_value;
            
            // Show result
            displayDicomResult(data);
            
            // Add event listeners
            centerSlider.oninput = () => adjustWindow();
            widthSlider.oninput = () => adjustWindow();
        } else {
            resultContent.innerHTML = `
                <div class="error">
                    <h3>❌ Lỗi xử lý DICOM</h3>
                    <p>${data.error}</p>
                </div>
            `;
        }
    } catch (error) {
        resultContent.innerHTML = `
            <div class="error">
                <h3>❌ Lỗi</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

function displayDicomResult(data) {
    const resultContent = document.getElementById('dicomContent');
    
    resultContent.innerHTML = `
        <div class="success">
            <h3>✅ Xử lý thành công!</h3>
        </div>
        <img src="${data.image}" class="result-image" id="dicomImage" alt="DICOM">
        <div class="result-info">
            <h3>📊 Thông tin DICOM</h3>
            <p><strong>Bệnh nhân:</strong> ${data.metadata.patient_name}</p>
            <p><strong>ID:</strong> ${data.metadata.patient_id}</p>
            <p><strong>Ngày:</strong> ${data.metadata.study_date}</p>
            <p><strong>Loại:</strong> ${data.metadata.modality}</p>
            <p><strong>Kích thước:</strong> ${data.metadata.columns} x ${data.metadata.rows}</p>
            <p><strong>Window Center:</strong> <span id="centerValue">${data.window_center}</span></p>
            <p><strong>Window Width:</strong> <span id="widthValue">${data.window_width}</span></p>
        </div>
    `;
}

async function adjustWindow() {
    const centerSlider = document.getElementById('windowCenter');
    const widthSlider = document.getElementById('windowWidth');
    const centerValue = document.getElementById('centerValue');
    const widthValue = document.getElementById('widthValue');
    const dicomImage = document.getElementById('dicomImage');
    
    const center = parseFloat(centerSlider.value);
    const width = parseFloat(widthSlider.value);
    
    // Update display
    centerValue.textContent = center.toFixed(0);
    widthValue.textContent = width.toFixed(0);
    
    try {
        const response = await fetch('/api/adjust-window', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_data: currentImageData,
                window_center: center,
                window_width: width
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            dicomImage.src = data.image;
        }
    } catch (error) {
        console.error('Error adjusting window:', error);
    }
}
