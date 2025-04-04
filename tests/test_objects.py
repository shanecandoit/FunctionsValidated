from fastapi.testclient import TestClient
from sqlmodel import Session

def test_create_object(client: TestClient):
    # Test creating a new object schema
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "user_data",
            "description": "User information schema",
            "attributes": {
                "name": "string",
                "age": "integer",
                "email": "string"
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "user_data"
    assert data["description"] == "User information schema"
    assert data["attributes"] == {
        "name": "string",
        "age": "integer",
        "email": "string"
    }
    assert "id" in data

def test_create_object_no_description(client: TestClient):
    # Test creating an object without description
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "minimal_object",
            "attributes": {
                "value": "string"
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "minimal_object"
    assert data["description"] is None
    assert data["attributes"] == {"value": "string"}

def test_read_objects(client: TestClient):
    # Create test objects
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "test_object_1",
            "description": "Test object 1",
            "attributes": {"field1": "string"}
        },
    )
    assert response.status_code == 200
    
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "test_object_2",
            "description": "Test object 2",
            "attributes": {"field2": "integer"}
        },
    )
    assert response.status_code == 200
    
    # Test reading all objects
    response = client.get("/api/v1/objects/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "test_object_1"
    assert data[1]["name"] == "test_object_2"
    
    # Test pagination
    response = client.get("/api/v1/objects/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test_object_2"

def test_read_object(client: TestClient):
    # Create a test object
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "test_object",
            "description": "Test object",
            "attributes": {"field": "string"}
        },
    )
    assert response.status_code == 200
    object_id = response.json()["id"]
    
    # Test reading the object
    response = client.get(f"/api/v1/objects/{object_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_object"
    assert data["description"] == "Test object"
    assert data["attributes"] == {"field": "string"}

def test_read_nonexistent_object(client: TestClient):
    response = client.get("/api/v1/objects/999")
    assert response.status_code == 404
    assert "Object not found" in response.json()["detail"]

def test_update_object(client: TestClient):
    # Create a test object
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "test_object",
            "description": "Test object",
            "attributes": {"field": "string"}
        },
    )
    assert response.status_code == 200
    object_id = response.json()["id"]
    
    # Test updating the object
    response = client.put(
        f"/api/v1/objects/{object_id}",
        json={
            "name": "updated_object",
            "description": "Updated object",
            "attributes": {
                "field": "string",
                "new_field": "integer"
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_object"
    assert data["description"] == "Updated object"
    assert data["attributes"] == {
        "field": "string",
        "new_field": "integer"
    }

def test_update_nonexistent_object(client: TestClient):
    response = client.put(
        "/api/v1/objects/999",
        json={
            "name": "nonexistent",
            "description": "This object doesn't exist",
            "attributes": {}
        },
    )
    assert response.status_code == 404
    assert "Object not found" in response.json()["detail"]

def test_delete_object(client: TestClient):
    # Create a test object
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "test_object",
            "description": "Test object",
            "attributes": {"field": "string"}
        },
    )
    assert response.status_code == 200
    object_id = response.json()["id"]
    
    # Test deleting the object
    response = client.delete(f"/api/v1/objects/{object_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    
    # Verify object is deleted
    response = client.get(f"/api/v1/objects/{object_id}")
    assert response.status_code == 404

def test_delete_nonexistent_object(client: TestClient):
    response = client.delete("/api/v1/objects/999")
    assert response.status_code == 404
    assert "Object not found" in response.json()["detail"]
