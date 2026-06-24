# from sqlalchemy import select
# from app.db.session import SessionLocal
# from app.models import Student
#
# with SessionLocal() as session:
#     stmt = select(Student).order_by(Student.full_name)
#     students = session.scalars(stmt).all()
#
#     for student in students:
#         print(student.full_name, student.group.name)

# from sqlalchemy import select
# from app.db.session import SessionLocal
# from app.models import Group
#
# with SessionLocal() as session:
#     stmt = select(Group).where(Group.name == "MS-101")
#     group = session.scalar(stmt)
#
#     if group:
#         for subject in group.subjects:
#             print(subject.name)


from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Subject

with SessionLocal() as session:
    stmt = select(Subject).where(Subject.name == "GIS")
    subject = session.scalar(stmt)

    if subject:
        for lab in sorted(subject.lab_works, key=lambda x: x.order_number):
            print(lab.order_number, lab.title)