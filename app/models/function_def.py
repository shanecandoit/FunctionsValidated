from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import JSON
from .object_schema import ObjectSchema

class FunctionDef(SQLModel, table=True):
    __tablename__ = "functions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    
    # Input/Output schema definitions
    input_schemas: Dict[str, int] = Field(default_factory=dict, sa_type=JSON)  # Map of input name to object_id
    output_schemas: Dict[str, int] = Field(default_factory=dict, sa_type=JSON)  # Map of output name to object_id
    
    # Function implementation details
    implementation_type: str = Field(default="python")  # e.g., "python", "sql", "external"
    implementation: str  # The actual implementation code
    parameters: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)  # Additional parameters/configuration
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "data_transform",
                "description": "Transforms input data according to specified rules",
                "input_schemas": {"source": 1},  # object_id 1
                "output_schemas": {"result": 2},  # object_id 2
                "implementation_type": "python",
                "implementation": "def process(source):\n    return {'result': transform(source)}",
                "parameters": {"validate_output": True}
            }
        }
