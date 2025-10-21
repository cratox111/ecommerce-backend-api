from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt, JWTError, ExpiredSignatureError
from random import randrange
import smtplib
from email.mime.text import MIMEText
import os

from db.schemas.model_user import UserDB, UserForm, UserResponse
from db.client import users

load_dotenv()

router = APIRouter(prefix='/auth', tags=['Auth'])
SECRET = os.getenv('SECRET')

crypt = CryptContext(schemes=['argon2'])
oauth = OAuth2PasswordBearer(tokenUrl='/auth/login')
oauth_register = OAuth2PasswordBearer(tokenUrl='/auth/register')

# Mail
my_mail = os.getenv('MAIL')
my_password = os.getenv('PASSWORD_MAIL')


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

def verifity_mail(token = Depends(oauth_register)):
    try:
        token = jwt.decode(token=token, key=SECRET, algorithms=['HS256'])
        user = token['data']
    except (JWTError, ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No tienes token o a expirado'
        )

    return user

@router.post('/register', status_code=200)
async def register(data_user: UserForm):
    if search_user(key='email', value=data_user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User existente'
        )
    
    token = jwt.encode({
        'sub': data_user.email,
        'exp': datetime.utcnow() + timedelta(minutes=5),
        'data': dict(data_user)
    }, SECRET, algorithm='HS256')


    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/register/verifity', status_code=201)
async def verifity(input: str, data = Depends(verifity_mail)):
    email = data['email']
    codigo = randrange(100, 999)

    msg = MIMEText(f'Tu codigo de verificasion es {codigo}')
    msg['Subject'] = 'Codigo de verificasion'
    msg['From'] = my_mail
    msg['To'] = email

    try:
    # Connect to the SMTP server (e.g., Gmail's SMTP server)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            # Login to the account
            server.login(my_mail, my_password)
            # Send the email
            server.sendmail(my_mail, email, msg.as_string())
        
    except Exception as e:
        print(f"Error sending email: {e}")

    if not int(input) == codigo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= 'El correo no existe'
        )

    password = crypt.hash(data['password'])
    data['password'] = password

    users.insert_one(data).inserted_id

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
    
