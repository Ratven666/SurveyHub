from app.models.slots.lab_works_registrations import LabWorksRegistration
from app.models.slots.audience_slots import AudienceSlot
from app.models.slots.registration_equipment import RegistrationEquipment
from app.models.slots.student_registrations import StudentRegistration
from app.models.labs_subjects.equipment import Equipment
from app.models.labs_subjects.equipment_units import EquipmentUnit
from app.models.labs_subjects.lab_work import LabWork
from app.models.labs_subjects.lab_work_equipment import LabWorkEquipment
from app.models.labs_subjects.subject import Subject
from app.models.students.group import Group
from app.models.students.group_subject import group_subject_association
from app.models.students.student import Student
from app.models.teachers.teacher import Teacher
from app.models.teachers.teacher_assignment import TeacherAssignment

__all__ = [
    "AudienceSlot",
    "Equipment", "EquipmentUnit",
    "Group", "group_subject_association",
    "LabWork", "LabWorkEquipment",
    "LabWorksRegistration",
    "RegistrationEquipment",
    "Student", "StudentRegistration",
    "Subject", "Teacher", "TeacherAssignment",
]
