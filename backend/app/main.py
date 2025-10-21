from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, process
from app.utils.config import settings

# Create FastAPI application
app = FastAPI(
    title="Document Processing API",
    description="Backend API for PDF document processing with AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(process.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Document Processing API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
