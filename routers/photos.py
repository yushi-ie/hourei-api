from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel

from schemas.auth import User
from services.auth import get_current_active_user
from services.storage import StorageService

router = APIRouter()
storage_service = StorageService()

class PhotoResponse(BaseModel):
    filename: str
    message: str

@router.post("/photos/upload", response_model=PhotoResponse)
async def upload_photo(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    # Use user username in filename to avoid collisions or organize
    file_name = f"{current_user.username}/{file.filename}"
    uploaded_filename = storage_service.upload_file(file, file_name)
    return PhotoResponse(filename=uploaded_filename, message="Photo uploaded successfully")
