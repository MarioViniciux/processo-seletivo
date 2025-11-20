from sqlalchemy.orm import Session, selectinload
from typing import Optional
from . import database, schemas
import uuid

def get_owner(db: Session, owner_id: uuid.UUID):
    return db.query(database.Owner).filter(database.Owner.id == owner_id).first()

def update_owner(db: Session, owner_id: uuid.UUID, owner_update: schemas.OwnerUpdate) -> Optional[database.Owner]:
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
    db_owner = db.query(database.Owner).filter(database.Owner.id == owner_id).first()

    if db_owner:
        db.delete(db_owner)
        db.commit()

        return db_owner
    
    return None

def create_asset(db: Session, asset: schemas.AssetCreate):
    db_asset = database.Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset

def get_asset(db: Session, asset_id: uuid.UUID):
    return db.query(database.Asset).options(selectinload(database.Asset.owner_ref)).filter(database.Asset.id == asset_id).first()

def update_asset(db: Session, asset_id: uuid.UUID, asset_update: schemas.AssetUpdate) -> Optional[database.Asset]:
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
    db_asset = db.query(database.Asset).filter(database.Asset.id == asset_id).first()

    if db_asset:
        db.delete(db_asset)
        db.commit()

        return db_asset
    
    return None