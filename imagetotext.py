import pytesseract as tess
from PIL import Image

tess.pytesseract.tesseract_cmd = r'C:\\Users\\naman\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

img = Image.open('image.png')
text = tess.image_to_string(img)
print(text)
