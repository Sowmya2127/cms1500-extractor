import pytesseract
from PIL import Image
import platform

# Windows needs explicit path; Mac/Linux find it on PATH automatically
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def run_ocr(image_path: str) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)