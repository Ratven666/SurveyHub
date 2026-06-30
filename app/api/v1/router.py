# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1 import groups, students, subjects, teachers, lab_work_equipment
from app.api.v1 import lab_works, lab_registrations, lab_progress, lab_reports
from app.api.v1 import equipment, equipment_units
from app.api.v1 import audience_slots, audience_registrations
from app.api.v1 import teacher_assignments

api_router = APIRouter()

api_router.include_router(groups.router)
api_router.include_router(students.router)
api_router.include_router(subjects.router)
api_router.include_router(teachers.router)
api_router.include_router(teacher_assignments.router)
api_router.include_router(lab_works.router)
api_router.include_router(lab_registrations.router)
api_router.include_router(lab_progress.router)
api_router.include_router(lab_reports.router)
api_router.include_router(equipment.router)
api_router.include_router(equipment_units.router)
api_router.include_router(audience_slots.router)
api_router.include_router(audience_registrations.router)
api_router.include_router(lab_work_equipment.router)
