from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BusinessReviewUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str


class BusinessReviewUpsert(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: Optional[str] = None
    is_active: bool = True

    @field_validator("review")
    @classmethod
    def validate_review(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class BusinessReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    user_id: int
    rating: int
    review: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user: BusinessReviewUserSummary


class BusinessRatingSummaryResponse(BaseModel):
    average_rating: float
    total_reviews: int
