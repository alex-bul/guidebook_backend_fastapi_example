import os
import base64
import uuid

from sqlalchemy.orm import Session
from db.methods import get_image, create_image
from db.database import get_db

from core.dependencies import verify_token
from schemas.image import Image, CreateImage, ImageInfo

from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(prefix='/images', tags=['Фото'])
storage_path = 'images'

if storage_path not in os.listdir():
    os.mkdir(storage_path)

from pydantic import BaseModel


class Data(BaseModel):
    img: str


@router.post("/upload", dependencies=[Depends(verify_token)], response_model=ImageInfo, description="Upload image by base64")
async def upload_image(data: Data, db: Session = Depends(get_db)) -> ImageInfo:
    img = data.img

    filename = f'{uuid.uuid4()}.jpg'
    filepath = os.path.join(storage_path, filename)
    encoded_data = img.split(';base64,')[-1].replace(' ', '+')
    try:
        decoded_data = base64.b64decode((encoded_data))
        with open(filepath, "wb") as f:
            f.write(decoded_data)
        return create_image(db, CreateImage(name=filename))
    except Exception:
        raise HTTPException(400, "Не удалось сохранить фото")


@router.get("/{image_id}")
async def get_image_by_id(image_id: int, db: Session = Depends(get_db)):
    image = get_image(db, image_id)
    file_path = './' + os.path.join(storage_path, image.name)

    if not image or not os.path.exists(file_path):
        raise HTTPException(404, "Фото не найдено")

    return FileResponse(file_path)
