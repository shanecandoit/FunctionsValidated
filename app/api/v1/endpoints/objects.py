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

@router.put("/{object_id}", response_model=ObjectSchema)
def update_object(*, session: Session = Depends(get_session), object_id: int, object_update: ObjectSchema):
    db_object = session.get(ObjectSchema, object_id)
    if not db_object:
        raise HTTPException(status_code=404, detail="Object not found")
    
    # Update object attributes
    for field, value in object_update.dict(exclude_unset=True).items():
        setattr(db_object, field, value)
    
    session.add(db_object)
    session.commit()
    session.refresh(db_object)
    return db_object

@router.delete("/{object_id}")
def delete_object(*, session: Session = Depends(get_session), object_id: int):
    object = session.get(ObjectSchema, object_id)
    if not object:
        raise HTTPException(status_code=404, detail="Object not found")
    
    session.delete(object)
    session.commit()
    return {"ok": True}
