from fastapi import FastAPI
from routers import auth

app = FastAPI()

# Routers
app.include_router(auth.router)

@app.get('/')
async def root():
    return {'msg': 'Bienvanido'}