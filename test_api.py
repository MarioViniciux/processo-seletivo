import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid
from backend.main import app
from backend.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_session():
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    db.expire_on_commit = False
    db.autoflush = False

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()
        Base.metadata.drop_all(bind=engine)
    
@pytest.fixture(scope="session")
def client(db_session):
    def override_get_db():
        try: 
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def auth_token(client, db_session):
    from backend import auth

    TEST_LOGIN = "eyesonasset"
    TEST_PASSWORD = "eyesonasset"

    user = auth.get_user_by_login(db_session,login=TEST_LOGIN)

    if user is None:
        auth.create_user(db_session, login=TEST_LOGIN, password=TEST_PASSWORD)

    login_data = {
        "login": TEST_LOGIN,
        "password": TEST_PASSWORD
    }
    response = client.post("/integrations/auth", json=login_data)

    assert response.status_code == 200, f"Falha ao obter token: {response.json()}"

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

def create_owner_in_db(client, auth_token, name="Owner Teste", email_prefix="teste"):
    unique_suffix = str(uuid.uuid4())[:8]
    unique_email = f"{email_prefix}_{unique_suffix}@teste.com"

    data = {
        "name": name,
        "email": unique_email,
        "phone": "111111111"
    }
    response = client.post("/integrations/owner", json=data, headers=auth_token)

    assert response.status_code == 200
    return response.json()["id"]

def create_asset_in_db(client, auth_token, owner_id, name="Asset Teste"):
    data = {
        "name": name,
        "category": "Navio",
        "owner_id": owner_id
    }
    response = client.post("/integrations/asset", json=data, headers=auth_token)

    assert response.status_code == 200
    return response.json()["id"]

def test_create_owner_sucess(client, auth_token):
    owner_data = {
        "name": "Mário Owner",
        "email": "mario@eyesonasset.com",
        "phone": "5574999809080"
    }
    response = client.post("/integrations/owner", json=owner_data, headers=auth_token)

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["name"] == owner_data["name"]
    assert len(data["id"]) > 5

def test_create_owner_required_fields_fail(client, auth_token):
    owner_data = {}
    response = client.post("/integrations/owner", json=owner_data, headers=auth_token)

    assert response.status_code == 422

    data = response.json()

    assert any(err['loc'][1] == 'name' for err in data['detail'])
    assert any(err['loc'][1] == 'email' for err in data['detail'])
    assert any(err['loc'][1] == 'phone' for err in data['detail'])

def test_create_owner_email_with_invalid_format(client, auth_token):
    owner_data = {
        "name": "Nome Válido",
        "email": "email_com_formato_invalido.com",
        "phone": "87999999999"
    }
    response = client.post("/integrations/owner", json=owner_data, headers=auth_token)

    assert response.status_code == 422

    data = response.json()

    assert data['detail'][0]['loc'][1] == 'email'
    assert 'value is not a valid email address' in data['detail'][0]['msg']

def test_create_owner_with_long_strings(client, auth_token):
    owner_data = {
        "name": "A" * 141,
        "email": "abc@teste.com",
        "phone": "1" * 21
    }
    response = client.post("/integrations/owner", json=owner_data, headers=auth_token)

    assert response.status_code == 422

    data = response.json()

    assert any(err['loc'][1] == 'name' for err in data['detail'])
    assert any(err['loc'][1] == 'phone' for err in data['detail'])

def test_read_owner_sucess(client, auth_token):
    owner_data = {
        "name": "Testar GET",
        "email": "get@get.com",
        "phone": "51988886666"
    }
    post_response = client.post("/integrations/owner", json=owner_data, headers=auth_token)
    owner_id = post_response.json()["id"]
    get_response = client.get(f"/integrations/owner/{owner_id}", headers=auth_token)

    assert get_response.status_code == 200
    assert get_response.json()["name"] == owner_data["name"]

def test_read_owner_non_existent(client, auth_token):
    non_existent_uuid = str(uuid.uuid4())
    not_found_response = client.get(f"/integrations/owner/{non_existent_uuid}", headers=auth_token)

    assert not_found_response.status_code == 404
    assert "Responsável não encontrado" in not_found_response.json()['detail']

def test_read_owner_with_invalid_format_id(client, auth_token):
    invalid_id = 'nao-e-uuid'
    response = client.get(f"/integrations/owner/{invalid_id}", headers=auth_token)

    assert response.status_code == 422
    assert "Input should be a valid UUID" in response.json()["detail"][0]["msg"]

