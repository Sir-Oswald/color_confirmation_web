const allowedColors = {
    "Red": "#FF0000",
    "Orange": "#FFA500",
    "Yellow": "#FFFF00",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Purple": "#800080",
    "Pink": "#FFC0CB",
    "Brown": "#964B00",
    "Black": "#000000",
    "Gray": "#808080",
    "White": "#FFFFFF",
    "Beige": "#F5F5DC",
    "Gold": "#FFD700",
    "Silver": "#C0C0C0",
    "Bronze": "#CD7F32",
    "Copper": "#B87333",
    "Rose Gold": "#B76E79"
};

let currentPatternIndex = 0;
let currentImageIndex = 0;
let patternFolders = [];
let currentImages = [];

document.addEventListener('DOMContentLoaded', () => {
    initializeColorButtons();
    loadPatternFolders();
    
    document.getElementById('prev-button').addEventListener('click', showPreviousImage);
    document.getElementById('next-button').addEventListener('click', showNextImage);
    document.getElementById('download-results').addEventListener('click', downloadResults);
    document.getElementById('delete-results').addEventListener('click', deleteResults);
});

function initializeColorButtons() {
    const primaryColorButtons = document.getElementById('primary-color-buttons');
    const secondaryColorButtons = document.getElementById('secondary-color-buttons');
    
    if (!primaryColorButtons || !secondaryColorButtons) {
        console.error('Color button containers not found');
        return;
    }
    
    for (const [colorName, colorValue] of Object.entries(allowedColors)) {
        const primaryButton = createColorButton(colorName, colorValue, 'primary');
        const secondaryButton = createColorButton(colorName, colorValue, 'secondary');
        
        primaryColorButtons.appendChild(primaryButton);
        secondaryColorButtons.appendChild(secondaryButton);
    }
}

function createColorButton(colorName, colorValue, type) {
    const button = document.createElement('button');
    button.textContent = colorName;
    button.style.backgroundColor = colorValue;
    button.style.color = getContrastColor(colorValue);
    button.classList.add('color-button');
    button.dataset.color = colorName;
    button.addEventListener('click', () => selectColor(type, colorName));
    return button;
}

