from pydantic import BaseModel
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
    id: str
    name: str
    email: str
    type_account: str