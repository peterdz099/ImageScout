import io
from PIL import (Image)
import fitz


def extrac_images_from_pdf(pdf_path):
    all_images = []
    pdf_file = fitz.open(pdf_path)
    for page_index in range(len(pdf_file)):
        page = pdf_file[page_index]
        image_list = page.get_images(full=True)
        if image_list:
            for img in image_list:
                xref = img[0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                if image.width > 35 and image.height > 35:
                    all_images.append(io.BytesIO(image_bytes))
    return all_images
