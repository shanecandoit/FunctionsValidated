from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ....models.object_schema import ObjectSchema
from ....core.database import get_session

router = APIRouter(prefix="/objects", tags=["objects"])

@router.post("/", response_model=ObjectSchema)
def create_object(*, session: Session = Depends(get_session), object: ObjectSchema):
    session.add(object)
    session.commit()
    session.refresh(object)
    return object

@router.get("/", response_model=List[ObjectSchema])
def read_objects(*, session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    objects = session.exec(select(ObjectSchema).offset(skip).limit(limit)).all()
    return objects

@router.get("/{object_id}", response_model=ObjectSchema)
def read_object(*, session: Session = Depends(get_session), object_id: int):
    object = session.get(ObjectSchema, object_id)
    if not object:
        raise HTTPException(status_code=404, detail="Object not found")
    return object
