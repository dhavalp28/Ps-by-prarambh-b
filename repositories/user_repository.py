from sqlalchemy.orm import Session

from db.models.user import User


def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(User).all()


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
