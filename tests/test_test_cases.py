from fastapi.testclient import TestClient
from sqlmodel import Session
import time


def test_create_test_case_with_invalid_function(client: TestClient):
    # Try to create a test case with non-existent input_tables
    response = client.post(
        "/api/v1/test-cases/",
        json={
            "name": "invalid_test",
            "description": "Test with invalid function",
            "function_id": 999,
            "input_tables": {},
            "expected_output_tables": {},
            "parameters": {}
        },
    )
    assert response.status_code == 404

def test_create_test_case_with_function_with_empty_input_tables(client: TestClient):
    # Try to create a test case with non-existent input_tables
    response = client.post(
        "/api/v1/test-cases/",
        json={
            "name": "invalid_test",
            "description": "Test with invalid function",
            "function_id": 999,
            "input_tables": {},
            "expected_output_tables": {},
            "parameters": {}
        },
    )
    assert response.status_code == 404

def test_create_test_case_with_invalid_input_table(client: TestClient):
    # Create an object schema with ID 1
    object_response = client.post(
        "/api/v1/objects/",
        json={
            "name": "dummy_object",
            "attributes": {"dummy": "string"}
        },
    )
    assert object_response.status_code == 200
    object_id = object_response.json()["id"]

    # Create a function first
    function_response = client.post(
        "/api/v1/functions/",
        json={
            "name": "simple_function",
            "input_schemas": {"input": object_id},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert function_response.status_code == 200
    function_id = function_response.json()["id"]
    
    # Create test case with non-existent input table
    response = client.post(
        "/api/v1/test-cases/",
        json={
            "name": "invalid_test",
            "description": "Test with invalid input table",
            "function_id": function_id,
            "input_tables": {"input": 999},  # Non-existent table ID
            "expected_output_tables": {},
            "parameters": {}
        },
    )
    assert response.status_code == 404
    assert "Input table input (id: 999) not found" in response.json()["detail"]

def test_create_test_case_with_schema_mismatch(client: TestClient):
    # Create two different object schemas
    schema1_response = client.post(
        "/api/v1/objects/",
        json={
            "name": "schema1",
            "attributes": {"value": "integer"}
        },
    )
    assert schema1_response.status_code == 200
    schema1_id = schema1_response.json()["id"]
    
    schema2_response = client.post(
        "/api/v1/objects/",
        json={
            "name": "schema2",
            "attributes": {"other": "string"}
        },
    )
    assert schema2_response.status_code == 200
    schema2_id = schema2_response.json()["id"]
    
    # Create a function using schema1
    function_response = client.post(
        "/api/v1/functions/",
        json={
            "name": "test_function",
            "input_schemas": {"x": schema1_id},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert function_response.status_code == 200
    function_id = function_response.json()["id"]
    
    # Create a table with schema2
    table_response = client.post(
        "/api/v1/tables/",
        json={
            "name": "wrong_schema_table",
            "object_id": schema2_id,
            "data": [{"other": "test"}]
        },
    )
    assert table_response.status_code == 200
    table_id = table_response.json()["id"]
    
    # Try to create a test case with mismatched schema
    response = client.post(
        "/api/v1/test-cases/",
        json={
            "name": "schema_mismatch_test",
            "description": "Test with schema mismatch",
            "function_id": function_id,
            "input_tables": {"x": table_id},
            "expected_output_tables": {},
            "parameters": {}
        },
    )
    assert response.status_code == 400
    assert "schema does not match" in response.json()["detail"]

def test_list_test_cases(client: TestClient):
    # Create a test case first
    function_response = client.post(
        "/api/v1/functions/",
        json={
            "name": "list_test_function",
            "input_schemas": {},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert function_response.status_code == 200
    function_id = function_response.json()["id"]
    
    test_case_response = client.post(
        "/api/v1/test-cases/",
        json={
            "name": "list_test",
            "function_id": function_id,
            "input_tables": {},
            "expected_output_tables": {},
            "parameters": {}
        },
    )
    assert test_case_response.status_code == 200
    
    # Test listing all test cases
    response = client.get("/api/v1/test-cases/")
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Test filtering by function ID
    response = client.get(f"/api/v1/test-cases/?function_id={function_id}")
    assert response.status_code == 200
    test_cases = response.json()
    assert len(test_cases) > 0
    assert all(tc["function_id"] == function_id for tc in test_cases)
    
    # Test pagination
    response = client.get("/api/v1/test-cases/?skip=0&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_run_nonexistent_test_case(client: TestClient):
    response = client.post("/api/v1/test-cases/999/run")
    assert response.status_code == 404
    assert "Test case not found" in response.json()["detail"]


def test_delete_test_case(client: TestClient):
    # Create a test case first
    function_response = client.post(
        "/api/v1/functions/",
        json={
            "name": "delete_test_function",
            "input_schemas": {},
            "output_schemas": {},
            "parameters": {}
        },
    )
    assert function_response.status_code == 200
    function_id = function_response.json()["id"]
    
    test_case_response = client.post(
        "/api/v1/test-cases/",
        json={
            "name": "delete_test",
            "function_id": function_id,
            "input_tables": {},
            "expected_output_tables": {},
            "parameters": {}
        },
    )
    assert test_case_response.status_code == 200
    test_case_id = test_case_response.json()["id"]
    
    # Delete the test case
    response = client.delete(f"/api/v1/test-cases/{test_case_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    
    # Verify it's deleted
    response = client.get(f"/api/v1/test-cases/{test_case_id}")
    assert response.status_code == 404

def test_delete_nonexistent_test_case(client: TestClient):
    response = client.delete("/api/v1/test-cases/999")
    assert response.status_code == 404
    assert "Test case not found" in response.json()["detail"]
