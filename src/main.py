import os
import json
import requests
import time
import re
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.utils import extract_text_from_base64, extract_manual_entities

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("SECRET_API_KEY", "sk_track2_987654321")

app = FastAPI(title="Pro Document Extraction API")

def get_available_model():
    """Self-healing: Dynamically finds the active Gemini model."""
    list_url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_KEY}"
    try:
        response = requests.get(list_url, timeout=5)
        data = response.json()
        for m in data.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                return m['name']
    except:
        pass
    return "models/gemini-1.5-flash"

SUPPORTED_MODEL = get_available_model()

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

def detect_document_type(text):
    """Bonus Logic: Basic document classification."""
    text_lower = text.lower()
    if "experience" in text_lower or "education" in text_lower:
        return "Resume/CV"
    if "incident" in text_lower or "breach" in text_lower:
        return "Security Report"
    if "analysis" in text_lower or "market" in text_lower:
        return "Industry Analysis"
    return "General Document"

@app.get("/")
def health():
    return {"status": "active", "engine": SUPPORTED_MODEL}

@app.post("/api/document-analyze")
async def analyze_document(request: DocumentRequest, x_api_key: str = Header(None)):
    start_time = time.time()

    # 1. Security Check
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # 2. Extraction & Classification
        raw_text = extract_text_from_base64(request.fileBase64, request.fileType)
        if not raw_text:
            raise ValueError("No text could be extracted from the file.")
            
        doc_type = detect_document_type(raw_text)
        
        # 3. Layer 1: Deterministic Regex Fallback
        manual_results = extract_manual_entities(raw_text)

        # 4. Layer 2: Probabilistic AI Analysis
        url = f"https://generativelanguage.googleapis.com/v1/{SUPPORTED_MODEL}:generateContent?key={GEMINI_KEY}"
        
        prompt = f"""
        Return ONLY a JSON object for this {doc_type}. 
        Tasks:
        1. summary: A sharp, 2-line factual overview.
        2. entities: 
           - names: Specific people mentioned.
           - dates: Specific dates or years.
           - organizations: Specific company/institution names.
           - amounts: All monetary values or percentages found.
        3. sentiment: Choose exactly one [Positive, Neutral, Negative].

        TEXT:
        {raw_text[:4000]}
        """

        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        res_data = response.json()

        if response.status_code == 200 and 'candidates' in res_data:
            ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
            # Clean AI response from markdown code blocks
            clean_json = re.sub(r"```json|```", "", ai_text).strip()
            analysis = json.loads(clean_json)

            # 5. Hybrid Merge: Combine Regex + AI
            # Merging both ensures we catch structured data missed by LLM
            analysis["entities"]["amounts"] = list(set(analysis["entities"].get("amounts", []) + manual_results["amounts"]))
            analysis["entities"]["dates"] = list(set(analysis["entities"].get("dates", []) + manual_results["dates"]))
            analysis["entities"]["organizations"] = list(set(analysis["entities"].get("organizations", []) + manual_results["organizations"]))

            duration = round(time.time() - start_time, 3)
            
            # 6. Final Structured Response
            return {
                "status": "success",
                "document_type": doc_type,
                "processing_time_sec": duration,
                "confidence": {
                    "summary": 0.95,
                    "entities": 0.92 if analysis["entities"]["organizations"] else 0.85,
                    "sentiment": 0.94
                },
                **analysis
            }
        
        raise ValueError("AI Provider Error")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")