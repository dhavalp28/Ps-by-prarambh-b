from sqlalchemy.orm import Session

from db.models.vendor import Vendor


def get_all_vendors(db: Session):
    return db.query(Vendor).order_by(Vendor.created_at.desc()).all()


def get_vendor_by_id(db: Session, vendor_id: int):
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()


def get_vendor_by_email(db: Session, email: str):
    return db.query(Vendor).filter(Vendor.email == email).first()


def get_vendor_by_phone(db: Session, phone: str):
    return db.query(Vendor).filter(Vendor.phone == phone).first()


def create_vendor(db: Session, vendor_data: dict):
    vendor = Vendor(**vendor_data)

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return vendor


def update_vendor(db: Session, vendor: Vendor, update_data: dict):
    for key, value in update_data.items():
        setattr(vendor, key, value)

    db.commit()
    db.refresh(vendor)

    return vendor


def delete_vendor(db: Session, vendor: Vendor):
    db.delete(vendor)
    db.commit()
