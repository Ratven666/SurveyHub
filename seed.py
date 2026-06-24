from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Group, Student, Subject, LabWork

def seed():
    with SessionLocal() as session:
        group1 = Group(name="MS-101")
        group2 = Group(name="MS-102")

        subj1 = Subject(name="Mine Surveying", description="Basic mine surveying course")
        subj2 = Subject(name="Geodesy", description="Geodetic foundations")
        subj3 = Subject(name="GIS", description="Introduction to GIS")

        subj1.lab_works = [
            LabWork(title="Traverse computation", order_number=1, description="Basic traverse"),
            LabWork(title="Leveling network", order_number=2, description="Leveling practice"),
        ]
        subj2.lab_works = [
            LabWork(title="Coordinate adjustment", order_number=1, description="Adjustment task"),
        ]
        subj3.lab_works = [
            LabWork(title="QGIS basics", order_number=1, description="Layers and styles"),
            LabWork(title="Spatial joins", order_number=2, description="Vector analysis"),
        ]

        group1.subjects.extend([subj1, subj2])
        group2.subjects.extend([subj1, subj3])

        students = [
            Student(full_name="Ivan Petrov", group=group1),
            Student(full_name="Anna Sidorova", group=group1),
            Student(full_name="Pavel Smirnov", group=group2),
        ]

        session.add_all([group1, group2, subj1, subj2, subj3, *students])
        session.commit()

if __name__ == "__main__":
    seed()
