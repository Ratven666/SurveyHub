from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import DbSession
from app.models import LabReport

router = APIRouter(prefix="/lab-reports", tags=["lab-reports"])

ReportStatus = Literal["pending", "submitted", "accepted", "rejected"]


class LabReportCreate(BaseModel):
    lab_registration_id: int
    status: ReportStatus = "pending"
    comment: str | None = None


class LabReportUpdate(BaseModel):
    status: ReportStatus | None = None
    comment: str | None = None


class LabReportRead(BaseModel):
    id: int
    lab_registration_id: int
    status: str
    comment: str | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[LabReportRead])
def list_lab_reports(
    db: DbSession,
    lab_registration_id: int | None = None,
    status: str | None = None,
):
    q = db.query(LabReport)
    if lab_registration_id is not None:
        q = q.filter(LabReport.lab_registration_id == lab_registration_id)
    if status is not None:
        q = q.filter(LabReport.status == status)
    return q.all()


@router.post("/", response_model=LabReportRead, status_code=201)
def create_lab_report(data: LabReportCreate, db: DbSession):
    report = LabReport(**data.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}", response_model=LabReportRead)
def get_lab_report(report_id: int, db: DbSession):
    report = db.get(LabReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="LabReport not found")
    return report


@router.patch("/{report_id}", response_model=LabReportRead)
def update_lab_report(report_id: int, data: LabReportUpdate, db: DbSession):
    report = db.get(LabReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="LabReport not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    db.commit()
    db.refresh(report)
    return report


@router.delete("/{report_id}", status_code=204)
def delete_lab_report(report_id: int, db: DbSession):
    report = db.get(LabReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="LabReport not found")
    db.delete(report)
    db.commit()
