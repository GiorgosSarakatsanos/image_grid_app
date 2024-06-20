document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData(this);

    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        displayImages(data.images);
        // Show 'Print to PDF' button after displaying images
        document.getElementById('printToPdfBtn').style.display = 'block';
    })
    .catch(error => console.error('Error:', error));
});

function displayImages(images) {
    let gridContainer = document.getElementById('grid-container');
    gridContainer.innerHTML = '';

    images.forEach(imageUrl => {
        let img = document.createElement('img');
        img.src = imageUrl;
        img.classList.add('img-preview');
        gridContainer.appendChild(img);
    });
}

document.getElementById('paper_type').addEventListener('change', function() {
    const userDefinedDimensions = document.getElementById('user_defined_dimensions');
    if (this.value === 'user_defined') {
        userDefinedDimensions.style.display = 'block';
    } else {
        userDefinedDimensions.style.display = 'none';
    }
});