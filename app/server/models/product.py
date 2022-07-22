from typing import Optional
from pydantic import BaseModel, EmailStr, Field



class ProductSchema(BaseModel):
    id : int = Field(unique=True)
    name: str = Field(...)
    description: Optional [str] 
    price: float = Field(...)

    class Config:

        schema_extra = {
            "example": {
                "name": "Apache",
                "description": "This is a fast motorcycle",
                "price": "73000000",
            }
        }

    

class UpdateProductModel(BaseModel):
    name: Optional[str]
    description: Optional[str]
    year: Optional[int]
    price: Optional[float]

    class Config:
        schema_extra = {
            "example": {
                "name": "Apache",
                "description": "This is a fast motorcycle",
                "price": "73000000",
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