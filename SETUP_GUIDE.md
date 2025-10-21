# Document Processing Application - Setup Guide

AI-powered document processing with dynamic elements, advanced evaluation metrics, and OCR support.

## Features

- **Dynamic Elements**: Configure reusable document processing templates
- **3-Agent AI Pipeline**: Processor → Summarizer → Evaluator
- **Advanced Evaluation Framework**:
  - Groundedness (claims supported by documents)
  - Accuracy (factual correctness)
  - Relevance (query alignment)
  - Individual detailed justifications for each metric
- **OCR Support**: Automatic detection and processing of scanned PDFs
- **Pattern Matching**: Intelligent extraction for counting queries
- **Quality Threshold**: Automatic 80% quality review flag

## Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **OpenAI API Key** (get from https://platform.openai.com/api-keys)

## Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/nykw2002/gpt5-2.git
cd gpt5-2
```

### Step 2: Install Python Dependencies

#### Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### AI Service
```bash
cd ai_service
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Configure OpenAI API Key

⚠️ **REQUIRED**: Create `ai_service/.env` file:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Step 4: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 5: Start All Services

Run these in **3 separate terminals**:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - AI Service:**
```bash
cd ai_service
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
python -m uvicorn main:app --reload --port 8001
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 6: Access the Application

Open your browser:
```
http://localhost:3000
# or http://localhost:3001 if 3000 is in use
```

## Architecture

### Services

- **Frontend (Next.js 14)**: http://localhost:3000
  - Dynamic element configuration
  - Real-time processing UI
  - Metrics visualization
  - Saved outputs management

- **Backend (FastAPI)**: http://localhost:8000
  - File upload handling
  - API routing
  - Request validation

- **AI Service (FastAPI)**: http://localhost:8001
  - 3-agent processing pipeline
  - OCR detection and processing
  - Pattern matching extraction
  - Advanced evaluation metrics

### 3-Agent Pipeline

1. **Agent 1 (Processor)**: Extracts and analyzes document content
2. **Agent 2 (Summarizer)**: Creates concise, focused answers
3. **Agent 3 (Evaluator)**:
   - Runs 4 separate evaluations
   - Evaluates groundedness against source documents
   - Fact-checks for accuracy
   - Assesses relevance to query
   - Provides detailed justifications

## Usage Guide

### Creating Dynamic Elements

1. Go to "Elements" page
2. Click "Create New Element"
3. Configure:
   - Name & Description
   - File type (PDF)
   - Prompt template
   - Additional context (optional)
4. Save element

### Running Elements

1. Select an element from dashboard
2. Upload PDF file(s)
3. Click "Process"
4. Review results:
   - Final answer
   - Quality metrics (Groundedness, Accuracy, Relevance)
   - Individual justifications
   - Agent outputs
   - Document sections used

### Saving Outputs

1. After processing, click "Save Output"
2. Output is linked to the element
3. View saved outputs in "Outputs" page

## Evaluation Metrics Explained

### Groundedness (0-100%)
**Question**: Are claims supported by document sources?
- **100%**: All claims directly from documents
- **80%**: Most claims supported, minor inferences
- **<80%**: Significant unsupported claims (needs review)

**Justification includes**: Specific document quotes, claim verification

### Accuracy (0-100%)
**Question**: Are the facts correct?
- **100%**: No errors
- **80%**: Minor inaccuracies
- **<80%**: Factual errors present (needs review)

**Justification includes**: Error identification, fact cross-checking

### Relevance (0-100%)
**Question**: Does it answer the user's question?
- **100%**: Directly answers question
- **80%**: Mostly relevant
- **<80%**: Tangential or off-topic (needs review)

**Justification includes**: Question alignment analysis

### Overall Quality Score
- **Average** of Groundedness, Accuracy, Relevance
- **<80% = Needs Review** (red warning banner)

## OCR Support

The system automatically detects scanned PDFs:
- Checks first page for extractable text
- If <10 characters found, uses OCR (PyMuPDF)
- Otherwise uses standard extraction (pdfplumber)
- Seamless user experience

## API Documentation

- **Backend**: http://localhost:8000/docs
- **AI Service**: http://localhost:8001/docs

## Troubleshooting

### Module not found
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Reinstall
pip install -r requirements.txt
```

### OpenAI API errors
- Verify API key in `ai_service/.env`
- Check account credits
- Ensure internet connection

### Port already in use
```bash
# Check what's using the port
# Windows
netstat -ano | findstr :8000

# Kill the process or use different port
python -m uvicorn app.main:app --reload --port 8002
```

### Frontend can't connect
- Verify backend running: http://localhost:8000/docs
- Check `frontend/.env.local` for `NEXT_PUBLIC_API_URL`

### Low quality scores
- Review the individual justifications
- Check if document contains needed information
- Refine your prompt for clarity
- Add additional context if needed

## Development Tips

- Monitor all 3 terminal windows for logs
- Use F12 browser console for frontend debugging
- Agent 3 debug logs show detailed evaluation steps
- API docs (`/docs`) allow direct endpoint testing

## File Storage

- **Uploads**: `backend/uploads/` (temporary PDF storage)
- **Dynamic Elements**: Browser localStorage
- **Saved Outputs**: Browser localStorage

## Next Steps

1. Create your first dynamic element
2. Test with sample PDFs
3. Review evaluation metrics
4. Explore agent outputs for transparency
5. Save high-quality results

## Support

For issues or questions:
- Check terminal logs for errors
- Review API documentation
- Examine browser console (F12)

Enjoy AI-powered document processing! 🚀
