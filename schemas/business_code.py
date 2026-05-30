from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BusinessCodeCreate(BaseModel):
    business_id: int


class BusinessCodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BusinessCodeValidateRequest(BaseModel):
    code: str
    coupon_id: Optional[int] = None


class BusinessCodeValidateResponse(BaseModel):
    valid: bool
    business_id: Optional[int] = None
    business_name: Optional[str] = None
    message: str
