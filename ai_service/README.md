# AI Document Processing Service

AI service with a 3-agent pipeline for intelligent document analysis using OpenAI's GPT models.

## Architecture

### 3-Agent Pipeline

1. **Agent 1 - Raw Data Processor**
   - Extracts and processes raw document content
   - Generates initial comprehensive answer to user prompt
   - Uses low temperature for focused, accurate responses

2. **Agent 2 - Summarization Agent**
   - Evaluates if Agent 1's answer needs summarization
   - Provides concise version while retaining key information
   - Returns original if already clear and concise

3. **Agent 3 - Evaluation Agent**
   - Compares outputs from Agent 1 and Agent 2
   - Determines the best final answer
   - Generates quality metrics (confidence, accuracy, completeness)
   - Identifies document sections used in the answer

## Setup

### 1. Create Virtual Environment

```bash
cd ai_service
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Edit `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key
OPENAI_MODEL=gpt-4o
PORT=8001
```

### 4. Run the Service

```bash
# From ai_service directory
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8001
```

The service will be available at `http://localhost:8001`

## API Endpoints

### Process Documents
```http
POST /api/process
Content-Type: application/json

{
  "request_id": "uuid",
  "file_paths": ["../backend/uploads/file1.pdf"],
  "prompt": "How many complaints are from Israel?",
  "timestamp": "2025-10-20T10:30:00Z"
}
```

**Response:**
```json
{
  "request_id": "uuid",
  "agent_1_output": "Based on the documents, there are 15 complaints...",
  "agent_2_output": "15 complaints from Israel.",
  "final_answer": "There are 15 complaints from Israel.",
  "metrics": {
    "confidence_score": 0.95,
    "accuracy_assessment": "high",
    "completeness": 0.88,
    "sources_used": 3
  },
  "sections_used": [
    {
      "file": "file1.pdf",
      "page": 3,
      "text_snippet": "Israel: 15 complaints recorded..."
    }
  ],
  "processing_time_seconds": 12.5,
  "timestamp": "2025-10-20T10:30:15Z"
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Document Processing",
  "openai_configured": true
}
```

## Project Structure

```
ai_service/
├── agents/
│   ├── agent_1_processor.py    # Raw data processing
│   ├── agent_2_summarizer.py   # Summarization logic
│   └── agent_3_evaluator.py    # Evaluation & metrics
├── services/
│   ├── pdf_processor.py        # PDF text extraction
│   └── openai_client.py        # OpenAI API wrapper
├── models/
│   └── schemas.py              # Pydantic models
├── main.py                     # FastAPI app
├── requirements.txt
├── .env
└── README.md
```

## Features

- **PDF Processing**: Extract text from PDFs using pdfplumber
- **Multi-Agent Pipeline**: Three specialized agents for quality answers
- **Quality Metrics**: Confidence, accuracy, and completeness scores
- **Source Tracking**: Identifies which PDF sections were used
- **OpenAI Integration**: Uses GPT-4o for intelligent processing
- **Error Handling**: Robust error handling and fallbacks

## Development

### Testing with cURL

```bash
curl -X POST "http://localhost:8001/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-123",
    "file_paths": ["../backend/uploads/document.pdf"],
    "prompt": "Summarize the main points",
    "timestamp": "2025-10-20T10:00:00Z"
  }'
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Agent Details

### Agent 1: Raw Data Processor
- **Purpose**: Generate comprehensive initial answer
- **Temperature**: 0.3 (focused)
- **Output**: Detailed response with all relevant information

### Agent 2: Summarization Agent
- **Purpose**: Condense information if needed
- **Temperature**: 0.5 (balanced)
- **Logic**: Evaluates verbosity and summarizes accordingly

### Agent 3: Evaluation Agent
- **Purpose**: Final answer quality control
- **Temperature**: 0.3 (precise)
- **Metrics Generated**:
  - `confidence_score`: How confident the AI is in the answer (0-1)
  - `accuracy_assessment`: Categorical assessment (high/medium/low)
  - `completeness`: How complete the answer is (0-1)
  - `sources_used`: Number of document sources referenced

## Notes

- Ensure OpenAI API key is properly configured
- PDF files must be accessible at the provided file paths
- Processing time depends on document size and complexity
- The service uses streaming for large documents
- Metrics are AI-generated evaluations, not ground truth

## Troubleshooting

**OpenAI API Errors:**
- Verify API key is valid
- Check API quota and billing
- Ensure internet connectivity

**PDF Processing Errors:**
- Verify file paths are correct and accessible
- Ensure PDFs are not corrupted or password-protected
- Check file permissions

**Timeout Issues:**
- Large documents may take longer to process
- Consider increasing timeout in backend's ai_client.py
- Monitor OpenAI API response times
