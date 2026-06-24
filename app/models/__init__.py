from app.models.slots.audience_registrations import AudienceRegistration
from app.models.slots.audience_slots import AudienceSlot
from app.models.labs_subjects.equipment import Equipment
from app.models.labs_subjects.equipment_units import EquipmentUnit
from app.models.students.group import Group
from app.models.students.group_subject import group_subject_association
from app.models.students.lab_progress import LabProgress
from app.models.slots.lab_registrations import LabRegistration
from app.models.labs_subjects.lab_work import LabWork
from app.models.labs_subjects.lab_work_equipment import LabWorkEquipment
from app.models.students.student import Student
from app.models.labs_subjects.subject import Subject
from app.models.teachers.teacher import Teacher
from app.models.teachers.teacher_assignment import TeacherAssignment

__all__ = [
    "AudienceRegistration",
    "AudienceSlot",
    "Equipment",
    "EquipmentUnit",
    "Group",
    "LabProgress",
    "LabRegistration",
    "LabWork",
    "LabWorkEquipment",
    "Student",
    "Subject",
    "Teacher",
    "TeacherAssignment",
    "group_subject_association",
]