function getContrastColor(hexColor) {
    const r = parseInt(hexColor.substr(1, 2), 16);
    const g = parseInt(hexColor.substr(3, 2), 16);
    const b = parseInt(hexColor.substr(5, 2), 16);
    
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    
    return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

function selectColor(type, colorName) {
    const buttons = document.querySelectorAll(`#${type}-color-buttons .color-button`);
    buttons.forEach(button => button.classList.remove('selected'));
    
    const selectedButton = document.querySelector(`#${type}-color-buttons .color-button[data-color="${colorName}"]`);
    if (selectedButton) {
        selectedButton.classList.add('selected');
        updateSwatch(type, colorName);
        saveColors();
    } else {
        console.error(`Button for ${colorName} not found`);
    }
}

function updateSwatch(type, colorName) {
    const swatch = document.getElementById(`${type}-swatch`);
    const colorNameElement = document.getElementById(`${type}-color-name`);
    
    if (!swatch || !colorNameElement) {
        console.error(`Swatch elements for ${type} not found`);
        return;
    }
    
    swatch.style.backgroundColor = allowedColors[colorName];
    colorNameElement.textContent = colorName;
}

function getSelectedColors() {
    const primaryColor = document.querySelector('#primary-color-buttons .color-button.selected')?.dataset.color || '';
    const secondaryColor = document.querySelector('#secondary-color-buttons .color-button.selected')?.dataset.color || '';
    return [primaryColor, secondaryColor];
}

function setSelectedColors(primaryColor, secondaryColor) {
    if (primaryColor) selectColor('primary', primaryColor);
    if (secondaryColor) selectColor('secondary', secondaryColor);
}

function loadPatternFolders() {
    fetch('/get_pattern_folders')
        .then(response => response.json())
        .then(data => {
            patternFolders = data.pattern_folders;
            if (patternFolders.length > 0) {
                loadSavedProgress();
                loadImagesForCurrentPattern();
            } else {
                console.log('No pattern folders found');
            }
        })
        .catch(error => console.error('Error loading pattern folders:', error));
}

function loadSavedProgress() {
    const savedPatternIndex = localStorage.getItem('currentPatternIndex');
    const savedImageIndex = localStorage.getItem('currentImageIndex');
    
    if (savedPatternIndex !== null && savedImageIndex !== null) {
        currentPatternIndex = parseInt(savedPatternIndex);
        currentImageIndex = parseInt(savedImageIndex);
        
        currentPatternIndex = Math.min(currentPatternIndex, patternFolders.length - 1);
    }
}

function saveProgress() {
    localStorage.setItem('currentPatternIndex', currentPatternIndex);
    localStorage.setItem('currentImageIndex', currentImageIndex);
}

function loadImagesForCurrentPattern() {
    const currentFolder = patternFolders[currentPatternIndex];
    fetch(`/get_images?folder=${encodeURIComponent(currentFolder)}`)
        .then(response => response.json())
        .then(data => {
            currentImages = data.images;
            if (currentImages.length > 0) {
                currentImageIndex = Math.min(currentImageIndex, currentImages.length - 1);
                showCurrentImage();
            } else {
                console.log('No images found in the current folder');
            }
        })
        .catch(error => console.error('Error loading images:', error));
}

function showCurrentImage() {
    if (currentImages.length === 0) {
        console.log('No images to display');
        return;
    }
    const currentImage = currentImages[currentImageIndex];
    const imagePath = `/pattern_image/${encodeURIComponent(patternFolders[currentPatternIndex])}/${encodeURIComponent(currentImage)}`;
    document.getElementById('current-image').src = imagePath;
    getImageColors();
    updateProgress();
    saveProgress();
}

function getImageColors() {
    const data = {
        pattern_folder: patternFolders[currentPatternIndex],
        image_name: currentImages[currentImageIndex]
    };
    
    fetch('/get_image_colors', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error getting image colors:', data.error);
        } else {
            setSelectedColors(data.colors[0], data.colors[1]);
        }
    })
    .catch(error => console.error('Error getting image colors:', error));
}

function saveColors(callback) {
    const [primaryColor, secondaryColor] = getSelectedColors();
    const data = {
        pattern_folder: patternFolders[currentPatternIndex],
        file_name: currentImages[currentImageIndex],
        colors: [primaryColor, secondaryColor]
    };
    
    fetch('/save_colors', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message);
        if (callback) callback();
    })
    .catch(error => {
        console.error('Error saving colors:', error);
    });
}

function showPreviousImage() {
    saveColors(() => {
        if (currentImageIndex > 0) {
            currentImageIndex--;
        } else if (currentPatternIndex > 0) {
            currentPatternIndex--;
            loadImagesForCurrentPattern();
            return;
        }
        showCurrentImage();
    });
}

function showNextImage() {
    saveColors(() => {
        if (currentImageIndex < currentImages.length - 1) {
            currentImageIndex++;
        } else if (currentPatternIndex < patternFolders.length - 1) {
            currentPatternIndex++;
            currentImageIndex = 0;
            loadImagesForCurrentPattern();
            return;
        }
        showCurrentImage();
    });
}

function updateProgress() {
    const totalPatterns = patternFolders.length;
    const currentPattern = currentPatternIndex + 1;
    const totalImages = currentImages.length;
    const currentImage = currentImageIndex + 1;
    document.getElementById('progress').textContent = `Pattern: ${currentPattern}/${totalPatterns}, Image: ${currentImage}/${totalImages}`;
}

function downloadResults() {
    window.location.href = '/download_results';
}

function deleteResults() {
    if (confirm("Are you sure you want to delete all results? This action cannot be undone.")) {
        fetch('/delete_results', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            })
            .catch(error => console.error('Error deleting results:', error));
    }
}