from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.services.file_service import file_service

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files

    Args:
        files: List of PDF files to upload

    Returns:
        dict: Contains list of uploaded file paths and count
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Validate at least one file
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one file is required")

    try:
        # Save all files
        file_paths = await file_service.save_multiple_files(files)

        return {
            "success": True,
            "message": f"Successfully uploaded {len(file_paths)} file(s)",
            "file_paths": file_paths,
            "count": len(file_paths)
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading files: {str(e)}"
        )


@router.delete("/upload/cleanup")
async def cleanup_uploads():
    """
    Clean up all temporary uploaded files

    Returns:
        dict: Success message
    """
    try:
        file_service.cleanup_temp_files()
        return {
            "success": True,
            "message": "Successfully cleaned up temporary files"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during cleanup: {str(e)}"
        )
