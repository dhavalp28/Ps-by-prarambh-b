from pydantic import BaseModel, EmailStr
from schemas.auth import DeviceInfoSchema


class VendorLoginSchema(DeviceInfoSchema):
    email: EmailStr
    password: str
