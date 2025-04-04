from fastapi.testclient import TestClient
from sqlmodel import Session

def test_create_function(client: TestClient):
    # First create input/output object schemas
    input_response = client.post(
        "/api/v1/objects/",
        json={
            "name": "input_data",
            "description": "Input schema",
            "attributes": {
                "value": "integer"
            }
        },
    )
    assert input_response.status_code == 200
    input_id = input_response.json()["id"]
    
    output_response = client.post(
        "/api/v1/objects/",
        json={
            "name": "output_data",
            "description": "Output schema",
            "attributes": {
                "result": "integer"
            }
        },
    )
    assert output_response.status_code == 200
    output_id = output_response.json()["id"]
    
    # Test creating a function
    response = client.post(
        "/api/v1/functions/",
        json={
            "name": "double_value",
            "description": "Doubles the input value",
            "input_schemas": {"value": input_id},
            "output_schemas": {"result": output_id},
            "parameters": {"timeout": 30}
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "double_value"
    assert "id" in data

def test_create_function_invalid_object_schema(client: TestClient):
    # Test creating a function with invalid object schema
    response = client.post(
        "/api/v1/functions/",
        json={
            "name": "invalid_function",
            "description": "Function with invalid object schema",
            "input_schemas": {"input": 999},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert response.status_code == 404
    assert "Input object schema with id 999 not found" in response.json()["detail"]
    
    response = client.post(
        "/api/v1/functions/",
        json={
            "name": "invalid_function",
            "description": "Function with invalid object schema",
            "input_schemas": {},
            "output_schemas": {"output": 999},
            "parameters": {}
        },
    )
    assert response.status_code == 404
    assert "Output object schema with id 999 not found" in response.json()["detail"]


def test_update_function_invalid_object_schema(client: TestClient):
    # Create a test function first
    create_response = client.post(
        "/api/v1/functions/",
        json={
            "name": "test_function",
            "description": "Test function",
            "input_schemas": {},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert create_response.status_code == 200
    function_id = create_response.json()["id"]
    
    # Test updating the function with invalid object schema
    response = client.put(
        f"/api/v1/functions/{function_id}",
        json={
            "name": "updated_function",
            "description": "Updated function",
            "input_schemas": {"input": 999},
            "output_schemas": {},
            "parameters": {"timeout": 60}
        },
    )
    assert response.status_code == 404
    assert "Input object schema with id 999 not found" in response.json()["detail"]
    
    response = client.put(
        f"/api/v1/functions/{function_id}",
        json={
            "name": "updated_function",
            "description": "Updated function",
            "input_schemas": {},
            "output_schemas": {"output": 999},
            "parameters": {"timeout": 60}
        },
    )
    assert response.status_code == 404
    assert "Output object schema with id 999 not found" in response.json()["detail"]


def test_create_function_no_description(client: TestClient):
    # Test creating a function without description
    response = client.post(
        "/api/v1/functions/",
        json={
            "name": "minimal_function",
            "input_schemas": {},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "minimal_function"
    assert data["description"] is None
    assert data["input_schemas"] == {}
    assert data["output_schemas"] == {}


def test_validate_nonexistent_function(client: TestClient):
    response = client.post("/api/v1/functions/999/validate")
    assert response.status_code == 404
    assert "Function not found" in response.json()["detail"]



def test_read_functions(client: TestClient):
    # Create test functions
    for i in range(2):
        response = client.post(
            "/api/v1/functions/",
            json={
                "name": f"test_function_{i}",
                "description": f"Test function {i}",
                "input_schemas": {},
                "output_schemas": {},
                "parameters": {}
            },
        )
        assert response.status_code == 200
    
    # Test reading all functions
    response = client.get("/api/v1/functions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "test_function_0"
    assert data[1]["name"] == "test_function_1"
    
    # Test pagination
    response = client.get("/api/v1/functions/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test_function_1"

def test_read_function(client: TestClient):
    # Create a test function
    response = client.post(
        "/api/v1/functions/",
        json={
            "name": "test_function",
            "description": "Test function",
            "input_schemas": {},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert response.status_code == 200
    function_id = response.json()["id"]
    
    # Test reading the function
    response = client.get(f"/api/v1/functions/{function_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_function"
    assert data["description"] == "Test function"


def test_read_nonexistent_function(client: TestClient):
    response = client.get("/api/v1/functions/999")
    assert response.status_code == 404
    assert "Function not found" in response.json()["detail"]


def test_update_nonexistent_function(client: TestClient):
    response = client.put(
        "/api/v1/functions/999",
        json={
            "name": "nonexistent",
            "description": "This function doesn't exist",
            "input_schemas": {},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert response.status_code == 404
    assert "Function not found" in response.json()["detail"]

def test_delete_function(client: TestClient):
    # Create a test function
    response = client.post(
        "/api/v1/functions/",
        json={
            "name": "test_function",
            "description": "Test function",
            "input_schemas": {},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert response.status_code == 200
    function_id = response.json()["id"]
    
    # Test deleting the function
    response = client.delete(f"/api/v1/functions/{function_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    
    # Verify function is deleted
    response = client.get(f"/api/v1/functions/{function_id}")
    assert response.status_code == 404


