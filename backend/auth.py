"""
Módulo de autenticação e autorização.

Fornece funcionalidades para:
- Hash e verificação de senhas
- Criação e validação de tokens JWT
- Gerenciamento de usuários
- Autenticação via OAuth2 Bearer tokens
"""

from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional, List
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import database

SECRET_KEY = "chave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/integrations/auth")
pwd_context = CryptContext(schemes=['pbkdf2_sha256'])

def verify_password(plain_password, hashed_password):
    """
    Verifica se uma senha em texto plano corresponde ao hash armazenado.
    
    Args:
        plain_password: Senha em texto plano fornecida pelo usuário
        hashed_password: Hash da senha armazenado no banco de dados
        
    Returns:
        bool: True se a senha corresponder, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Gera o hash de uma senha usando o algoritmo pbkdf2_sha256.
    
    Args:
        password: Senha em texto plano a ser hasheada
        
    Returns:
        str: Hash da senha
    """
    return pwd_context.hash(password)

def get_user_by_login(db: Session, login: str):
    """
    Busca um usuário pelo login.
    
    Args:
        db: Sessão do banco de dados
        login: Login do usuário a ser buscado
        
    Returns:
        database.User ou None: Usuário encontrado ou None se não existir
    """
    return db.query(database.User).filter(database.User.login == login).first()

def create_user(db: Session, login: str, password: str):
    """
    Cria um novo usuário no banco de dados.
    
    A senha é automaticamente hasheada antes de ser armazenada.
    
    Args:
        db: Sessão do banco de dados
        login: Login único do usuário
        password: Senha em texto plano (será hasheada)
        
    Returns:
        database.User: Usuário criado
    """
    hashed_password = get_password_hash(password)

    db_user = database.User(login=login, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_id(db: Session, user_id: int):
    """
    Busca um usuário pelo ID.
    
    Args:
        db: Sessão do banco de dados
        user_id: ID do usuário a ser buscado
        
    Returns:
        database.User ou None: Usuário encontrado ou None se não existir
    """
    return db.query(database.User).filter(database.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[database.User]:
    """
    Lista usuários com paginação.
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros a pular (para paginação)
        limit: Número máximo de registros a retornar (padrão: 100)
        
    Returns:
        List[database.User]: Lista de usuários
    """
    return db.query(database.User).offset(skip).limit(limit).all()

def update_user_status(db: Session, user_id: int, is_active: bool) -> Optional[database.User]:
    """
    Atualiza o status de ativação de um usuário.
    
    Args:
        db: Sessão do banco de dados
        user_id: ID do usuário a ser atualizado
        is_active: Novo status de ativação (True ou False)
        
    Returns:
        database.User ou None: Usuário atualizado ou None se não existir
    """
    db_user = get_user_by_id(db, user_id=user_id)

    if db_user:
        db_user.is_active = is_active
        db.commit()
        db.refresh(db_user)

    return db_user

def delete_user(db: Session, user_id: int) -> Optional[database.User]:
    """
    Remove um usuário do banco de dados.
    
    Args:
        db: Sessão do banco de dados
        user_id: ID do usuário a ser removido
        
    Returns:
        database.User ou None: Usuário removido ou None se não existir
    """
    db_user = get_user_by_id(db, user_id=user_id)

    if db_user:
        db.delete(db_user)
        db.commit()

    return db_user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um token JWT de acesso.
    
    Args:
        data: Dados a serem codificados no token (geralmente contém "sub": username)
        expires_delta: Tempo de expiração customizado. Se None, usa o padrão (60 minutos)
        
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_access_token(token: str):
    """
    Decodifica e valida um token JWT.
    
    Args:
        token: Token JWT a ser decodificado
        
    Returns:
        dict: Payload do token decodificado
        
    Raises:
        HTTPException: 401 se o token for inválido ou expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency que valida o token JWT e retorna o usuário autenticado.
    
    Esta função é usada como dependency nos endpoints que requerem autenticação.
    
    Args:
        token: Token JWT extraído automaticamente do header Authorization
        
    Returns:
        str: Login do usuário autenticado
        
    Raises:
        HTTPException: 401 se o token for inválido, expirado ou não fornecido
    """
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