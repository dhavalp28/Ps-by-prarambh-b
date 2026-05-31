from datetime import datetime

from db.models.auth_session import AuthSession
from sqlalchemy.orm import Session


def create_auth_session(db: Session, data: dict):
    session = AuthSession(**data)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_auth_session_by_id(db: Session, session_id: int):
    return db.query(AuthSession).filter(AuthSession.id == session_id).first()


def get_auth_session_by_key(db: Session, session_key: str):
    return db.query(AuthSession).filter(AuthSession.session_key == session_key).first()


def update_auth_session(db: Session, auth_session: AuthSession, update_data: dict):
    for key, value in update_data.items():
        setattr(auth_session, key, value)
    db.commit()
    db.refresh(auth_session)
    return auth_session


def revoke_auth_session(db: Session, auth_session: AuthSession):
    setattr(auth_session, "is_active", False)
    setattr(auth_session, "revoked_at", datetime.utcnow())
    db.commit()
    db.refresh(auth_session)
    return auth_session


def revoke_all_user_sessions(db: Session, user_id: int):
    sessions = (
        db.query(AuthSession)
        .filter(AuthSession.user_id == user_id, AuthSession.is_active)
        .all()
    )
    now = datetime.utcnow()
    for session in sessions:
        setattr(session, "is_active", False)
        setattr(session, "revoked_at", now)
    db.commit()
    return sessions


def revoke_all_vendor_sessions(db: Session, vendor_id: int):
    sessions = (
        db.query(AuthSession)
        .filter(AuthSession.vendor_id == vendor_id, AuthSession.is_active)
        .all()
    )
    now = datetime.utcnow()
    for session in sessions:
        setattr(session, "is_active", False)
        setattr(session, "revoked_at", now)
    db.commit()
    return sessions


def get_active_sessions_for_entity(
    db: Session, *, user_id: int | None = None, vendor_id: int | None = None
):
    query = db.query(AuthSession).filter(AuthSession.is_active)
    if user_id is not None:
        query = query.filter(AuthSession.user_id == user_id)
    if vendor_id is not None:
        query = query.filter(AuthSession.vendor_id == vendor_id)
    return query.order_by(AuthSession.created_at.desc()).all()
