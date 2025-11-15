from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, router_user, router_items

app = FastAPI()


# Sitios permitidos para acceder a la API
origins = [
    'http://localhost:5173'
]

# COnfiguracion de la API CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth.router)
app.include_router(router_user.router)
app.include_router(router_items.router)


@app.get('/')
async def root():
    return {'msg': 'Bienvanido'}