from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ....models.test_case import TestCase
from ....models.function_def import FunctionDef
from ....models.table_data import TableData
from ....core.database import get_session

router = APIRouter(prefix="/test-cases", tags=["test-cases"])


@router.post("/", response_model=TestCase)
def create_test_case(*, session: Session = Depends(get_session), test_case: TestCase):
    # Verify that the function exists
    function = session.get(FunctionDef, test_case.function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    
    # Verify that all input tables exist and match function schema
    for input_name, table_id in test_case.input_tables.items():
        if input_name not in function.input_schemas:
            raise HTTPException(
                status_code=400,
                detail=f"Input {input_name} not defined in function schema"
            )
        table = session.get(TableData, table_id)
        if not table:
            raise HTTPException(
                status_code=404,
                detail=f"Input table {input_name} (id: {table_id}) not found"
            )
        if table.object_id != function.input_schemas[input_name]:
            raise HTTPException(
                status_code=400,
                detail=f"Input table {input_name} schema does not match function definition"
            )
    
    # Verify that all expected output tables exist and match function schema
    for output_name, table_id in test_case.expected_output_tables.items():
        if output_name not in function.output_schemas:
            raise HTTPException(
                status_code=400,
                detail=f"Output {output_name} not defined in function schema"
            )
        table = session.get(TableData, table_id)
        if not table:
            raise HTTPException(
                status_code=404,
                detail=f"Expected output table {output_name} (id: {table_id}) not found"
            )
        if table.object_id != function.output_schemas[output_name]:
            raise HTTPException(
                status_code=400,
                detail=f"Expected output table {output_name} schema does not match function definition"
            )
    
    session.add(test_case)
    session.commit()
    session.refresh(test_case)
    return test_case

@router.get("/", response_model=List[TestCase])
def read_test_cases(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    function_id: Optional[int] = None,
    status: Optional[str] = None
):
    query = select(TestCase)
    if function_id:
        query = query.where(TestCase.function_id == function_id)
    if status:
        query = query.where(TestCase.last_status == status)
    test_cases = session.exec(query.offset(skip).limit(limit)).all()
    return test_cases

@router.get("/{test_case_id}", response_model=TestCase)
def read_test_case(*, session: Session = Depends(get_session), test_case_id: int):
    test_case = session.get(TestCase, test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case

@router.post("/{test_case_id}/run")
async def run_test(
    *,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    test_case_id: int
):
    test_case = session.get(TestCase, test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    # Queue the test to run in the background
    background_tasks.add_task(run_test_case, test_case_id, session)
    
    return {
        "message": "Test execution queued",
        "test_case_id": test_case_id
    }

@router.delete("/{test_case_id}")
def delete_test_case(*, session: Session = Depends(get_session), test_case_id: int):
    test_case = session.get(TestCase, test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    session.delete(test_case)
    session.commit()
    return {"ok": True}
