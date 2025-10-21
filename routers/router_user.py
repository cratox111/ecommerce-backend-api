from fastapi import APIRouter, HTTPException, status, Depends

from .auth import auth_user

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/me')
async def me(user = Depends(auth_user)):
    return user