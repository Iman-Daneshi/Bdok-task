
from dataclasses import field
from datetime import datetime
from .product import ProductSchema
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class Status(str, Enum):
    received = "received"
    processing = "processing"
    delivered = "delivered"
class Count():
    count: int


class BasketSchema(BaseModel):
    items: List[ProductSchema]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status : Status
    
    
    class Config:
        schema_extra = {
            "example": {
                "items": ["apache"],
                "created_at": "2017-06-01 12:22",
                "updated_at": "2017-06-05 12:22",
                "status": "processing",
            }
        }


class UpdateBasketModel(BaseModel):
    count: Optional[int]
    items: Optional[List]
    created_at : Optional[datetime]
    updated_at : Optional[datetime]
    status : Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "items": ["apache"],
                "created_at": "2017-06-01 12:22",
                "updated_at": "2017-06-05 12:22",
                "status": "processing",
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