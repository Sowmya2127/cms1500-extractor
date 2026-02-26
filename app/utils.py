import fitz  # PyMuPDF
import os

def pdf_to_images(pdf_path: str, output_dir: str = "outputs") -> list:
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(output_dir, f"page_{i}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    return image_paths