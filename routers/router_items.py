from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form, Depends
from db.schemas.model_item import ImageModel
from db.client import producs
from .auth import auth_user
from os import getcwd
from PIL import Image

router = APIRouter(prefix='/items', tags=['items'])
PATH_FILES = getcwd() + '/uploads/images/items/'

def resize_image(filename: str):
    sizes = [
        {"width": 1280, "height": 720},
        {"width": 640, "height": 480},
    ]
    for size in sizes:
        image = Image.open(PATH_FILES + filename)
        image.thumbnail((size["width"], size["height"]))
        image.save(PATH_FILES + f"{size['width']}_{size['height']}_{filename}")

@router.post("/create")
async def create_item(background_tasks: BackgroundTasks, file: UploadFile = File(...), name: str = Form(...), description: str = Form(...), price: str = Form(...), tpye: str = Form(...), user = Depends(auth_user)
):
    # Guardar archivo
    file_location = PATH_FILES + file.filename
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Redimensionar en background
    background_tasks.add_task(resize_image, file.filename)

    # Crear documento MongoDB
    product_doc = {
        "name": name,
        "description": description,
        "price": price,
        "seller": user.name,
        "img": ImageModel(
            filename=file.filename,
            path=file_location,
            sizes=["1280x720", "640x480"]
        ).dict()
    }

    producs.insert_one(product_doc).inserted_id

    return {"msg": "Producto guardado"}