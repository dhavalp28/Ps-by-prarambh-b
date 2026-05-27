from sqlalchemy.orm import Session
from datetime import datetime
from db.models.otp_session import OtpSession


def create_otp_session(db: Session, phone: str, otp: str, purpose: str, expires_at: datetime, temp_user_data: str = None):
    """Create a new OTP session"""
    otp_session = OtpSession(
        phone=phone,
        otp=otp,
        purpose=purpose,
        expires_at=expires_at,
        temp_user_data=temp_user_data,
        attempts=0
    )
    db.add(otp_session)
    db.commit()
    db.refresh(otp_session)
    return otp_session


def get_otp_session_by_phone(db: Session, phone: str, purpose: str):
    """Get the latest OTP session for a phone number"""
    return db.query(OtpSession).filter(
        OtpSession.phone == phone,
        OtpSession.purpose == purpose,
        OtpSession.is_verified == False
    ).order_by(OtpSession.created_at.desc()).first()


def update_otp_session(db: Session, otp_session_id: int, **kwargs):
    """Update an OTP session"""
    otp_session = db.query(OtpSession).filter(OtpSession.id == otp_session_id).first()
    if otp_session:
        for key, value in kwargs.items():
            setattr(otp_session, key, value)
        db.commit()
        db.refresh(otp_session)
    return otp_session


def increment_attempts(db: Session, otp_session_id: int):
    """Increment OTP verification attempts"""
    otp_session = db.query(OtpSession).filter(OtpSession.id == otp_session_id).first()
    if otp_session:
        otp_session.attempts += 1
        db.commit()
        db.refresh(otp_session)
    return otp_session


def delete_otp_session(db: Session, otp_session_id: int):
    """Delete an OTP session"""
    otp_session = db.query(OtpSession).filter(OtpSession.id == otp_session_id).first()
    if otp_session:
        db.delete(otp_session)
        db.commit()
    return otp_session


def get_otp_session_by_id(db: Session, otp_session_id: int):
    """Get OTP session by ID"""
    return db.query(OtpSession).filter(OtpSession.id == otp_session_id).first()
