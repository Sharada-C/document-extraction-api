import os
import json
import requests
import time
import re
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.utils import extract_text_from_base64, extract_manual_entities

# 1. Configuration & Environment Setup
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("SECRET_API_KEY", "sk_track2_987654321")

app = FastAPI(title="High-Precision Document Extraction API")

def get_available_model():
    """Self-healing discovery to find the most capable available Gemini model."""
    list_url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_KEY}"
    try:
        response = requests.get(list_url, timeout=5)
        data = response.json()
        for m in data.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                return m['name']
    except Exception:
        pass
    return "models/gemini-1.5-flash"

SUPPORTED_MODEL = get_available_model()

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

@app.get("/")
def health():
    return {"status": "active", "engine": SUPPORTED_MODEL}

@app.post("/api/document-analyze")
async def analyze_document(request: DocumentRequest, x_api_key: str = Header(None)):
    start_time = time.time()

    # 2. Security Authentication
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # 3. Extraction & Pre-processing Guardrails
        raw_text = extract_text_from_base64(request.fileBase64, request.fileType)
        
        if not raw_text or len(raw_text.strip()) < 50:
             return {
                "status": "success",
                "document_type": "Other/Invalid",
                "processing_time_sec": round(time.time() - start_time, 3),
                "confidence": {"classification": 1.0, "summary": 0.1, "entities": 0.0, "sentiment": 0.0},
                "summary": "Document content too short or unreadable for meaningful analysis.",
                "entities": {"names": [], "organizations": [], "dates": [], "amounts": [], "domains": []},
                "sentiment": "Neutral"
            }
        
        # 4. NEW: Metadata Hinting Logic
        # This helps the AI differentiate between 'Education' in a Resume vs 'Education Sector' in a Report.
        filename_hint = request.fileName.lower()
        hint_text = ""
        if any(word in filename_hint for word in ["analysis", "report", "industry"]):
            hint_text = "SYSTEM NOTE: The filename suggests this is an Industry Report. Prioritize this over Resume/CV."
        elif any(word in filename_hint for word in ["invoice", "bill", "receipt"]):
            hint_text = "SYSTEM NOTE: The filename suggests this is an Invoice or Billing document."

        # 5. Layer 1: Deterministic Extraction (Regex)
        manual_results = extract_manual_entities(raw_text)

        # 6. Layer 2: Master Prompt with Contextual Hinting
        url = f"https://generativelanguage.googleapis.com/v1/{SUPPORTED_MODEL}:generateContent?key={GEMINI_KEY}"
        
        master_prompt = f"""
        {hint_text}
        You are a high-precision Document Analysis Engine. Your goal is ZERO hallucination.
        
        STRICT CLASSIFICATION RULES:
        1. "Industry Report": Use for technical analysis, market trends, or whitepapers discussing sectors.
        2. "Resume/CV": Use ONLY for a personal profile of ONE specific individual's career.
        3. If the text discusses 'Global sectors', 'Market trends', or 'Innovation' -> It is an Industry Report.
        
        ENTITY RULES:
        - Extract ONLY explicitly mentioned Person names, Organizations, Dates, and Amounts.
        
        OUTPUT STRICT JSON ONLY:
        {{
          "document_type": "...",
          "confidence": {{
            "classification": 0.0,
            "summary": 0.0,
            "entities": 0.0,
            "sentiment": 0.0
          }},
          "summary": "3-5 lines of factual insights.",
          "entities": {{
            "names": [],
            "organizations": [],
            "dates": [],
            "amounts": [],
            "domains": []
          }},
          "sentiment": "Positive/Neutral/Negative"
        }}

        TEXT TO ANALYZE:
        {raw_text[:4500]}
        """

        response = requests.post(url, json={"contents": [{"parts": [{"text": master_prompt}]}]}, timeout=25)
        res_data = response.json()

        if response.status_code == 200 and 'candidates' in res_data:
            ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
            clean_json = re.sub(r"```json|```", "", ai_text).strip()
            analysis = json.loads(clean_json)

            # 7. Layer 3: Hybrid Merge
            analysis["entities"]["amounts"] = list(set(analysis["entities"].get("amounts", []) + manual_results["amounts"]))
            analysis["entities"]["dates"] = list(set(analysis["entities"].get("dates", []) + manual_results["dates"]))
            analysis["entities"]["organizations"] = list(set(analysis["entities"].get("organizations", []) + manual_results["organizations"]))

            return {
                "status": "success",
                "processing_time_sec": round(time.time() - start_time, 3),
                **analysis
            }
        
        raise ValueError(f"AI Provider Error: {res_data.get('error', {}).get('message', 'Unknown failure')}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")