from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import JSON
from .object_schema import ObjectSchema

class TableData(SQLModel, table=True):
    __tablename__ = "tables"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    object_id: int = Field(foreign_key="objects.id")
    data: List[Dict[str, Any]] = Field(default_factory=list, sa_type=JSON)  # List of rows conforming to object schema
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to ObjectSchema
    object: ObjectSchema = Relationship()
