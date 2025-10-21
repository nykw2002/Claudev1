import os
import shutil
from pathlib import Path
from typing import List
from fastapi import UploadFile, HTTPException
import uuid
from app.utils.config import settings


class FileService:
    """Service for handling file uploads and storage"""

    def __init__(self):
        # Ensure upload directory is relative to the current working directory
        self.upload_dir = Path(settings.UPLOAD_DIR)
        if not self.upload_dir.is_absolute():
            self.upload_dir = Path.cwd() / self.upload_dir

        # Create directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        print(f"Upload directory: {self.upload_dir}")

    async def save_upload_file(self, upload_file: UploadFile) -> str:
        """
        Save an uploaded file to the uploads directory

        Args:
            upload_file: FastAPI UploadFile object

        Returns:
            str: Relative path to the saved file

        Raises:
            HTTPException: If file validation fails
        """
        try:
            # Validate file extension
            file_ext = Path(upload_file.filename).suffix.lower()
            print(f"Validating file: {upload_file.filename}, extension: {file_ext}")

            if file_ext not in settings.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
                )

            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = self.upload_dir / unique_filename
            print(f"Saving file to: {file_path}")

            # Save file
            try:
                with file_path.open("wb") as buffer:
                    shutil.copyfileobj(upload_file.file, buffer)
                print(f"File saved successfully: {file_path}")
            except Exception as e:
                print(f"Error writing file: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to save file: {str(e)}"
                )
            finally:
                upload_file.file.close()

            # Return path as string (relative to backend dir or just uploads/filename)
            result_path = f"{settings.UPLOAD_DIR}/{unique_filename}"
            print(f"Returning path: {result_path}")
            return result_path

        except HTTPException:
            raise
        except Exception as e:
            print(f"Unexpected error in save_upload_file: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )

    async def save_multiple_files(self, files: List[UploadFile]) -> List[str]:
        """
        Save multiple uploaded files

        Args:
            files: List of FastAPI UploadFile objects

        Returns:
            List[str]: List of relative paths to saved files
        """
        file_paths = []
        for file in files:
            file_path = await self.save_upload_file(file)
            file_paths.append(file_path)
        return file_paths

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage

        Args:
            file_path: Path to the file (e.g., "uploads/filename.pdf")

        Returns:
            bool: True if deleted successfully
        """
        try:
            # Handle both absolute and relative paths
            full_path = Path(file_path)
            if not full_path.is_absolute():
                # If relative, assume it's relative to the current directory
                full_path = Path.cwd() / file_path

            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")
            return False

    def delete_multiple_files(self, file_paths: List[str]) -> None:
        """Delete multiple files"""
        for file_path in file_paths:
            self.delete_file(file_path)

    def cleanup_temp_files(self) -> None:
        """Clean up all files in the upload directory"""
        try:
            for file in self.upload_dir.iterdir():
                if file.is_file():
                    file.unlink()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")


# Singleton instance
file_service = FileService()
