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

from db.schemas.model_user import UserDB, UserForm, UserResponse, VerifyCode
from db.client import users

load_dotenv()

router = APIRouter(prefix='/auth', tags=['Auth'])
SECRET = os.getenv('SECRET')

crypt = CryptContext(schemes=['argon2'])  # Definicion del algoritmo a usar con el hasheo de contraseñas
oauth_register = OAuth2PasswordBearer(tokenUrl='/auth/register')  # Definicion del token para el registro de usuarios
oauth = OAuth2PasswordBearer(tokenUrl='/auth/login')  # Definicon del token a usar para el logeo de usuarios

my_mail = os.getenv('MAIL')
my_password = os.getenv('PASSWORD_MAIL')

codigos = []

# Busqueda de usuarios
def search_user(key, value):
    user = users.find_one({key: value})
    if not user:
        return None
    
    return user

# Retorno de la info de usuarios mediante el token
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

# Verifica el email despues que el usario ingresa sus datos
def verify_mail(token = Depends(oauth_register)):
    try:
        token = jwt.decode(token=token, key=SECRET, algorithms=['HS256'])
        user = token['data']
    except (JWTError, ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No tienes token o a expirado'
        )

    return user

# Ruta para el registro de usuarios
@router.post('/register', status_code=200)
async def register(data_user: UserForm):
    if search_user(key='email', value=data_user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User existente'
        )

    g_codigo = randrange(100, 999)
    codigos.append({'email': data_user.email, 'codigo': g_codigo})

    # enviar correo
    msg = MIMEText(f'Tu codigo de verificación es {g_codigo}')
    msg['Subject'] = 'Verificación de correo'
    msg['From'] = my_mail
    msg['To'] = data_user.email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(my_mail, my_password)
            server.sendmail(my_mail, data_user.email, msg.as_string())
    except Exception as e:
        print(f"Error enviando correo: {e}")

    # crear token temporal con los datos del usuario
    token = jwt.encode({
        'sub': data_user.email,
        'exp': datetime.utcnow() + timedelta(minutes=5),
        'data': dict(data_user)
    }, SECRET, algorithm='HS256')

    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/register/verify', status_code=201)
async def verify(input: VerifyCode, data = Depends(verify_mail)):
    input_code = int(input.input)
    email = data['email']

    # buscar código para este email
    registro = next((c for c in codigos if c['email'] == email), None)

    if not registro or registro['codigo'] != input_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Código incorrecto'
        )

    # eliminar código usado
    codigos.remove(registro)

    # registrar usuario
    password = crypt.hash(data['password'])
    data['password'] = password
    users.insert_one(data).inserted_id

    return {'msg': 'Usuario creado correctamente'}
 

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
    
