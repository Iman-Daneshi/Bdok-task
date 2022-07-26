

from typing import Optional
from pydantic import BaseModel, EmailStr, Field



class UserSchema(BaseModel):
    username: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(max_length=128)
    national_id: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "Imdan",
                "first_name": "Iman",
                "last_name": "Daneshi",
                "email": "iman@mail.com",
                "password": "123456",
                "national_id": "0020022381"
            }
        }


class UpdateUserModel(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    national_id: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "username": "Imdan",
                "first_name": "Iman",
                "last_name": "Daneshi",
                "email": "iman@mail.com",
                "password": "123456",
                "national_id": "0020022381"
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}