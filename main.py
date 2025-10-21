from fastapi import FastAPI
from routers import auth, router_user

app = FastAPI()

# Routers
app.include_router(auth.router)
app.include_router(router_user.router)

@app.get('/')
async def root():
    return {'msg': 'Bienvanido'}