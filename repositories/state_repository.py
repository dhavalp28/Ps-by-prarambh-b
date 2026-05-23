from sqlalchemy.orm import Session

from app.db.models.state import State


def get_all_states(db: Session):
    return db.query(State).all()


def get_state_by_id(db: Session, state_id: int):
    return db.query(State).filter(State.id == state_id).first()


def get_state_by_name(db: Session, name: str):
    return db.query(State).filter(State.name == name).first()


def create_state(db: Session, state_data: dict):
    state = State(**state_data)

    db.add(state)
    db.commit()
    db.refresh(state)

    return state


def update_state(db: Session, state: State, update_data: dict):
    for key, value in update_data.items():
        setattr(state, key, value)

    db.commit()
    db.refresh(state)

    return state


def delete_state(db: Session, state: State):
    db.delete(state)
    db.commit()
