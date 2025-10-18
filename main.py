from fastapi import FastAPI

app = FastAPI()

# Routers


async def root():
    return {'msg': 'Bienvanido'}