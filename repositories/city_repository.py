from sqlalchemy.orm import Session, joinedload

from db.models.city import City


def get_all_cities(db: Session):
    return db.query(City).options(joinedload(City.state)).all()


def get_cities_by_state(db: Session, state_id: int):
    return db.query(City).options(joinedload(City.state)).filter(City.state_id == state_id).all()


def get_city_by_id(db: Session, city_id: int):
    return db.query(City).options(joinedload(City.state)).filter(City.id == city_id).first()


def get_city_by_name_and_state(db: Session, name: str, state_id: int):
    return db.query(City).filter(City.name == name, City.state_id == state_id).first()


def create_city(db: Session, city_data: dict):
    city = City(**city_data)

    db.add(city)
    db.commit()
    db.refresh(city)

    return city


def update_city(db: Session, city: City, update_data: dict):
    for key, value in update_data.items():
        setattr(city, key, value)

    db.commit()
    db.refresh(city)

    return city


def delete_city(db: Session, city: City):
    db.delete(city)
    db.commit()
