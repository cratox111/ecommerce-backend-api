from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt, JWTError, ExpiredSignatureError
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

def auth_user(token = Depends(oauth)):   
    try:
        token = jwt.decode(token=token, key=SECRET, algorithms=['HS256'])
        user = search_user(key='email', value=token['sub'])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User no existe'
            )

        del user['_id']
    except (JWTError, ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No tienes token o a expirado'
        )



    return UserResponse(**user)

@router.post('/register', status_code=201)
async def register(data_user: UserForm):
    if search_user(key='email', value=data_user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User existente'
        )
    
    
    hash_password = crypt.hash(data_user.password)
    data_user.password = hash_password

    user = dict(data_user)
    users.insert_one(user).inserted_id

    return {'msg': 'User creado'}

@router.post('/login', status_code=200)
async def login(data: OAuth2PasswordRequestForm = Depends()):
    user = search_user(key='email', value=data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='El usuario no existe'
        )
    
    if not crypt.verify(data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Contraseña incorrecta'
        )

    token = jwt.encode({
        'sub': user['email'],
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, SECRET, algorithm='HS256')

    return {'access_token': token, 'token_type': 'bearer'}
    
