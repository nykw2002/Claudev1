# Document Processing Application

A full-stack AI-powered document processing application with a 3-agent pipeline for intelligent PDF analysis.

## Architecture Overview

This application consists of three main services:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│             │      │             │      │             │
│  Frontend   │─────▶│   Backend   │─────▶│ AI Service  │
│  (Next.js)  │      │  (FastAPI)  │      │  (3 Agents) │
│             │◀─────│             │◀─────│             │
└─────────────┘      └─────────────┘      └─────────────┘
    Port 3000           Port 8000            Port 8001
```

### Frontend (Next.js + TypeScript)
- User interface for file upload and prompt input
- Real-time processing status
- Results visualization with metrics
- Responsive design with Tailwind CSS

### Backend (FastAPI)
- File upload handling
- Request orchestration
- Communication with AI service
- RESTful API endpoints

### AI Service (FastAPI + OpenAI)
- **Agent 1**: Raw data processor - extracts and analyzes documents
- **Agent 2**: Summarization agent - condenses information if needed
- **Agent 3**: Evaluation agent - generates final answer with quality metrics

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- OpenAI API key

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (edit .env if needed)
# AI_SERVICE_URL=http://localhost:8001

# Run the server
python -m uvicorn app.main:app --reload --port 8000
```

Backend will be running at: `http://localhost:8000`

### 2. AI Service Setup

```bash
cd ai_service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment - IMPORTANT: Add your OpenAI API key!
# Edit .env and replace with your actual key:
# OPENAI_API_KEY=sk-your-actual-api-key-here

# Run the service
python main.py
```

AI Service will be running at: `http://localhost:8001`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (edit .env.local if needed)
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend will be running at: `http://localhost:3000`

## Usage

1. **Open the application** in your browser: `http://localhost:3000`

2. **Upload PDF files**:
   - Drag and drop PDF files into the upload area, or
   - Click to browse and select files
   - Multiple files are supported

3. **Enter your question**:
   - Type a question about the documents
   - Example: "How many complaints are from Israel?"

4. **Process documents**:
   - Click "Process Documents" button
   - Wait for the AI agents to analyze (typically 10-30 seconds)

5. **View results**:
   - See the final answer
   - Review quality metrics (confidence, accuracy, completeness)
   - Explore document sections that were used
   - Optionally view detailed agent outputs

## JSON Communication Flow

### 1. Frontend → Backend (Upload)
```json
FormData with PDF files
```

**Response:**
```json
{
  "success": true,
  "file_paths": ["uploads/uuid.pdf"],
  "count": 1
}
```

### 2. Frontend → Backend (Process Request)
```json
{
  "file_paths": ["uploads/uuid.pdf"],
  "prompt": "Your question here"
}
```

### 3. Backend → AI Service (Runtime JSON)
```json
{
  "request_id": "uuid",
  "file_paths": ["uploads/uuid.pdf"],
  "prompt": "Your question here",
  "timestamp": "2025-10-20T10:30:00Z"
}
```

### 4. AI Service → Backend → Frontend (Response)
```json
{
  "request_id": "uuid",
  "agent_1_output": "Detailed analysis...",
  "agent_2_output": "Summarized version...",
  "final_answer": "Final evaluated answer...",
  "metrics": {
    "confidence_score": 0.95,
    "accuracy_assessment": "high",
    "completeness": 0.88,
    "sources_used": 3
  },
  "sections_used": [
    {
      "file": "document.pdf",
      "page": 3,
      "text_snippet": "Relevant excerpt..."
    }
  ],
  "processing_time_seconds": 12.5,
  "timestamp": "2025-10-20T10:30:15Z"
}
```

## Project Structure

```
TESTING STUFF2/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── models/            # Pydantic schemas
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── main.py            # FastAPI app
│   ├── uploads/               # Temporary PDF storage
│   ├── requirements.txt
│   └── .env
│
├── ai_service/                 # AI processing service
│   ├── agents/                # 3-agent pipeline
│   │   ├── agent_1_processor.py
│   │   ├── agent_2_summarizer.py
│   │   └── agent_3_evaluator.py
│   ├── services/
│   │   ├── pdf_processor.py   # PDF text extraction
│   │   └── openai_client.py   # OpenAI wrapper
│   ├── models/
│   │   └── schemas.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── page.tsx           # Main page
│   │   └── layout.tsx
│   ├── components/            # React components
│   │   ├── FileUpload.tsx
│   │   ├── PromptInput.tsx
│   │   ├── ProcessingStatus.tsx
│   │   └── ResultsDisplay.tsx
│   ├── services/
│   │   └── api.ts             # API client
│   ├── types/
│   │   └── index.ts           # TypeScript types
│   ├── package.json
│   └── .env.local
│
└── PROJECT_README.md           # This file
```

## API Documentation

### Backend API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### AI Service API
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Technology Stack

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Python-multipart** - File uploads

### AI Service
- **OpenAI GPT-4o** - Language model
- **pdfplumber** - PDF text extraction
- **FastAPI** - Service framework

## Features

- ✅ Multi-file PDF upload with drag-and-drop
- ✅ Real-time processing status indicators
- ✅ 3-agent AI pipeline for quality answers
- ✅ Quality metrics (confidence, accuracy, completeness)
- ✅ Source tracking - shows which PDF sections were used
- ✅ Clean, responsive UI
- ✅ Type-safe TypeScript throughout
- ✅ RESTful API design
- ✅ JSON-based communication between services
- ✅ Error handling and user feedback
- ✅ Temporary file storage with cleanup

## Environment Variables

### Backend (.env)
```env
AI_SERVICE_URL=http://localhost:8001
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=.pdf
```

### AI Service (.env)
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
PORT=8001
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check if port 8000 is available
- Verify all dependencies are installed: `pip install -r requirements.txt`

### AI Service errors
- **OpenAI API Key**: Make sure you've set a valid API key in `ai_service/.env`
- **Port conflict**: Ensure port 8001 is not in use
- **Dependencies**: Run `pip install -r requirements.txt` in ai_service directory

### Frontend issues
- **Dependencies**: Run `npm install` in frontend directory
- **API connection**: Verify backend is running at `http://localhost:8000`
- **Port conflict**: If 3000 is in use, Next.js will suggest another port

### Common Errors

**"AI service is unavailable"**
- Make sure the AI service is running on port 8001
- Check the `AI_SERVICE_URL` in backend/.env

**"File not found" errors**
- Ensure the backend/uploads directory exists
- Check file paths are being stored correctly

**OpenAI API errors**
- Verify API key is valid and has credits
- Check internet connectivity
- Review OpenAI API status page

## Development

### Running in Development Mode

Open 3 terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - AI Service:**
```bash
cd ai_service
venv\Scripts\activate  # Windows
python main.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Testing the Flow

1. Start all three services
2. Open http://localhost:3000
3. Upload a test PDF file
4. Enter a question: "Summarize this document"
5. Click "Process Documents"
6. Observe the console logs in each service
7. Review the results with metrics

## Production Deployment

For production deployment, consider:

1. **Environment variables**: Use secure secret management
2. **File storage**: Use cloud storage (S3, Azure Blob) instead of local uploads
3. **Database**: Add database for request history and analytics
4. **Authentication**: Implement user authentication
5. **Rate limiting**: Add rate limits to prevent abuse
6. **HTTPS**: Use SSL certificates
7. **Scaling**: Deploy services independently with container orchestration

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions:
1. Check the individual service README files
2. Review API documentation at `/docs` endpoints
3. Examine console logs for error messages
4. Verify all environment variables are set correctly

---

**Happy document processing!** 🚀
