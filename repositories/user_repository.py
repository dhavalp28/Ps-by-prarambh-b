from db.models.user import User
from sqlalchemy.orm import Session, joinedload


def get_user_by_phone(db: Session, phone: str):
    return (
        db.query(User)
        .options(joinedload(User.state), joinedload(User.city))
        .filter(User.phone == phone)
        .first()
    )


def get_user_by_email(db: Session, email: str):
    return (
        db.query(User)
        .options(joinedload(User.state), joinedload(User.city))
        .filter(User.email == email)
        .first()
    )


def get_user_by_email_case_insensitive(db: Session, email: str):
    return (
        db.query(User)
        .options(joinedload(User.state), joinedload(User.city))
        .filter(User.email.ilike(email))
        .first()
    )


def get_user_by_id(db: Session, user_id: int):
    return (
        db.query(User)
        .options(joinedload(User.state), joinedload(User.city))
        .filter(User.id == user_id)
        .first()
    )


def get_admin_user_count(db: Session) -> int:
    return db.query(User).filter(User.role.ilike("admin")).count()


def get_all_users(db: Session):
    return db.query(User).options(joinedload(User.state), joinedload(User.city)).all()


def create_user(db: Session, user_data: dict):
    user = User(**user_data)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def update_user(db: Session, user: User, update_data: dict):
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
