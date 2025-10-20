from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from dotenv import load_dotenv
from jose import jwt
import os

from db.schemas.model_user import UserDB, UserForm, UserResponse
from db.client import users

load_dotenv()

router = APIRouter(prefix='/auth', tags=['Auth'])
SECRET = os.getenv('SECRET')

crypt = CryptContext(schemes=['argon2'])
oauth = OAuth2PasswordBearer(tokenUrl='/auth/login')

def search_user(key, value):
    user = users.find_one({key: value})
    if not user:
        return None
    
    return user

@router.post('/register', status_code=201)
async def regsiter(data_user: UserForm):
    if search_user(key='email', value=data_user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User existente'
        )
    
    
    hash_password = crypt.hash(data_user.password)
    data_user.password = hash_password

    user = dict(data_user)
    users.insert_one(user)

    return {'msg': 'User creado'}

@router.post('/login', status_code=200)
async def login(user:OAuth2PasswordRequestForm):
    pass

    
