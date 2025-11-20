from fastapi import FastAPI
from pydantic import BaseModel, Field, UUID4
from uuid import UUID

app = FastAPI()

class AssetSchema(BaseModel):
    id: UUID4
    name: str = Field(..., max_length=140, description="Nome do ativo")
    category: str = Field(..., max_length=60, description="Categoria (ex.: Aeronave, Navio)")
    owner: UUID4

@app.post("/integrations/asset")
def create_asset(asset: AssetSchema):
    return asset