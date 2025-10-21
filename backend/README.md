# Document Processing Backend

FastAPI backend service for handling PDF document uploads and processing with AI.

## Features

- PDF file upload with validation
- Communication with AI service via JSON
- Temporary file storage management
- CORS support for frontend integration
- Health check endpoints

## Setup

### 1. Create Virtual Environment

```bash
cd backend
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

Edit `.env` file:

```env
AI_SERVICE_URL=http://localhost:8001
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=.pdf
```

### 4. Run the Server

```bash
# From backend directory
python -m uvicorn app.main:app --reload --port 8000

# Or using the main.py script
python app/main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Upload Files
```http
POST /api/upload
Content-Type: multipart/form-data

files: [file1.pdf, file2.pdf]
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully uploaded 2 file(s)",
  "file_paths": ["uploads/uuid1.pdf", "uploads/uuid2.pdf"],
  "count": 2
}
```

### Process Documents
```http
POST /api/process
Content-Type: application/json

{
  "request_id": "uuid",
  "file_paths": ["uploads/uuid1.pdf"],
  "prompt": "How many complaints are from Israel?",
  "timestamp": "2025-10-20T10:30:00Z"
}
```

**Response:**
```json
{
  "request_id": "uuid",
  "agent_1_output": "Raw answer...",
  "agent_2_output": "Summarized answer...",
  "final_answer": "Final evaluated answer...",
  "metrics": {
    "confidence_score": 0.95,
    "accuracy_assessment": "high",
    "completeness": 0.88,
    "sources_used": 3
  },
  "sections_used": [...],
  "processing_time_seconds": 12.5,
  "timestamp": "2025-10-20T10:30:15Z"
}
```

### Health Check
```http
GET /api/health
```

### Cleanup Uploads
```http
DELETE /api/upload/cleanup
```

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── models/          # Pydantic models
│   │   ├── config.py    # RuntimeJSON, ConfigJSON
│   │   └── response.py  # AIResponse, Metrics
│   ├── routes/          # API endpoints
│   │   ├── upload.py    # File upload routes
│   │   └── process.py   # Processing routes
│   ├── services/        # Business logic
│   │   ├── file_service.py   # File handling
│   │   └── ai_client.py      # AI service communication
│   ├── utils/
│   │   └── config.py    # Configuration settings
│   └── main.py          # FastAPI app
├── uploads/             # Temporary file storage
├── requirements.txt
├── .env
└── README.md
```

## Development

### Testing with cURL

**Upload files:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

**Process documents:**
```bash
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["uploads/uuid.pdf"],
    "prompt": "Your question here"
  }'
```

## Notes

- Files are stored temporarily in the `uploads/` directory
- File cleanup can be automated or manual via `/api/upload/cleanup`
- AI service must be running at the configured URL
- CORS is configured for `localhost:3000` and `localhost:3001`