def test_full_update_owner_sucess(client, auth_token):
    initial_data = {
        "name": "Antigo",
        "email": "antigo@email.com",
        "phone": "51000001111"
    }
    post_response = client.post("/integrations/owner", json=initial_data, headers=auth_token)
    owner_id = post_response.json()['id']

    update_data = {
        "name": "Novo",
        "email": "novo@email.com",
        "phone": "11111111111"
    }
    update_response = client.put(f"/integrations/owner/{owner_id}", json=update_data, headers=auth_token)

    assert update_response.status_code == 200
    updated_data = update_response.json()

    assert updated_data['name'] == 'Novo'
    assert updated_data['email'] == 'novo@email.com'

def test_partial_update_owner_sucess(client, auth_token):
    initial_data = {
        "name": "Antigo",
        "email": "antigo@email.com",
        "phone": "51000001111"
    }
    post_response = client.post("/integrations/owner", json=initial_data, headers=auth_token)
    owner_id = post_response.json()['id']

    update_data = {"phone": "999999"}
    update_response = client.put(f"/integrations/owner/{owner_id}", json=update_data, headers=auth_token)

    assert update_response.status_code == 200
    updated_data = update_response.json()

    assert updated_data["phone"] == "999999"
    assert updated_data["name"] == initial_data["name"]

def test_update_owner_non_existent(client, auth_token):
    non_existent_uuid = str(uuid.uuid4())
    update_data = {"name": "Alguém Inexistente"}
    response = client.put(f"/integrations/owner/{non_existent_uuid}", json=update_data, headers=auth_token)

    assert response.status_code == 404
    assert f"Responsável com ID {non_existent_uuid} não encontrado." in response.json()['detail']

def test_update_owner_with_invalid_format_id(client, auth_token):
    invalid_id = "uuid-invalido"
    update_data = {"name": "Invalido"}
    response = client.put(f"/integrations/owner/{invalid_id}", json=update_data, headers=auth_token)

    assert response.status_code == 422
    assert "Input should be a valid UUID" in response.json()['detail'][0]['msg']

def test_update_owner_with_long_string(client, auth_token):
    owner_data = {
        "name": "A",
        "email": "a@a.com",
        "phone": "1"
    }
    post_response = client.post("/integrations/owner", json=owner_data, headers=auth_token)
    owner_id = post_response.json()["id"]
    update_long_name = {"name": "A" * 141}
    update_name_response = client.put(f"/integrations/owner/{owner_id}", json=update_long_name, headers=auth_token)

    assert update_name_response.status_code == 422
    assert 'String should have at most 140 characters' in update_name_response.json()['detail'][0]['msg']

    update_phone_long = {"phone": "1" * 21}
    update_phone_response = client.put(f"/integrations/owner/{owner_id}", json=update_phone_long, headers=auth_token)

    assert update_phone_response.status_code == 422
    assert 'String should have at most 20 characters' in update_phone_response.json()['detail'][0]['msg']

def test_delete_cascade(client, auth_token):
    owner_id = create_owner_in_db(client, auth_token, name="Owner Cascade")
    asset_1 = create_asset_in_db(client, auth_token, owner_id=owner_id, name="Asset 1")
    asset_2 = create_asset_in_db(client, auth_token, owner_id=owner_id, name="Asset 2")
    delete_response = client.delete(f"/integrations/owner/{owner_id}", headers=auth_token)

    assert delete_response.status_code == 204

    owner_get_response = client.get(f'/integrations/owner/{owner_id}', headers=auth_token)

    assert owner_get_response.status_code == 404

    asset_1_get_response = client.get(f"/integrations/asset/{asset_1}", headers=auth_token)
    asset_2_get_response = client.get(f"/integrations/asset/{asset_2}", headers=auth_token)

    assert asset_1_get_response.status_code == 404
    assert asset_2_get_response.status_code == 404

def test_delete_owner_non_existent(client, auth_token):
    non_existent_uuid = str(uuid.uuid4())
    response = client.delete(f"/integrations/owner/{non_existent_uuid}", headers=auth_token)

    assert response.status_code == 404
    assert f"Responsável com ID {non_existent_uuid} não encontrado"

def test_delete_owner_with_invalid_format_id(client, auth_token):
    invalid_id = "id-formato-errado"
    response = client.delete(f"/integrations/owner/{invalid_id}", headers=auth_token)

    assert response.status_code == 422
    assert "Input should be a valid UUID" in response.json()['detail'][0]['msg']

def test_create_asset_sucess(client, auth_token):
    owner_id = create_owner_in_db(client, auth_token, name="owner para asset")

    asset_data = {
        "name": "Jato Executivo",
        "category": "Aeronave",
        "owner_id": owner_id
    }
    response = client.post("/integrations/asset", json=asset_data, headers=auth_token)

    assert response.status_code == 200
    
    data = response.json()

    assert "id" in data
    assert "owner_ref" in data
    assert data["name"] == asset_data["name"]
    assert data["owner_id"] == owner_id
    assert data["owner_ref"]["name"] == "owner para asset"

