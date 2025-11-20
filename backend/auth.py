from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, status
from typing import Optional
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "chave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/integrations/auth")

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