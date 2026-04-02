🚀 High-Precision Document Extraction API

⚡ Designed for high accuracy, low hallucination, and production-ready performance.

A professional-grade FastAPI backend for extracting structured information from unstructured documents (PDF, DOCX, Images).
This system uses a Hybrid NLP Pipeline combining deterministic logic and AI models to ensure reliable and accurate results.

---

💡 System Architecture & Approach

Traditional LLM-based systems often hallucinate or miss structured data in complex documents.
This project solves that using a layered hybrid approach:

🔹 Deterministic Layer (Regex)

- Extracts currency, percentages, and patterns with high precision
- Ensures no loss of critical numerical data

🔹 Probabilistic Layer (LLM - Gemini 1.5 Flash)

- Generates concise summaries (2 lines)
- Performs context-aware sentiment analysis

🔹 Sanitization Layer

- Cleans OCR/PDF noise
- Removes artifacts (extra symbols, formatting issues)

🔹 Self-Healing Model Discovery

- Dynamically selects available Gemini models
- Prevents API failures due to version changes

---

🛠️ Tech Stack

- Language: Python 3.10+
- Framework: FastAPI (Async)
- AI Engine: Google Gemini 1.5 Flash
- OCR & Parsing:
  - Tesseract OCR (Images)
  - PyPDF (PDFs)
  - python-docx (DOCX)
- Deployment: Render / Railway

---

⚠️ Prerequisites

- Python 3.10+
- Tesseract OCR Engine (must be installed on your system)
  👉 https://github.com/tesseract-ocr/tesseract

---

✨ Features

- 📄 Multi-format support (PDF, DOCX, Images)
- 🔍 OCR-based text extraction
- 🧠 AI-powered summarization
- 🏷️ Named Entity Extraction (Regex + NLP)
- 😊 Sentiment Analysis (Positive / Neutral / Negative)
- 🧾 Document Type Detection
- 📊 Confidence Scores
- ⏱️ Processing Time Tracking
- 🔐 API Key Authentication

---

📁 Repository Structure

document-extraction-api/
├── src/
│   ├── main.py          # API routes & core logic
│   └── utils.py         # OCR + text cleaning
├── build.sh             # Render build script (installs system dependencies like Tesseract)
├── render.yaml          # Render deployment configuration (infrastructure as code)
├── .env                 # Environment variables (excluded from Git)
├── requirements.txt     # Python dependencies
└── test_api.py          # Local testing script

---

🚀 Setup & Installation

1️⃣ Create Virtual Environment

python -m venv venv
.\venv\Scripts\Activate.ps1

2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Configuration

Create a ".env" file in the root directory:

GEMINI_API_KEY=your_api_key_here
TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe
SECRET_API_KEY=sk_track2_987654321

---

▶️ Running the Server

python -m uvicorn src.main:app --reload

---

📡 API Usage

Endpoint

POST https://document-extraction-api-39s3.onrender.com/api/document-analyze

Headers

x-api-key: YOUR_SECRET_API_KEY
Content-Type: application/json

Example Request (cURL)

curl -X POST https://document-extraction-api-39s3.onrender.com/api/document-analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_track2_987654321" \
  -d '{
    "fileName": "sample.pdf",
    "fileType": "pdf",
    "fileBase64": "BASE64_STRING"
  }'

---

📊 Sample Response

{
  "status": "success",
  "document_type": "Security Report",
  "processing_time_sec": 5.29,
  "confidence": {
    "summary": 0.95,
    "entities": 0.92,
    "sentiment": 0.94
  },
  "summary": "A major cybersecurity breach exposed sensitive customer data across multiple financial institutions.",
  "entities": {
    "names": [],
    "organizations": [],
    "dates": [],
    "amounts": []
  },
  "sentiment": "Negative"
}

---

📘 API Documentation

Interactive Swagger UI:

https://document-extraction-api-39s3.onrender.com/docs

---

❤️ Health Check

GET https://document-extraction-api-39s3.onrender.com/

Response:

{
  "status": "API running"
}

---

🌐 Live Deployment

- API Endpoint: https://document-extraction-api-39s3.onrender.com/api/document-analyze
- Interactive Swagger Docs: https://document-extraction-api-39s3.onrender.com/docs
- Health Check: https://document-extraction-api-39s3.onrender.com/

⚡ Note: This API is hosted on a Render Free Instance. If inactive, allow up to 60 seconds for the first request.

---

🤖 AI Tools Used

- Google Gemini 1.5 Flash → Primary model for summarization and sentiment analysis
- Gemini (LLM Assistance) → Used for debugging, infrastructure setup (Render), and system optimization

---

⚠️ Known Limitations

- Cold Start Delay
  Due to Render Free Tier, the first request may take up to 60 seconds

- OCR Accuracy
  Handwritten or low-quality images may produce less accurate results due to Tesseract limitations

---

🧠 Why Hybrid AI?

LLMs alone may:

- Hallucinate data
- Miss structured patterns

This system combines:

- ✅ Regex (precision)
- ✅ AI (context understanding)

👉 Result: High accuracy + reliability

---

📌 Note

This project is actively maintained and optimized for performance and accuracy.