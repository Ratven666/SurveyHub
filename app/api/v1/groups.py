from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import Group

router = APIRouter(prefix="/groups", tags=["groups"])


class GroupCreate(BaseModel):
    name: str


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
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("/{group_id}", response_model=GroupRead)
def get_group(group_id: int, db: DbSession):
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group
