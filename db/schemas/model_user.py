from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

class UserForm(BaseModel):
    name: str
    email: str
    password: str

class UserDB(BaseModel):
    id: str
    name: str
    email: str
    password: str
    shopping_cart: Optional[list]
    wish_list: Optional[list]

class UserResponse(BaseModel):
    name: str
    email: str
    shopping_cart: Optional[list] = None
    wish_list: Optional[list] = None

class VerifyCode(BaseModel):
    input: str