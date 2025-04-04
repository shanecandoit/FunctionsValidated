from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import JSON
from .function_def import FunctionDef
from .table_data import TableData

class TestCase(SQLModel, table=True):
    __tablename__ = "test_cases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    
    # Reference to the function being tested
    function_id: int = Field(foreign_key="functions.id")
    
    # Maps of named inputs/outputs to table IDs
    input_tables: Dict[str, int] = Field(default_factory=dict, sa_type=JSON)  # Map of input name to table_id
    expected_output_tables: Dict[str, int] = Field(default_factory=dict, sa_type=JSON)  # Map of output name to table_id
    
    # Test parameters and configuration
    parameters: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    function: FunctionDef = Relationship()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "basic_transform_test",
                "description": "Tests basic data transformation",
                "function_id": 1,
                "input_tables": {"source": 1},  # table_id 1
                "expected_output_tables": {"result": 2},  # table_id 2
                "parameters": {"timeout": 30}
            }
        }
