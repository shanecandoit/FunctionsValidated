from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from ....models.table_data import TableData
from ....models.object_schema import ObjectSchema
from ....core.database import get_session
from pydantic import ValidationError
import json

router = APIRouter(prefix="/tables", tags=["tables"])

@router.post("/", response_model=TableData)
def create_table(*, session: Session = Depends(get_session), table: TableData):
    # Verify that the referenced object exists
    object_schema = session.get(ObjectSchema, table.object_id)
    if not object_schema:
        raise HTTPException(status_code=404, detail="Referenced object schema not found")
    
    # Validate data against the object schema
    try:
        for row in table.data:
            # Here you would validate each row against the object schema
            # This is a basic implementation - you might want to add more validation
            for field, value in row.items():
                if field not in object_schema.attributes:
                    raise ValidationError(f"Field {field} not in schema attributes")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    session.add(table)
    session.commit()
    session.refresh(table)
    return table

@router.get("/", response_model=List[TableData])
def read_tables(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    object_id: Optional[int] = None
):
    query = select(TableData)
    if object_id:
        query = query.where(TableData.object_id == object_id)
    tables = session.exec(query.offset(skip).limit(limit)).all()
    return tables

@router.get("/{table_id}", response_model=TableData)
def read_table(*, session: Session = Depends(get_session), table_id: int):
    table = session.get(TableData, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@router.put("/{table_id}", response_model=TableData)
def update_table(*, session: Session = Depends(get_session), table_id: int, table_update: TableData):
    table = session.get(TableData, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Verify that the referenced object exists
    object_schema = session.get(ObjectSchema, table_update.object_id)
    if not object_schema:
        raise HTTPException(status_code=404, detail="Referenced object schema not found")
    
    # Validate data against the object schema
    try:
        for row in table_update.data:
            for field, value in row.items():
                if field not in object_schema.attributes:
                    raise ValidationError(f"Field {field} not in schema attributes")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Update table attributes
    table_data = table_update.dict(exclude_unset=True)
    for key, value in table_data.items():
        setattr(table, key, value)
    
    session.add(table)
    session.commit()
    session.refresh(table)
    return table

@router.delete("/{table_id}")
def delete_table(*, session: Session = Depends(get_session), table_id: int):
    table = session.get(TableData, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    session.delete(table)
    session.commit()
    return {"ok": True}
