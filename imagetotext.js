// Import Tesseract.js library
const Tesseract = require('tesseract.js');

// Function to perform OCR on an image file
function performOCR(imageFilePath) {
    // Load the image file
    Tesseract.recognize(
        imageFilePath, // Path to the image file
        'eng', // Language (English in this case)
        { logger: m => console.log(m) } // Logger function to output progress messages
    ).then(({ data: { text } }) => {
        // Output the extracted text
        console.log('Extracted Text:', text);
    }).catch(error => {
        // Handle any errors that occur during OCR
        console.error('Error:', error);
    });
}

// Example usage: Perform OCR on an image file
performOCR('image2.jpg');
