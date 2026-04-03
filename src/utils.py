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
    """Sanitizes text by removing noise without losing critical data."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable ASCII characters common in OCR noise
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()

def extract_manual_entities(text):
    """
    Layer 2: Deterministic Regex Fallback
    Greedy patterns to catch data LLMs might skip.
    """
    # 1. Amounts & Percentages (e.g., $500, 20%, 50 USD)
    currency_pattern = r"([\$₹£€]\s?\d+(?:,\d+)*(?:\.\d+)?|\d+(?:,\d+)*(?:\.\d+)?\s?(?:USD|INR|EUR|GBP|dollars|rupees))"
    percent_pattern = r"(\d+(?:\.\d+)?%)"
    
    # 2. Dates (e.g., 03/04/2026, March 12, 2024, or just 2025)
    date_pattern = r"(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b|\b\d{4}\b)"
    
    # 3. Keyword Organization Detector (e.g., 'ABC Solutions', 'Global Bank')
    org_keywords = r"\b[A-Z][a-z]+ (?:Technologies|Solutions|Bank|Inc|Ltd|Systems|Corp|University|Institute|Agency|Department)\b"
    
    amounts = re.findall(currency_pattern, text) + re.findall(percent_pattern, text)
    dates = re.findall(date_pattern, text)
    orgs = re.findall(org_keywords, text)
    
    return {
        "amounts": [a.strip() for a in set(amounts)],
        "dates": [d.strip() for d in set(dates)],
        "organizations": [o.strip() for o in set(orgs)]
    }

def extract_text_from_base64(file_base64, file_type):
    """Extracts text based on file format: PDF, DOCX, or Image."""
    try:
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
    except Exception as e:
        print(f"Extraction error: {e}")
        return ""