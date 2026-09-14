# Specsense

Built this to learn how to connect a real AI API to a full-stack app, using a
problem I thought was actually useful: engineering specs, RFPs, and contracts
are long and easy to miss things in. Specsense reads a PDF and pulls out the
deadlines, requirements, and risks worth flagging, so you don't have to read
all 40 pages to find the one clause that matters.

## What it does

Upload a spec/RFP/contract PDF → it extracts the text → sends it to Gemini
with a prompt asking for a structured breakdown → shows you:
- **Deadlines** — what's due and when
- **Requirements** — categorized (Materials, Safety, Compliance, etc.)
- **Risks** — flagged issues with a severity rating and why they matter

## Tech stack


| Backend : Python, FastAPI |
| AI :  Google Gemini API (`google-genai`) |
| PDF parsing : `pypdf` |
| Frontend : Plain HTML/CSS/JavaScript (no framework, no build step) |

The backend is written so the AI provider is isolated to one function —
swapping to a different model/provider later means changing that one
function, not the frontend.

## Running it locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
# create a .env file with: GEMINI_API_KEY=your_key_here
python -m uvicorn main:app --reload --port 8000
```

**Frontend**

Just open `frontend/index.html` in a browser. It's a single static file —
no build step, no npm install. Make sure the "Backend API URL" field on the
page points to `http://localhost:8000` (that's the default).

## What I learned building this

- How a frontend, backend, and third-party API actually talk to each other
  over HTTP (and why the API key has to live on the backend, never the
  frontend)
- Prompt design for getting reliable structured JSON out of an LLM instead
  of free-form text
- Basic error handling for things that fail outside your control (a slow
  API, a bad file, a network hiccup)
- Git basics — `.gitignore`, staging, committing, pushing, and specifically
  *why* secrets should never end up in version control

## Known limitations / what I'd add next

- Only works on PDFs with real text (not scanned images without OCR)
- No authentication or rate-limiting — fine for a demo, not production
- Long documents get truncated to keep costs/latency down; chunking longer
  docs would be the next real improvement
