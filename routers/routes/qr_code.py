from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io

from routers.deps import get_db
from repositories.business_repository import get_all_businesses, get_business_by_id
from repositories.business_code_repository import get_business_code_by_business_id
from services import qr_code_service
from utils.response import success_list, error_server, error_not_found

router = APIRouter()


@router.get("/generate-single/{business_id}")
def generate_single_qr_sticker(
    business_id: int,
    format: str = Query("png", pattern="^(png|jpg|jpeg)$"),
    db: Session = Depends(get_db)
):
    """Generate a single QR code sticker for a business"""
    try:
        # Get business
        business = get_business_by_id(db, business_id)
        if not business:
            return error_not_found(title="Generate QR Sticker", resource="Business")
        
        # Get business code
        business_code_obj = get_business_code_by_business_id(db, business_id)
        if not business_code_obj:
            return error_not_found(title="Generate QR Sticker", resource="Business Code")
        
        # Generate sticker
        sticker_buffer = qr_code_service.generate_single_sticker(
            business.business_name,
            business_code_obj.code,
            format
        )
        
        filename = f"{business_code_obj.code}_{business.business_name.replace(' ', '_')}.{format.lower()}"
        
        return StreamingResponse(
            iter([sticker_buffer.getvalue()]),
            media_type=f"image/{format.lower()}",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return error_server(title="Generate QR Sticker", error=str(e))


@router.get("/generate-bulk")
def generate_bulk_qr_stickers(
    business_ids: List[int] = Query(...),
    format: str = Query("png", pattern="^(png|jpg|jpeg)$"),
    db: Session = Depends(get_db)
):
    """Generate QR code stickers for multiple businesses and download as ZIP"""
    try:
        if not business_ids:
            raise HTTPException(status_code=400, detail="No business IDs provided")
        
        businesses_data = []
        
        for business_id in business_ids:
            business = get_business_by_id(db, business_id)
            if not business:
                continue
            
            business_code_obj = get_business_code_by_business_id(db, business_id)
            if not business_code_obj:
                continue
            
            businesses_data.append({
                "business_name": business.business_name,
                "business_code": business_code_obj.code,
            })
        
        if not businesses_data:
            raise HTTPException(status_code=404, detail="No valid businesses found")
        
        # Generate ZIP
        zip_buffer = qr_code_service.generate_sticker_zip(businesses_data, format)
        
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=qr_stickers.zip"}
        )
    except Exception as e:
        return error_server(title="Generate Bulk QR Stickers", error=str(e))


@router.get("/generate-all")
def generate_all_qr_stickers(
    city_id: Optional[int] = None,
    format: str = Query("png", pattern="^(png|jpg|jpeg)$"),
    db: Session = Depends(get_db)
):
    """Generate QR code stickers for all businesses and download as ZIP"""
    try:
        # Get all businesses
        businesses = get_all_businesses(db, city_id=city_id)
        
        if not businesses:
            raise HTTPException(status_code=404, detail="No businesses found")
        
        businesses_data = []
        
        for business in businesses:
            business_code_obj = get_business_code_by_business_id(db, business.id)
            if business_code_obj:
                businesses_data.append({
                    "business_name": business.business_name,
                    "business_code": business_code_obj.code,
                })
        
        if not businesses_data:
            raise HTTPException(status_code=404, detail="No business codes found")
        
        # Generate ZIP
        zip_buffer = qr_code_service.generate_sticker_zip(businesses_data, format)
        
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=qr_stickers_all.zip"}
        )
    except Exception as e:
        return error_server(title="Generate All QR Stickers", error=str(e))
