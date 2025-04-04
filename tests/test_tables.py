from fastapi.testclient import TestClient
from sqlmodel import Session

def test_create_table(client: TestClient):
    # First create an object schema
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
    object_id = response.json()["id"]
    
    # Test creating a table with that schema
    response = client.post(
        "/api/v1/tables/",
        json={
            "name": "users",
            "description": "Sample user data",
            "object_id": object_id,
            "data": [
                {
                    "name": "John Doe",
                    "age": 30,
                    "email": "john@example.com"
                }
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "users"
    assert data["description"] == "Sample user data"
    assert data["object_id"] == object_id
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == "John Doe"

def test_create_table_nonexistent_object(client: TestClient):
    # Test creating a table with non-existent object schema
    response = client.post(
        "/api/v1/tables/",
        json={
            "name": "invalid_table",
            "description": "Invalid table",
            "object_id": 999,  # Non-existent object ID
            "data": [{"value": "test"}]
        },
    )
    assert response.status_code == 404
    assert "Referenced object schema not found" in response.json()["detail"]

def test_create_table_invalid_schema(client: TestClient):
    # First create an object schema
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "user_data",
            "description": "User information schema",
            "attributes": {
                "name": "string",
                "age": "integer"
            }
        },
    )
    assert response.status_code == 200
    object_id = response.json()["id"]
    
    # Test creating a table with invalid data
    response = client.post(
        "/api/v1/tables/",
        json={
            "name": "users",
            "description": "Sample user data",
            "object_id": object_id,
            "data": [
                {
                    "name": "John Doe",
                    "age": 30,
                    "invalid_field": "value"  # Field not in schema
                }
            ]
        },
    )
    assert response.status_code == 400
    assert "Extra fields found in data" in response.json()["detail"]

def test_read_tables(client: TestClient):
    # First create an object schema
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "simple_data",
            "description": "Simple data schema",
            "attributes": {"value": "string"}
        },
    )
    assert response.status_code == 200
    object_id = response.json()["id"]
    
    # Create test tables
    for i in range(2):
        response = client.post(
            "/api/v1/tables/",
            json={
                "name": f"test_table_{i}",
                "description": f"Test table {i}",
                "object_id": object_id,
                "data": [{"value": f"test{i}"}]
            },
        )
        assert response.status_code == 200
    
    # Test reading all tables
    response = client.get("/api/v1/tables/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "test_table_0"
    assert data[1]["name"] == "test_table_1"
    
    # Test reading tables with object_id filter
    response = client.get(f"/api/v1/tables/?object_id={object_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(table["object_id"] == object_id for table in data)

def test_update_table(client: TestClient):
    # First create an object schema
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "user_data",
            "description": "User information schema",
            "attributes": {
                "name": "string",
                "age": "integer"
            }
        },
    )
    assert response.status_code == 200
    object_id = response.json()["id"]
    
    # Create a table
    response = client.post(
        "/api/v1/tables/",
        json={
            "name": "users",
            "description": "Sample user data",
            "object_id": object_id,
            "data": [
                {
                    "name": "John Doe",
                    "age": 30
                }
            ]
        },
    )
    assert response.status_code == 200
    table_id = response.json()["id"]
    
    # Test updating the table
    response = client.put(
        f"/api/v1/tables/{table_id}",
        json={
            "name": "updated_users",
            "description": "Updated user data",
            "object_id": object_id,
            "data": [
                {
                    "name": "Jane Doe",
                    "age": 25
                }
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_users"
    assert data["data"][0]["name"] == "Jane Doe"

def test_update_nonexistent_table(client: TestClient):
    # Test updating a non-existent table
    response = client.put(
        "/api/v1/tables/999",
        json={
            "name": "invalid_table",
            "description": "Invalid table",
            "object_id": 1,
            "data": []
        },
    )
    assert response.status_code == 404
    assert "Table not found" in response.json()["detail"]

def test_delete_table(client: TestClient):
    # First create an object schema
    response = client.post(
        "/api/v1/objects/",
        json={
            "name": "simple_data",
            "description": "Simple data schema",
            "attributes": {"value": "string"}
        },
    )
    assert response.status_code == 200
    object_id = response.json()["id"]
    
    # Create a table
    response = client.post(
        "/api/v1/tables/",
        json={
            "name": "test_table",
            "description": "Test table",
            "object_id": object_id,
            "data": [{"value": "test"}]
        },
    )
    assert response.status_code == 200
    table_id = response.json()["id"]
    
    # Test deleting the table
    response = client.delete(f"/api/v1/tables/{table_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    
    # Verify table is deleted
    response = client.get(f"/api/v1/tables/{table_id}")
    assert response.status_code == 404

def test_delete_nonexistent_table(client: TestClient):
    # Test deleting a non-existent table
    response = client.delete("/api/v1/tables/999")
    assert response.status_code == 404
    assert "Table not found" in response.json()["detail"]
