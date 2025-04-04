from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from ....models.function_def import FunctionDef
from ....models.object_schema import ObjectSchema
from ....core.database import get_session

router = APIRouter(prefix="/functions", tags=["functions"])

@router.post("/", response_model=FunctionDef)
def create_function(*, session: Session = Depends(get_session), function: FunctionDef):
    # Verify that all referenced object schemas exist
    for input_obj_id in function.input_schemas.values():
        if not session.get(ObjectSchema, input_obj_id):
            raise HTTPException(
                status_code=404,
                detail=f"Input object schema with id {input_obj_id} not found"
            )
    
    for output_obj_id in function.output_schemas.values():
        if not session.get(ObjectSchema, output_obj_id):
            raise HTTPException(
                status_code=404,
                detail=f"Output object schema with id {output_obj_id} not found"
            )
    
    
    session.add(function)
    session.commit()
    session.refresh(function)
    return function

@router.get("/", response_model=List[FunctionDef])
def read_functions(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    query = select(FunctionDef)
    functions = session.exec(query.offset(skip).limit(limit)).all()
    return functions

@router.get("/{function_id}", response_model=FunctionDef)
def read_function(*, session: Session = Depends(get_session), function_id: int):
    function = session.get(FunctionDef, function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    return function

@router.put("/{function_id}", response_model=FunctionDef)
def update_function(
    *,
    session: Session = Depends(get_session),
    function_id: int,
    function_update: FunctionDef
):
    function = session.get(FunctionDef, function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    
    # Verify that all referenced object schemas exist
    for input_obj_id in function_update.input_schemas.values():
        if not session.get(ObjectSchema, input_obj_id):
            raise HTTPException(
                status_code=404,
                detail=f"Input object schema with id {input_obj_id} not found"
            )
    
    for output_obj_id in function_update.output_schemas.values():
        if not session.get(ObjectSchema, output_obj_id):
            raise HTTPException(
                status_code=404,
                detail=f"Output object schema with id {output_obj_id} not found"
            )
    
    # Update function attributes
    function_data = function_update.dict(exclude_unset=True)
    for key, value in function_data.items():
        setattr(function, key, value)
    
    session.add(function)
    session.commit()
    session.refresh(function)
    return function

@router.delete("/{function_id}")
def delete_function(*, session: Session = Depends(get_session), function_id: int):
    function = session.get(FunctionDef, function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    
    session.delete(function)
    session.commit()
    return {"ok": True}

@router.post("/{function_id}/validate")
def validate_function(*, session: Session = Depends(get_session), function_id: int):
    """Validate function implementation and schema compatibility"""
    function = session.get(FunctionDef, function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    
    # A Function needs a name
    if not function.name:
        raise HTTPException(status_code=400, detail="Function name is required")
    
    # A Function needs a description
    if not function.description:
        raise HTTPException(status_code=400, detail="Function description is required")
    
    # A Function needs at least one input schema
    if not function.input_schemas:
        raise HTTPException(status_code=400, detail="Function needs at least one input schema")
    
    # A Function needs at least one output schema
    if not function.output_schemas:
        raise HTTPException(status_code=400, detail="Function needs at least one output schema")
    
