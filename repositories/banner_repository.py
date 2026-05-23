from sqlalchemy.orm import Session

from db.models.banner import Banner


def get_all_banners(db: Session):
    return db.query(Banner).order_by(Banner.sort_order.asc(), Banner.id.asc()).all()


def get_banner_by_id(db: Session, banner_id: int):
    return db.query(Banner).filter(Banner.id == banner_id).first()


def get_banner_by_title(db: Session, title: str):
    return db.query(Banner).filter(Banner.title == title).first()


def create_banner(db: Session, banner_data: dict):
    banner = Banner(**banner_data)

    db.add(banner)
    db.commit()
    db.refresh(banner)

    return banner


def update_banner(db: Session, banner: Banner, update_data: dict):
    for key, value in update_data.items():
        setattr(banner, key, value)

    db.commit()
    db.refresh(banner)

    return banner


def delete_banner(db: Session, banner: Banner):
    db.delete(banner)
    db.commit()
