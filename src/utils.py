import pytesseract
from PIL import Image
import io
import base64
from pypdf import PdfReader
from docx import Document
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Set Tesseract path from .env
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")

def heavy_clean(text):
    """Removes noise and extra symbols"""

    # Remove quoted text safely
    text = re.sub(r'".*?"', '', text)

    # Remove extra spaces/newlines
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def extract_amounts_regex(text):
    """Hard-coded regex to catch currency that AI might miss."""
    # Matches symbols like $, ₹, £, € followed by numbers.
    pattern = r"([$₹£€]\s?\d+(?:,\d+)*(?:\.\d+)?)"
    percentages = r"(\d+(?:\.\d+)?%)"
    found = re.findall(pattern, text) + re.findall(percentages, text)
    return list(set(found))

def extract_text_from_base64(file_base64, file_type):
    """Extracts text based on file format: PDF, DOCX, or Image."""
    file_bytes = base64.b64decode(file_base64)
    text = ""

    if file_type.lower() == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text += page.extract_text() or ""
            
    elif file_type.lower() == "docx":
        doc = Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
            
    elif file_type.lower() == "image":
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img)
        
    return heavy_clean(text)