from db.base import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class BusinessGallery(Base):
    __tablename__ = "business_gallery"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(
        Integer,
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    business = relationship("Business", back_populates="gallery_images")
