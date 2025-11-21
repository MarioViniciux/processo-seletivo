"""
Módulo de operações CRUD (Create, Read, Update, Delete).

Fornece funções para manipulação de dados de Owners (Responsáveis) e Assets (Ativos)
no banco de dados usando SQLAlchemy ORM.
"""

from sqlalchemy.orm import Session, selectinload
from typing import Optional
import database, schemas
import uuid

def get_owner(db: Session, owner_id: uuid.UUID):
    """
    Busca um responsável pelo ID.
    
    Args:
        db: Sessão do banco de dados
        owner_id: UUID do responsável a ser buscado
        
    Returns:
        database.Owner ou None: Responsável encontrado ou None se não existir
    """
    return db.query(database.Owner).filter(database.Owner.id == owner_id).first()

def get_owners(db: Session, skip: int = 0, limit: int = 100):
    """
    Lista responsáveis com paginação.
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros a pular (para paginação)
        limit: Número máximo de registros a retornar (padrão: 100)
        
    Returns:
        List[database.Owner]: Lista de responsáveis
    """
    return db.query(database.Owner).offset(skip).limit(limit).all()

def update_owner(db: Session, owner_id: uuid.UUID, owner_update: schemas.OwnerUpdate) -> Optional[database.Owner]:
    """
    Atualiza os dados de um responsável existente.
    
    Permite atualização parcial - apenas campos fornecidos serão atualizados.
    
    Args:
        db: Sessão do banco de dados
        owner_id: UUID do responsável a ser atualizado
        owner_update: Dados a serem atualizados (campos opcionais)
        
    Returns:
        database.Owner ou None: Responsável atualizado ou None se não existir
    """
    db_owner = db.query(database.Owner).filter(database.Owner.id == owner_id).first()

    if db_owner:
        update_data: Dict[str, Any] = owner_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_owner, key, value)
        
        db.add(db_owner)
        db.commit()
        db.refresh(db_owner)

    return db_owner

def delete_owner(db: Session, owner_id: uuid.UUID) -> Optional[database.Owner]:
    """
    Remove um responsável do banco de dados.
    
    A exclusão de um responsável também remove todos os ativos associados
    devido ao cascade delete configurado no relacionamento.
    
    Args:
        db: Sessão do banco de dados
        owner_id: UUID do responsável a ser removido
        
    Returns:
        database.Owner ou None: Responsável removido ou None se não existir
    """
    db_owner = db.query(database.Owner).filter(database.Owner.id == owner_id).first()

    if db_owner:
        db.delete(db_owner)
        db.commit()

        return db_owner
    
    return None

def create_asset(db: Session, asset: schemas.AssetCreate):
    """
    Cria um novo ativo no banco de dados.
    
    Args:
        db: Sessão do banco de dados
        asset: Dados do ativo a ser criado
        
    Returns:
        database.Asset: Ativo criado
    """
    db_asset = database.Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset

def get_asset(db: Session, asset_id: uuid.UUID):
    """
    Busca um ativo pelo ID com carregamento eager do relacionamento owner_ref.
    
    Args:
        db: Sessão do banco de dados
        asset_id: UUID do ativo a ser buscado
        
    Returns:
        database.Asset ou None: Ativo encontrado com owner_ref carregado ou None se não existir
    """
    return db.query(database.Asset).options(selectinload(database.Asset.owner_ref)).filter(database.Asset.id == asset_id).first()

def get_assets(db: Session, skip: int = 0, limit: int = 100):
    """
    Lista ativos com paginação e carregamento eager do relacionamento owner_ref.
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros a pular (para paginação)
        limit: Número máximo de registros a retornar (padrão: 100)
        
    Returns:
        List[database.Asset]: Lista de ativos com owner_ref carregado
    """
    return db.query(database.Asset).options(selectinload(database.Asset.owner_ref)).offset(skip).limit(limit).all()

def update_asset(db: Session, asset_id: uuid.UUID, asset_update: schemas.AssetUpdate) -> Optional[database.Asset]:
    """
    Atualiza os dados de um ativo existente.
    
    Permite atualização parcial e valida se o novo owner_id (se fornecido) existe.
    Utiliza transação com rollback em caso de erro.
    
    Args:
        db: Sessão do banco de dados
        asset_id: UUID do ativo a ser atualizado
        asset_update: Dados a serem atualizados (campos opcionais)
        
    Returns:
        database.Asset ou None: Ativo atualizado com owner_ref carregado ou None se:
            - O ativo não existir
            - O novo owner_id não existir
            - Ocorrer erro durante a atualização
    """
    db_asset = db.query(database.Asset).filter(database.Asset.id == asset_id).first()

    if db_asset:
        update_data: Dict[str, Any] = asset_update.model_dump(exclude_unset=True)

        if "owner_id" in update_data:
            new_owner = get_owner(db, owner_id=update_data['owner_id'])

            if new_owner is None:
                return None
        
        for key, value in update_data.items():
            setattr(db_asset, key, value)

        
        try:
            db.commit()
            db.refresh(db_asset)

            update_count = db.query(database.Asset).filter(database.Asset.id == asset_id).update(update_data, synchronize_session="fetch")

            if update_count == 0:
                db.rollback() 
                return None

            updated_asset = (
                db.query(database.Asset)
                .options(selectinload(database.Asset.owner_ref))
                .filter(database.Asset.id == asset_id)
                .first()
            )
        
            return updated_asset
        except Exception as e:
            db.rollback()
            print(f"Erro durante o commit: {e}")
            
            return None
    
    return None

def delete_asset(db: Session, asset_id: uuid.UUID) -> Optional[database.Asset]:
    """
    Remove um ativo do banco de dados.
    
    Args:
        db: Sessão do banco de dados
        asset_id: UUID do ativo a ser removido
        
    Returns:
        database.Asset ou None: Ativo removido ou None se não existir
    """
    db_asset = db.query(database.Asset).filter(database.Asset.id == asset_id).first()

    if db_asset:
        db.delete(db_asset)
        db.commit()

        return db_asset
    
    return None