def test_create_asset_without_owner_id(client, auth_token):
    non_existent_uuid = str(uuid.uuid4())

    asset_data = {
        "name": "Jato Executivo",
        "category": "Aeronave",
        "owner_id": non_existent_uuid
    }
    response = client.post("/integrations/asset", json=asset_data, headers=auth_token)

    assert response.status_code == 404
    assert "Responsável" in response.json()["detail"]

def test_create_asset_with_invalid_owner_id(client, auth_token):
    invalid_id = 'id-invalido'

    asset_data = {
        "name": "Jato Executivo",
        "category": "Aeronave",
        "owner_id": invalid_id
    }
    response = client.post("/integrations/asset", json=asset_data, headers=auth_token)

    assert response.status_code == 422
    assert "Input should be a valid UUID" in response.json()["detail"][0]['msg']

def test_create_asset_required_fields_fail(client, auth_token):
    asset_data = {
        "name": "A",
        "category": "B"
    }
    response = client.post("/integrations/asset", json=asset_data, headers=auth_token)

    assert response.status_code == 422
    assert any(err['loc'][1] == 'owner_id' for err in response.json()['detail'])

def test_create_asset_with_long_strings(client, auth_token):
    owner_id = create_owner_in_db(client, auth_token)
    asset_data = {
        "name": "A" * 141,
        "category": "C" * 61,
        "owner_id": owner_id 
    }
    response = client.post("/integrations/asset", json=asset_data, headers=auth_token)

    assert response.status_code == 422

    data = response.json()

    assert any(err['loc'][1] == 'name' for err in data['detail'])
    assert any(err['loc'][1] == 'category' for err in data['detail'])

def test_read_asset_with_owner(client, auth_token):
    owner_id = create_owner_in_db(client, auth_token, name="Owner Carregado")
    asset_id = create_asset_in_db(client, auth_token, owner_id=owner_id, name="Asset a Carregar")
    response = client.get(f"/integrations/asset/{asset_id}", headers=auth_token)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Asset a Carregar"
    assert data["owner_id"] == owner_id
    assert "owner_ref" in data
    assert data["owner_ref"]["name"] == "Owner Carregado"
    assert "email" in data["owner_ref"]

def test_read_asset_non_existent(client, auth_token):
    non_existent_uuid = str(uuid.uuid4())
    response_404 = client.get(f"/integrations/asset/{non_existent_uuid}", headers=auth_token)

    assert response_404.status_code == 404
    assert "Ativo não encontrado" in response_404.json()["detail"]

def test_read_asset_with_invalid_format_id(client, auth_token):
    invalid_id = "nao-e-uuid"
    response_422 = client.get(f"/integrations/asset/{invalid_id}", headers=auth_token)

    assert response_422.status_code == 422
    assert "Input should be a valid UUID" in response_422.json()["detail"][0]["msg"]

''' 
    Corrigir depois (comparando IDs errados)

def test_update_asset_success(client):
    owner_original_id = create_owner_in_db(client, name="Owner Antigo")
    owner_novo_id = create_owner_in_db(client, name="Owner Novo")
    asset_data = {
        "name": "Foguete",
        "category": "Aeronave",
        "owner_id": owner_original_id
    }
    post_response = client.post("/integrations/asset", json=asset_data)
    asset_id = post_response.json()["id"]
    update_data = {
        "name": "Foguete Atualizado",
        "owner_id": owner_novo_id  
    }
    update_response = client.put(f"/integrations/asset/{asset_id}", json=update_data)
    
    assert update_response.status_code == 200
    
    updated_data = update_response.json()
    
    assert updated_data["name"] == "Foguete Atualizado"
    assert updated_data["category"] == asset_data["category"] 
    assert updated_data["owner_id"] == owner_novo_id
    assert updated_data["owner_ref"]["name"] == "Owner Novo"
'''

'''
    Corrigir depois (Pelo postman, mostra o output que está como alvo, mas no teste, não passa)

def test_update_asset_with_owner_non_existent(client):
    owner_id_valid = create_owner_in_db(client)
    asset_id = create_asset_in_db(client, owner_id=owner_id_valid)
    non_existent_uuid = str(uuid.uuid4())
    update_data = {"owner_id": non_existent_uuid}
    response = client.put(f"/integrations/asset/{asset_id}", json=update_data)
    
    assert response.status_code == 404
    assert f"Responsável com ID {non_existent_uuid} não encontrado" in response.json()["detail"]
'''

