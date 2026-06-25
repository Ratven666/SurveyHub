from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.deps import DbSession
from app.models import Group, group_subject_association

router = APIRouter(prefix="/groups", tags=["groups"])

class GroupCreate(BaseModel):
    name: str

class GroupUpdate(BaseModel):
    name: str | None = None

class GroupRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

@router.get("/", response_model=list[GroupRead])
def list_groups(db: DbSession):
    return db.query(Group).all()

@router.post("/", response_model=GroupRead, status_code=201)
def create_group(data: GroupCreate, db: DbSession):
    group = Group(name=data.name)
    db.add(group); db.commit(); db.refresh(group)
    return group

@router.get("/{group_id}", response_model=GroupRead)
def get_group(group_id: int, db: DbSession):
    group = db.get(Group, group_id)
    if not group: raise HTTPException(404, "Group not found")
    return group

@router.patch("/{group_id}", response_model=GroupRead)
def update_group(group_id: int, data: GroupUpdate, db: DbSession):
    group = db.get(Group, group_id)
    if not group: raise HTTPException(404, "Group not found")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(group, f, v)
    db.commit(); db.refresh(group)
    return group

@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: int, db: DbSession):
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    db.execute(
        group_subject_association.delete().where(
            group_subject_association.c.group_id == group_id
        )
    )
    db.flush()

    db.delete(group)
    db.commit()

