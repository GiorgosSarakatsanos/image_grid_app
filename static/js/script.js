document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData(this);

    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        displayPDF(data.pdf_url);
    })
    .catch(error => console.error('Error:', error));
});

function displayPDF(pdfUrl) {
    let pdfContainer = document.getElementById('pdf-container');
    pdfContainer.innerHTML = `<iframe src="${pdfUrl}" frameborder="0"></iframe>`;
}

document.getElementById('paper_type').addEventListener('change', function() {
    const userDefinedDimensions = document.getElementById('user_defined_dimensions');
    if (this.value === 'user_defined') {
        userDefinedDimensions.style.display = 'block';
    } else {
        userDefinedDimensions.style.display = 'none';
    }
});

document.getElementById('image_size').addEventListener('change', function() {
    const customImageSize = document.getElementById('custom_image_size');
    if (this.value === 'custom') {
        customImageSize.style.display = 'block';
    } else {
        customImageSize.style.display = 'none';
    }
});