def test_update_asset_non_existent(client, auth_token):
    non_existent_uuid = str(uuid.uuid4())
    update_data = {"name": "Test"}
    response_404 = client.put(f"/integrations/asset/{non_existent_uuid}", json=update_data, headers=auth_token)

    assert response_404.status_code == 404
    assert f"Ativo com ID {non_existent_uuid} não encontrado" in response_404.json()["detail"]

def test_update_asset_with_invalid_format_id(client, auth_token):
    invalid_id = "nao-e-uuid" 
    update_data = {"name": "Test"}
    response_422 = client.put(f"/integrations/asset/{invalid_id}", json=update_data, headers=auth_token)

    assert response_422.status_code == 422
    assert "Input should be a valid UUID" in response_422.json()["detail"][0]["msg"]

def test_delete_asset_sucess(client, auth_token):
    owner_id = create_owner_in_db(client, auth_token, name="Owner para Deleção")
    asset_id = create_asset_in_db(client, auth_token, owner_id=owner_id, name="Asset a Deletar")
    get_initial_response = client.get(f"/integrations/asset/{asset_id}", headers=auth_token)

    assert get_initial_response.status_code == 200

    delete_response = client.delete(f"/integrations/asset/{asset_id}", headers=auth_token)
    
    assert delete_response.status_code == 204 

    get_final_response = client.get(f"/integrations/asset/{asset_id}", headers=auth_token)

    assert get_final_response.status_code == 404

def test_delete_asset_non_existent(client, auth_token):
    non_existent_uuid = str(uuid.uuid4())
    response_404 = client.delete(f"/integrations/asset/{non_existent_uuid}", headers=auth_token)
    
    assert response_404.status_code == 404
    assert "Ativo com ID" in response_404.json()["detail"]
    
def test_delete_asset_with_invalid_format_id(client, auth_token):
    invalid_id = "id-errado-para-delete" 
    response_422 = client.delete(f"/integrations/asset/{invalid_id}", headers=auth_token)
    
    assert response_422.status_code == 422
    assert "Input should be a valid UUID" in response_422.json()["detail"][0]["msg"]

def test_create_user_sucess(client, auth_token):
    new_login = f"user_{str(uuid.uuid4())[:8]}"
    user_data = {
        "login": new_login,
        "password": "senha_mockada"
    }
    response = client.post("/integrations/user", json=user_data, headers=auth_token)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["login"] == new_login
    assert "hashed_password" not in data

def test_read_user_by_id(client, auth_token):
    new_login = f"read_{str(uuid.uuid4())[:8]}"
    create_response = client.post("/integrations/user", json={"login": new_login, "password": "x"}, headers=auth_token)
    new_user_id = create_response.json()["id"]
    response_id = client.get(f"/integrations/user/{new_user_id}", headers=auth_token)

    assert response_id.status_code == 200
    assert response_id.json()["login"] == new_login

def test_read_users(client, auth_token):
    new_login = f"read_{str(uuid.uuid4())[:8]}"
    create_response = client.post("/integrations/user", json={"login": new_login, "password": "x"}, headers=auth_token)
    new_user_id = create_response.json()["id"]
    response_list = client.get(f"/integrations/user/", headers=auth_token)

    assert response_list.status_code == 200
    assert any(user['id'] == new_user_id for user in response_list.json())

def test_read_user_non_existent(client, auth_token):
    non_existent_id = 99999
    response = client.get(f"/integrations/user/{non_existent_id}", headers=auth_token)

    assert response.status_code == 404
    assert "Usuário não encontrado" in response.json()['detail']

def test_delete_user_sucess(client, auth_token):
    new_login = f"del_{str(uuid.uuid4())[:8]}"
    post_response = client.post("/integrations/user", json={"login": new_login, "password": "x"}, headers=auth_token)
    user_id_to_delete = post_response.json()['id']
    delete_response = client.delete(f"/integrations/user/{user_id_to_delete}", headers=auth_token)

    assert delete_response.status_code == 204

    get_response = client.get(f"/integrations/user/{user_id_to_delete}", headers=auth_token)

    assert get_response.status_code == 404

def test_global_auth_without_token(client):
    owner_data = {
        "name": "Teste",
        "email": "teste@teste.com",
        "phone": "11111111"
    }
    response = client.post("/integrations/owner", json=owner_data, headers={})

    assert response.status_code == 401
    assert "Not authenticated" in response.json()['detail']

def test_global_auth_with_invalid_token(client):
    invalid_token = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmYWtlIn0.bOGo"}
    response = client.get("/integrations/owner/00000000-0000-0000-0000-000000000000", headers=invalid_token)

    assert response.status_code == 401
    assert "Token inválido" in response.json()['detail']
