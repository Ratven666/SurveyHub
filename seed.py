"""
seed.py — заполнение БД тестовыми данными.

Запуск:   python seed.py
Повторный запуск безопасен: данные уже существуют → выходим с сообщением.
"""

from app.db.session import SessionLocal
from app.models import (
    AudienceRegistration,
    AudienceSlot,
    Equipment,
    EquipmentUnit,
    Group,
    LabProgress,
    LabRegistration,
    LabReport,
    LabWork,
    LabWorkEquipment,
    Student,
    Subject,
    Teacher,
    TeacherAssignment,
)


# ─────────────────────────────────────────────────────────────────────────────
# Вспомогательные функции
# ─────────────────────────────────────────────────────────────────────────────

def _already_seeded(session) -> bool:
    """Возвращает True, если в БД уже есть хотя бы одна группа."""
    return session.query(Group).first() is not None


# ─────────────────────────────────────────────────────────────────────────────
# Главная функция
# ─────────────────────────────────────────────────────────────────────────────

def seed() -> None:
    with SessionLocal() as session:
        if _already_seeded(session):
            print("Seed skipped: database already contains data.")
            return

        # ── Группы ────────────────────────────────────────────────────────────
        group_ms101 = Group(name="MS-101")
        group_ms102 = Group(name="MS-102")
        session.add_all([group_ms101, group_ms102])
        session.flush()  # получаем id до создания зависимых объектов

        # ── Предметы ──────────────────────────────────────────────────────────
        subj_surveying = Subject(
            name="Mine Surveying",
            description="Basic mine surveying course",
            training_direction="21.05.04",
        )
        subj_geodesy = Subject(
            name="Geodesy",
            description="Geodetic foundations",
            training_direction="21.05.04",
        )
        subj_gis = Subject(
            name="GIS",
            description="Introduction to GIS",
            training_direction="21.05.04",
        )
        session.add_all([subj_surveying, subj_geodesy, subj_gis])
        session.flush()

        # ── M2M: группа ↔ предмет ─────────────────────────────────────────────
        group_ms101.subjects.extend([subj_surveying, subj_geodesy])
        group_ms102.subjects.extend([subj_surveying, subj_gis])
        session.flush()

        # ── Преподаватели ─────────────────────────────────────────────────────
        teacher_ivanov = Teacher(
            last_name="Ivanov",
            first_name="Sergey",
            middle_name="Petrovich",
            email="ivanov@univ.ru",
            department="Mine Surveying Dept.",
            position="Associate Professor",
        )
        teacher_kuznetsova = Teacher(
            last_name="Kuznetsova",
            first_name="Elena",
            middle_name="Vladimirovna",
            email="kuznetsova@univ.ru",
            department="Geodesy Dept.",
            position="Senior Lecturer",
        )
        session.add_all([teacher_ivanov, teacher_kuznetsova])
        session.flush()

        # ── Назначения преподавателей ─────────────────────────────────────────
        session.add_all([
            TeacherAssignment(
                teacher=teacher_ivanov, group=group_ms101, subject=subj_surveying
            ),
            TeacherAssignment(
                teacher=teacher_ivanov, group=group_ms102, subject=subj_surveying
            ),
            TeacherAssignment(
                teacher=teacher_kuznetsova, group=group_ms101, subject=subj_geodesy
            ),
            TeacherAssignment(
                teacher=teacher_kuznetsova, group=group_ms102, subject=subj_gis
            ),
        ])
        session.flush()

        # ── Оборудование ──────────────────────────────────────────────────────
        equip_level = Equipment(
            name="Digital Level",
            description="Leica NA730 digital leveling instrument",
        )
        equip_total = Equipment(
            name="Total Station",
            description="Leica TS06 5'' total station",
        )
        equip_gnss = Equipment(
            name="GNSS Receiver",
            description="Trimble R8s GNSS receiver",
        )
        session.add_all([equip_level, equip_total, equip_gnss])
        session.flush()

        # ── Экземпляры оборудования ───────────────────────────────────────────
        session.add_all([
            EquipmentUnit(
                equipment=equip_level,
                name="Нивелир №1",
                serial_number="SN-LVL-001",
                inventory_number="INV-2024-001",
                status="working",
            ),
            EquipmentUnit(
                equipment=equip_level,
                name="Нивелир №2",
                serial_number="SN-LVL-002",
                inventory_number="INV-2024-002",
                status="working",
            ),
            EquipmentUnit(
                equipment=equip_total,
                name="Тахеометр №1",
                serial_number="SN-TS-001",
                inventory_number="INV-2024-003",
                status="working",
            ),
            EquipmentUnit(
                equipment=equip_total,
                name="Тахеометр №2",
                serial_number="SN-TS-002",
                inventory_number="INV-2024-004",
                status="repair",  # намеренно — для проверки фильтров
            ),
            EquipmentUnit(
                equipment=equip_gnss,
                name="GNSS-приёмник №1",
                serial_number="SN-GPS-001",
                inventory_number="INV-2024-005",
                status="working",
            ),
        ])
        session.flush()

        # ── Лабораторные работы ───────────────────────────────────────────────
        lw_traverse = LabWork(
            title="Traverse computation",
            order_number=1,
            description="Calculation and adjustment of a closed traverse",
            subject=subj_surveying,
            required_seat_type="desk",
            min_students=1, max_students=2,
            hours_to_complete=2,
        )
        lw_leveling = LabWork(
            title="Leveling network",
            order_number=2,
            description="Field leveling practice using digital levels",
            subject=subj_surveying,
            required_seat_type="device",
            min_students=2, max_students=3,
            hours_to_complete=4,
        )
        lw_adjustment = LabWork(
            title="Coordinate adjustment",
            order_number=1,
            description="Least squares adjustment of geodetic network",
            subject=subj_geodesy,
            required_seat_type="desk",
            min_students=1, max_students=1,
            hours_to_complete=2,
        )
        lw_qgis = LabWork(
            title="QGIS basics",
            order_number=1,
            description="Working with layers, styles, and attribute tables",
            subject=subj_gis,
            required_seat_type="device",
            min_students=1, max_students=1,
            hours_to_complete=2,
        )
        lw_joins = LabWork(
            title="Spatial joins",
            order_number=2,
            description="Vector analysis and spatial join operations",
            subject=subj_gis,
            required_seat_type="device",
            min_students=1, max_students=1,
            hours_to_complete=2,
        )
        session.add_all([lw_traverse, lw_leveling, lw_adjustment, lw_qgis, lw_joins])
        session.flush()

        # ── Привязка оборудования к лаб. работам ──────────────────────────────
        session.add_all([
            LabWorkEquipment(lab_work=lw_leveling, equipment=equip_level, required_units=1),
            LabWorkEquipment(lab_work=lw_leveling, equipment=equip_total, required_units=1),
            LabWorkEquipment(lab_work=lw_adjustment, equipment=equip_gnss, required_units=1),
        ])
        session.flush()

        # ── Студенты ──────────────────────────────────────────────────────────
        petrov = Student(
            last_name="Petrov", first_name="Ivan", middle_name="Alexandrovich",
            student_card_number="SC-2024-001", chip_card_number="CHIP-001",
            group=group_ms101,
        )
        sidorova = Student(
            last_name="Sidorova", first_name="Anna", middle_name="Dmitrievna",
            student_card_number="SC-2024-002", chip_card_number="CHIP-002",
            group=group_ms101,
        )
        smirnov = Student(
            last_name="Smirnov", first_name="Pavel", middle_name="Nikolaevich",
            student_card_number="SC-2024-003", chip_card_number="CHIP-003",
            group=group_ms102,
        )
        kozlov = Student(
            last_name="Kozlov", first_name="Dmitry", middle_name="Igorevich",
            student_card_number="SC-2024-004", chip_card_number="CHIP-004",
            group=group_ms102,
        )
        session.add_all([petrov, sidorova, smirnov, kozlov])
        session.flush()

        # ── Слоты аудиторий ───────────────────────────────────────────────────
        # weekday: 1=Пн, 2=Вт, 3=Ср, 4=Чт, 5=Пт   |   pair: 1..5
        slot_mon_p1 = AudienceSlot(weekday=1, pair_number=1, desk_capacity=20, device_capacity=10)
        slot_mon_p2 = AudienceSlot(weekday=1, pair_number=2, desk_capacity=20, device_capacity=10)
        slot_wed_p3 = AudienceSlot(weekday=3, pair_number=3, desk_capacity=15, device_capacity=5)
        slot_thu_p2 = AudienceSlot(weekday=4, pair_number=2, desk_capacity=15, device_capacity=8)
        session.add_all([slot_mon_p1, slot_mon_p2, slot_wed_p3, slot_thu_p2])
        session.flush()

        # ── Записи в аудиторию ────────────────────────────────────────────────
        session.add_all([
            AudienceRegistration(student=petrov,   slot=slot_mon_p1, seat_type="desk"),
            AudienceRegistration(student=sidorova, slot=slot_mon_p1, seat_type="desk"),
            AudienceRegistration(student=smirnov,  slot=slot_wed_p3, seat_type="device"),
            AudienceRegistration(student=kozlov,   slot=slot_wed_p3, seat_type="device"),
        ])
        session.flush()

        # ── Записи на лабораторные работы ─────────────────────────────────────
        reg_petrov_traverse   = LabRegistration(student=petrov,   lab_work=lw_traverse,  audience_slot=slot_mon_p1, status="approved")
        reg_sidorova_traverse = LabRegistration(student=sidorova, lab_work=lw_traverse,  audience_slot=slot_mon_p1, status="approved")
        reg_petrov_leveling   = LabRegistration(student=petrov,   lab_work=lw_leveling,  audience_slot=slot_mon_p2, status="pending")
        reg_smirnov_qgis      = LabRegistration(student=smirnov,  lab_work=lw_qgis,      audience_slot=slot_wed_p3, status="approved")
        reg_kozlov_qgis       = LabRegistration(student=kozlov,   lab_work=lw_qgis,      audience_slot=slot_wed_p3, status="approved")
        reg_smirnov_joins     = LabRegistration(student=smirnov,  lab_work=lw_joins,     audience_slot=slot_thu_p2, status="pending")
        session.add_all([
            reg_petrov_traverse, reg_sidorova_traverse, reg_petrov_leveling,
            reg_smirnov_qgis, reg_kozlov_qgis, reg_smirnov_joins,
        ])
        session.flush()

        # ── Прогресс выполнения ───────────────────────────────────────────────
        session.add_all([
            LabProgress(lab_registration=reg_petrov_traverse,   status="defended",    note="Защищена на отлично."),
            LabProgress(lab_registration=reg_sidorova_traverse, status="submitted",   note="Отчёт сдан, ожидает проверки."),
            LabProgress(lab_registration=reg_smirnov_qgis,      status="in_progress", note=None),
        ])
        session.flush()

        # ── Отчёты ────────────────────────────────────────────────────────────
        session.add_all([
            LabReport(lab_registration=reg_petrov_traverse,   status="accepted",  comment="Все расчёты верны. Оценка: отлично."),
            LabReport(lab_registration=reg_sidorova_traverse, status="submitted", comment=None),
        ])

        session.commit()
        print("Seed completed successfully.")
        print(f"  Groups:    {session.query(Group).count()}")
        print(f"  Subjects:  {session.query(Subject).count()}")
        print(f"  Teachers:  {session.query(Teacher).count()}")
        print(f"  Students:  {session.query(Student).count()}")
        print(f"  LabWorks:  {session.query(LabWork).count()}")
        print(f"  Slots:     {session.query(AudienceSlot).count()}")
        print(f"  LabRegs:   {session.query(LabRegistration).count()}")


if __name__ == "__main__":
    seed()