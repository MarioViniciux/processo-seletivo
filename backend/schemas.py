from pydantic import BaseModel, Field, UUID4, EmailStr, ConfigDict
from typing import Optional

class OwnerCreate(BaseModel):
    name: str = Field(..., max_length=140)
    email: EmailStr = Field(..., max_length=140)
    phone: str = Field(..., max_length=20)

class OwnerSchema(OwnerCreate):
    id: UUID4
    
    model_config = ConfigDict(from_attributes=True)

class OwnerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=140)
    email: Optional[EmailStr] = Field(None, max_length=140)
    phone: Optional[str] = Field(None, max_length=20)

class AssetCreate(BaseModel):
    name: str = Field(..., max_length=140)
    category: str = Field(..., max_length=60)
    owner_id: UUID4

class AssetSchema(AssetCreate):
    id: UUID4
    owner_ref: Optional[OwnerSchema] = None 

    model_config = ConfigDict(from_attributes=True)

class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=140, description="Nome do ativo")
    category: Optional[str] = Field(None, max_length=60, description="Categoria (ex.: Aeronave, Navio)")
    owner_id: Optional[UUID4] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginData(BaseModel):
    login: str
    password: str