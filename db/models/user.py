from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)

    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)

    referral_code = Column(String, nullable=True)

    hashed_password = Column(String, nullable=False)

    # Relationships
    state = relationship("State")
    city = relationship("City")
