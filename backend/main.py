import json # pulls the libraries from the requiremnets.txt   
import os
from io import BytesIO

from dotenv import load_dotenv # .env files actually gets read in my memory
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pypdf import PdfReader

load_dotenv()

app = FastAPI(title="Spec Analyzer API") # this creates the web server 

app.add_middleware(
    CORSMiddleware, # as some of trhe browsers have a security rule that blocks a webpage from callong an api on a different address unless the api explicitly allowes it,  the real company would lock this down to their own domain
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
MODEL = "gemini-2.5-flash"
MAX_CHARS = 60_000  

SYSTEM_PROMPT = """You are a technical document analyst who reviews engineering \
specs, RFPs, and contracts for a construction or engineering firm. Given the raw \
text of a document, extract a structured summary. Respond with ONLY valid JSON, \
no prose, no markdown fences, matching exactly this shape:

{
  "document_title": "string, your best guess at the document's title/subject",
  "summary": "2-3 sentence plain-language summary of what this document is",
  "deadlines": [
    {"label": "string, what the deadline is for", "date_or_timeframe": "string"}
  ],
  "requirements": [
    {"item": "string, the requirement", "category": "string, e.g. Materials, Safety, Scheduling, Compliance"}
  ],
  "risks": [
    {"item": "string, the flagged risk or ambiguity", "severity": "low|medium|high", "reason": "string, why this is a risk"}
  ]
}

If a section has no relevant content, return an empty array for it. Never omit a key."""
def extract_pdf_text(file_bytes: bytes) -> str: # this defines the reusable function
    reader = PdfReader(BytesIO(file_bytes))# raw uploaded files that returns as a str
    if reader.is_encrypted:
        raise HTTPException(400, "This PDF is password-protected. Please upload an unlocked file.")
    text_parts = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(text_parts).strip()
    if not text:
        raise HTTPException(
            400,
            "Couldn't extract any text from this PDF. It may be a scanned image "
            "without an OCR text layer.",
        )
    return text[:MAX_CHARS]
@app.get("/health") # if someone  comes with the get request i will just simply say that run the function that is below.
def health():
    return {"status": "ok"}


@app.post("/analyze") 
async def analyze(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Please upload a PDF file.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            500,
            "Server is missing GEMINI_API_KEY. Set it in your .env file or "
            "deployment environment variables.",
        )

    file_bytes = await file.read()
    document_text = extract_pdf_text(file_bytes)

    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=document_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                max_output_tokens=2000,
            ),
        )
    except Exception as exc:
        raise HTTPException(502, f"Error calling the analysis model: {exc}")

    raw_text = response.text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        raise HTTPException(502, "The model returned a response that couldn't be parsed as JSON.")

    return parsed
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)