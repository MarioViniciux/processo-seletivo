"""
Módulo principal da API FastAPI para gerenciamento de integrações.

Este módulo define os endpoints da API REST para operações CRUD de:
- Owners (Responsáveis)
- Assets (Ativos)
- Users (Usuários)
- Autenticação

A API utiliza autenticação via JWT Bearer tokens e CORS configurado
para permitir requisições do frontend.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import database, schemas, crud, auth
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de contexto para o ciclo de vida da aplicação.
    
    Executa operações de inicialização e finalização da aplicação:
    - Cria as tabelas do banco de dados na inicialização
    - Cria usuário de teste padrão se não existir
    - Executa cleanup na finalização
    
    Args:
        app: Instância da aplicação FastAPI
        
    Yields:
        None: Controla o ciclo de vida da aplicação
    """
    print("Iniciando a aplicação e criando o database...")
    database.create_db_and_tables()

    with database.SessionLocal() as db:
        if auth.get_user_by_login(db, login="eyesonasset") is None:
            auth.create_user(db, login="eyesonasset", password="eyesonasset")
            print("Usuário de teste 'eyesonasset' criado no DB.")

    yield

    print("Desligando a aplicação.")

app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.post("/integrations/owner", response_model=schemas.OwnerSchema)
def create_owner(owner: schemas.OwnerCreate, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Cria um novo responsável (owner) no sistema.
    
    Args:
        owner: Dados do responsável a ser criado (nome, email, telefone)
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        schemas.OwnerSchema: Dados do responsável criado incluindo ID
        
    Raises:
        HTTPException: Se houver erro de validação ou autenticação
    """
    db_owner = database.Owner(**owner.model_dump())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)

    return db_owner

@app.put("/integrations/owner/{owner_id}", response_model=schemas.OwnerSchema)
def update_owner(
    owner_id: uuid.UUID, owner_update: schemas.OwnerUpdate, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Atualiza os dados de um responsável existente.
    
    Permite atualização parcial (apenas campos fornecidos serão atualizados).
    
    Args:
        owner_id: UUID do responsável a ser atualizado
        owner_update: Dados a serem atualizados (campos opcionais)
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        schemas.OwnerSchema: Dados atualizados do responsável
        
    Raises:
        HTTPException: 404 se o responsável não for encontrado
    """
    db_owner = crud.update_owner(db, owner_id=owner_id, owner_update=owner_update)

    if db_owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Responsável com ID {owner_id} não encontrado.")

    return db_owner

@app.get("/integrations/owner/{owner_id}", response_model=schemas.OwnerSchema)
def read_owner(owner_id: uuid.UUID, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Busca um responsável específico pelo ID.
    
    Args:
        owner_id: UUID do responsável a ser buscado
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        schemas.OwnerSchema: Dados do responsável encontrado
        
    Raises:
        HTTPException: 404 se o responsável não for encontrado
    """
    owner = crud.get_owner(db, owner_id=owner_id)

    if owner is None:
        raise HTTPException(status_code=404, detail="Responsável não encontrado")

    return owner

@app.get("/integrations/owner", response_model=List[schemas.OwnerSchema])
def read_owners(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Lista todos os responsáveis com paginação.
    
    Args:
        skip: Número de registros a pular (para paginação)
        limit: Número máximo de registros a retornar (padrão: 100)
        db: Sessão do banco de dados (injetada via dependency)
        
    Returns:
        List[schemas.OwnerSchema]: Lista de responsáveis
    """
    owners = crud.get_owners(db, skip=skip, limit=limit)

    return owners

@app.delete("/integrations/owner/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(owner_id: uuid.UUID,db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Remove um responsável do sistema.
    
    A exclusão de um responsável também remove todos os ativos associados
    (cascade delete).
    
    Args:
        owner_id: UUID do responsável a ser removido
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        None: Status 204 (No Content) em caso de sucesso
        
    Raises:
        HTTPException: 404 se o responsável não for encontrado
    """
    db_owner = crud.delete_owner(db, owner_id=owner_id)

    if db_owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Responsável com ID {owner_id} não encontrado")

    return

@app.post("/integrations/asset", response_model=schemas.AssetSchema)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Cria um novo ativo no sistema.
    
    O ativo deve estar associado a um responsável existente.
    
    Args:
        asset: Dados do ativo a ser criado (nome, categoria, owner_id)
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        schemas.AssetSchema: Dados do ativo criado incluindo referência ao responsável
        
    Raises:
        HTTPException: 404 se o responsável especificado não for encontrado
    """
    owner = crud.get_owner(db, owner_id=asset.owner_id)
    
    if owner is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Responsável com ID '{asset.owner_id}' não encontrado. O ativo não pode ser cadastrado."
        )

    db_asset = crud.create_asset(db, asset=asset)
    db_asset.owner_ref = owner

    return db_asset

@app.get("/integrations/asset/{asset_id}", response_model=schemas.AssetSchema)
def read_asset(asset_id: uuid.UUID, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Busca um ativo específico pelo ID.
    
    Retorna o ativo com a referência completa ao responsável (owner_ref).
    
    Args:
        asset_id: UUID do ativo a ser buscado
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        schemas.AssetSchema: Dados do ativo encontrado com referência ao responsável
        
    Raises:
        HTTPException: 404 se o ativo não for encontrado
    """
    asset = crud.get_asset(db, asset_id=asset_id)

    if asset is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    return asset

@app.get("/integrations/asset", response_model=List[schemas.AssetSchema])
def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Lista todos os ativos com paginação.
    
    Args:
        skip: Número de registros a pular (para paginação)
        limit: Número máximo de registros a retornar (padrão: 100)
        db: Sessão do banco de dados (injetada via dependency)
        
    Returns:
        List[schemas.AssetSchema]: Lista de ativos
    """
    return crud.get_assets(db, skip=skip, limit=limit)

@app.put("/integrations/asset/{asset_id}", response_model=schemas.AssetSchema) 
def update_asset(
    asset_id: uuid.UUID,
    asset_update: schemas.AssetUpdate,
    db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)
):
    """
    Atualiza os dados de um ativo existente.
    
    Permite atualização parcial e alteração do responsável associado.
    
    Args:
        asset_id: UUID do ativo a ser atualizado
        asset_update: Dados a serem atualizados (campos opcionais)
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        schemas.AssetSchema: Dados atualizados do ativo
        
    Raises:
        HTTPException: 404 se o ativo ou novo responsável não forem encontrados
    """
    db_asset = crud.update_asset(db, asset_id=asset_id, asset_update=asset_update)

    if db_asset is None:
        if asset_update.owner_id is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Responsável com ID {asset_update.owner} não encontrado")

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ativo com ID {asset_id} não encontrado.")


    return db_asset

@app.delete("/integrations/asset/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: uuid.UUID, 
    db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)
):
    """
    Remove um ativo do sistema.
    
    Args:
        asset_id: UUID do ativo a ser removido
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        None: Status 204 (No Content) em caso de sucesso
        
    Raises:
        HTTPException: 404 se o ativo não for encontrado
    """
    db_asset = crud.delete_asset(db, asset_id=asset_id)

    if db_asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ativo com ID {asset_id} não encontrado")

    return

@app.post("/integrations/auth", response_model=schemas.Token)
def login_access_token(form_data: schemas.LoginData, db: Session = Depends(database.get_db)):
    """
    Autentica um usuário e retorna um token de acesso JWT.
    
    Args:
        form_data: Credenciais de login (login e senha)
        db: Sessão do banco de dados (injetada via dependency)
        
    Returns:
        schemas.Token: Token de acesso JWT e tipo de token
        
    Raises:
        HTTPException: 401 se as credenciais forem inválidas
    """
    user = auth.get_user_by_login(db, login=form_data.login)

    if user is None or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas", headers={"WWW-Authenticate": "Bearer"})
    
    access_token = auth.create_access_token(data={"sub": user.login})

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/integrations/user", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(user_data: schemas.LoginData, db: Session = Depends(database.get_db)):
    """
    Cria um novo usuário no sistema.
    
    Args:
        user_data: Dados do usuário (login e senha)
        db: Sessão do banco de dados (injetada via dependency)
        
    Returns:
        schemas.UserSchema: Dados do usuário criado (sem senha)
        
    Raises:
        HTTPException: 400 se o login já estiver registrado
    """
    if auth.get_user_by_login(db, login=user_data.login):
        raise HTTPException(status_code=400, detail="Login já registrado")

    return auth.create_user(db, login=user_data.login, password=user_data.password)

@app.get("/integrations/user", response_model=List[schemas.UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Lista todos os usuários com paginação.
    
    Args:
        skip: Número de registros a pular (para paginação)
        limit: Número máximo de registros a retornar (padrão: 100)
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        List[schemas.UserSchema]: Lista de usuários
    """
    return auth.get_users(db, skip=skip, limit=limit)

@app.get("/integrations/user/{user_id}", response_model=schemas.UserSchema)
def read_user_by_id(user_id: int, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Busca um usuário específico pelo ID.
    
    Args:
        user_id: ID do usuário a ser buscado
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        schemas.UserSchema: Dados do usuário encontrado
        
    Raises:
        HTTPException: 404 se o usuário não for encontrado
    """
    user = auth.get_user_by_id(db, user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user

@app.delete("/integrations/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    """
    Remove um usuário do sistema.
    
    Args:
        user_id: ID do usuário a ser removido
        db: Sessão do banco de dados (injetada via dependency)
        current_user: Usuário autenticado (injetado via dependency)
        
    Returns:
        None: Status 204 (No Content) em caso de sucesso
        
    Raises:
        HTTPException: 404 se o usuário não for encontrado
    """
    if auth.delete_user(db, user_id=user_id) is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return
