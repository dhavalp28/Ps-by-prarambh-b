from pydantic import BaseModel, EmailStr
from schemas.auth import DeviceInfoSchema


class AdminLoginSchema(DeviceInfoSchema):
    email: str
    password: str


class AdminBootstrapSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    state_id: int | None = None
    city_id: int | None = None
