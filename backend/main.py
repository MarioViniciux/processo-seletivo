from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from . import database, schemas, crud, auth
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    db_owner = database.Owner(**owner.model_dump())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)

    return db_owner

@app.put("/integrations/owner/{owner_id}", response_model=schemas.OwnerSchema)
def update_owner(
    owner_id: uuid.UUID, owner_update: schemas.OwnerUpdate, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    db_owner = crud.update_owner(db, owner_id=owner_id, owner_update=owner_update)

    if db_owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Responsável com ID {owner_id} não encontrado.")

    return db_owner

@app.get("/integrations/owner/{owner_id}", response_model=schemas.OwnerSchema)
def read_owner(owner_id: uuid.UUID, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    owner = crud.get_owner(db, owner_id=owner_id)

    if owner is None:
        raise HTTPException(status_code=404, detail="Responsável não encontrado")

    return owner

@app.get("/integrations/owner", response_model=List[schemas.OwnerSchema])
def read_owners(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    owners = crud.get_owners(db, skip=skip, limit=limit)

    return owners

@app.delete("/integrations/owner/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(owner_id: uuid.UUID,db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    db_owner = crud.delete_owner(db, owner_id=owner_id)

    if db_owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Responsável com ID {owner_id} não encontrado")

    return

@app.post("/integrations/asset", response_model=schemas.AssetSchema)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
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
    asset = crud.get_asset(db, asset_id=asset_id)

    if asset is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    return asset

@app.get("/integrations/asset", response_model=List[schemas.AssetSchema])
def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_assets(db, skip=skip, limit=limit)

@app.put("/integrations/asset/{asset_id}", response_model=schemas.AssetSchema) 
def update_asset(
    asset_id: uuid.UUID,
    asset_update: schemas.AssetUpdate,
    db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)
):
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
    db_asset = crud.delete_asset(db, asset_id=asset_id)

    if db_asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ativo com ID {asset_id} não encontrado")

    return

@app.post("/integrations/auth", response_model=schemas.Token)
def login_access_token(form_data: schemas.LoginData, db: Session = Depends(database.get_db)):
    user = auth.get_user_by_login(db, login=form_data.login)

    if user is None or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas", headers={"WWW-Authenticate": "Bearer"})
    
    access_token = auth.create_access_token(data={"sub": user.login})

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/integrations/user", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(user_data: schemas.LoginData, db: Session = Depends(database.get_db)):
    if auth.get_user_by_login(db, login=user_data.login):
        raise HTTPException(status_code=400, detail="Login já registrado")

    return auth.create_user(db, login=user_data.login, password=user_data.password)

@app.get("/integrations/user", response_model=List[schemas.UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    return auth.get_users(db, skip=skip, limit=limit)

@app.get("/integrations/user/{user_id}", response_model=schemas.UserSchema)
def read_user_by_id(user_id: int, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    user = auth.get_user_by_id(db, user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user

@app.delete("/integrations/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(database.get_db), current_user: str = Depends(auth.get_current_user)):
    if auth.delete_user(db, user_id=user_id) is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return
