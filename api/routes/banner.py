from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from api.deps import get_db
from schemas.banner import BannerResponse
from services import banner_service

router = APIRouter()


@router.get("/", response_model=List[BannerResponse])
def list_banners(db: Session = Depends(get_db)):
    return banner_service.get_all_banners(db)


@router.get("/{banner_id}", response_model=BannerResponse)
def get_banner(banner_id: int, db: Session = Depends(get_db)):
    return banner_service.get_banner(db, banner_id)


@router.post("/", response_model=BannerResponse, status_code=status.HTTP_201_CREATED)
async def create_banner(
    title: str = Form(...),
    subtitle: Optional[str] = Form(None),
    redirect_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    sort_order: int = Form(0),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await banner_service.create_banner(
        db=db,
        title=title,
        subtitle=subtitle,
        redirect_url=redirect_url,
        description=description,
        sort_order=sort_order,
        image=image,
    )


@router.put("/{banner_id}", response_model=BannerResponse)
async def update_banner(
    banner_id: int,
    title: Optional[str] = Form(None),
    subtitle: Optional[str] = Form(None),
    redirect_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    return await banner_service.update_banner(
        db=db,
        banner_id=banner_id,
        title=title,
        subtitle=subtitle,
        redirect_url=redirect_url,
        description=description,
        sort_order=sort_order,
        is_active=is_active,
        image=image,
    )


@router.delete("/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_banner(banner_id: int, db: Session = Depends(get_db)):
    banner_service.delete_banner(db, banner_id)
