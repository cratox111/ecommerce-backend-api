from pydantic import BaseModel
from typing import Optional

class ImageModel(BaseModel):
    filename: str
    path: str
    sizes: list[str]


class ItemDB(BaseModel):
    id: str
    name: str
    description: str
    comments: str
    price: str
    seller: str
    img: ImageModel

class ItemForm(BaseModel):
    name: str
    description: str
    price: str

