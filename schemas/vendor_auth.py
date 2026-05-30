from pydantic import BaseModel, EmailStr


class VendorLoginSchema(BaseModel):
    email: EmailStr
    password: str
