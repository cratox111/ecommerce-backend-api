from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

class UserForm(BaseModel):
    name: str
    email: str
    password: str
    type_account: str

class UserDB(BaseModel):
    id: str
    name: str
    email: str
    password: str
    shopping_cart: Optional[list]
    wish_list: Optional[list]
    type_account: str

class UserResponse(BaseModel):
    name: str
    email: str
    shopping_cart: Optional[list] = None
    wish_list: Optional[list] = None
    type_account: str