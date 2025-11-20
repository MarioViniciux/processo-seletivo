from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional, List
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from . import database

SECRET_KEY = "chave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/integrations/auth")
pwd_context = CryptContext(schemes=['pbkdf2_sha256'])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_login(db: Session, login: str):
    return db.query(database.User).filter(database.User.login == login).first()

def create_user(db: Session, login: str, password: str):
    hashed_password = get_password_hash(password)

    db_user = database.User(login=login, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(database.User).filter(database.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[database.User]:
    return db.query(database.User).offset(skip).limit(limit).all()

def update_user_status(db: Session, user_id: int, is_active: bool) -> Optional[database.User]:
    db_user = get_user_by_id(db, user_id=user_id)

    if db_user:
        db_user.is_active = is_active
        db.commit()
        db.refresh(db_user)

    return db_user

def delete_user(db: Session, user_id: int) -> Optional[database.User]:
    db_user = get_user_by_id(db, user_id=user_id)

    if db_user:
        db.delete(db_user)
        db.commit()

    return db_user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token) 

        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        return username 
        
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=401, detail="Não foi possível validar as credenciais")