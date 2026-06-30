"""
seed.py — заполнение БД тестовыми данными для SurveyHub.

Запуск:
    python seed.py                                             # sqlite
    DATABASE_URL=postgresql+psycopg2://u:p@localhost/db python seed.py

Идемпотентен: повторный запуск не создаёт дублей.
"""
from __future__ import annotations

import logging
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.base import Base
from app.models import (
    AudienceSlot,
    Equipment,
    EquipmentUnit,
    Group,
    LabWork,
    LabWorkEquipment,
    LabWorksRegistration,
    RegistrationEquipment,
    Student,
    StudentRegistration,
    Subject,
    Teacher,
    TeacherAssignment,
    group_subject_association,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("seed")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)


# ──────────────────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_or_create(session: Session, model, defaults: dict | None = None, **kwargs):
    obj = session.query(model).filter_by(**kwargs).first()
    if obj:
        return obj, False
    obj = model(**{**kwargs, **(defaults or {})})
    session.add(obj)
    session.flush()
    return obj, True


# ──────────────────────────────────────────────────────────────────────────────
# sections
# ──────────────────────────────────────────────────────────────────────────────

def seed_groups(session: Session) -> list[Group]:
    groups = []
    for name in ["ГИС-21", "ГИС-22", "ИВТ-21"]:
        g, created = _get_or_create(session, Group, name=name)
        if created:
            log.info("  + Group: %s", name)
        groups.append(g)
    return groups


def seed_subjects(session: Session) -> list[Subject]:
    data = [
        ("Геоинформационные системы",      "Теория и практика работы с ГИС",          "09.03.02"),
        ("Дистанционное зондирование Земли","Обработка спутниковых снимков",            "09.03.02"),
        ("Геодезия",                        "Методы полевых геодезических измерений",  "21.03.03"),
    ]
    subjects = []
    for name, desc, direction in data:
        s, created = _get_or_create(
            session, Subject,
            name=name, description=desc, training_direction=direction,
        )
        if created:
            log.info("  + Subject: %s", name)
        subjects.append(s)
    return subjects


def seed_teachers(session: Session) -> list[Teacher]:
    data = [
        ("Иванов",   "Пётр",  "Сергеевич",   "ivanov@edu.ru",   "Кафедра ГИС", "Доцент"),
        ("Сидорова", "Анна",  "Владимировна", "sidorova@edu.ru", "Кафедра ГИС", "Старший преподаватель"),
    ]
    teachers = []
    for last, first, middle, email, dept, pos in data:
        t, created = _get_or_create(
            session, Teacher, email=email,
            defaults=dict(last_name=last, first_name=first, middle_name=middle,
                          department=dept, position=pos),
        )
        if created:
            log.info("  + Teacher: %s %s", last, first)
        teachers.append(t)
    return teachers


def seed_equipment(session: Session) -> tuple[list[Equipment], list[EquipmentUnit]]:
    catalog = [
        ("Нивелир Leica NA720", "Оптический нивелир", [
            ("Нивелир №1", "LEI-001", "INV-0001"),
            ("Нивелир №2", "LEI-002", "INV-0002"),
            ("Нивелир №3", "LEI-003", "INV-0003"),
        ]),
        ("Тахеометр Sokkia CX-105", "Электронный тахеометр", [
            ("Тахеометр №1", "SOK-001", "INV-0010"),
            ("Тахеометр №2", "SOK-002", "INV-0011"),
        ]),
        ("GPS-приёмник Trimble R2", "GNSS-приёмник", [
            ("GPS №1", "TRM-001", "INV-0020"),
        ]),
    ]
    all_eq, all_units = [], []
    for eq_name, eq_desc, units in catalog:
        eq, created = _get_or_create(session, Equipment, name=eq_name,
                                     defaults={"description": eq_desc})
        if created:
            log.info("  + Equipment: %s", eq_name)
        all_eq.append(eq)
        for u_name, serial, inv in units:
            unit, u_created = _get_or_create(
                session, EquipmentUnit, serial_number=serial,
                defaults=dict(equipment_id=eq.id, name=u_name,
                              inventory_number=inv, status="working"),
            )
            if u_created:
                log.info("    + EquipmentUnit: %s", u_name)
            all_units.append(unit)
    return all_eq, all_units


def seed_students(session: Session, groups: list[Group]) -> list[Student]:
    rows = [
        # g_idx, last, first, middle, card, chip
        (0, "Петров",    "Алексей",    "Михайлович",    "СТ-2021-001", "CHIP-001"),
        (0, "Кузнецова", "Мария",      "Андреевна",     "СТ-2021-002", "CHIP-002"),
        (0, "Васильев",  "Дмитрий",   "Олегович",      "СТ-2021-003", "CHIP-003"),
        (1, "Морозова",  "Екатерина", "Сергеевна",     "СТ-2022-001", "CHIP-004"),
        (1, "Новиков",   "Иван",       "Павлович",      "СТ-2022-002", "CHIP-005"),
        (1, "Лебедева",  "Ольга",      "Викторовна",    "СТ-2022-003", "CHIP-006"),
        (2, "Соколов",   "Артём",      "Игоревич",      "СТ-2021-101", "CHIP-007"),
        (2, "Попова",    "Наталья",   "Дмитриевна",    "СТ-2021-102", "CHIP-008"),
        (2, "Фёдоров",   "Никита",    "Александрович", "СТ-2021-103", "CHIP-009"),
    ]
    students = []
    for g_idx, last, first, middle, card, chip in rows:
        s, created = _get_or_create(
            session, Student, student_card_number=card,
            defaults=dict(last_name=last, first_name=first, middle_name=middle,
                          chip_card_number=chip, group_id=groups[g_idx].id),
        )
        if created:
            log.info("  + Student: %s %s", last, first)
        students.append(s)
    return students


def seed_group_subject_links(session, groups, subjects) -> None:
    links = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2)]
    for g_idx, s_idx in links:
        if subjects[s_idx] not in groups[g_idx].subjects:
            groups[g_idx].subjects.append(subjects[s_idx])
            log.info("  + GroupSubject: %s → %s",
                     groups[g_idx].name, subjects[s_idx].name)
    session.flush()


def seed_teacher_assignments(session, teachers, groups, subjects):
    rows = [(0, 0, 0), (0, 1, 0), (1, 0, 1), (1, 2, 2)]
    assignments = []
    for t_i, g_i, s_i in rows:
        ta, created = _get_or_create(
            session, TeacherAssignment,
            teacher_id=teachers[t_i].id,
            group_id=groups[g_i].id,
            subject_id=subjects[s_i].id,
        )
        if created:
            log.info("  + TeacherAssignment: %s → %s / %s",
                     teachers[t_i].last_name, groups[g_i].name, subjects[s_i].name)
        assignments.append(ta)
    return assignments


def seed_lab_works(session, subjects, all_eq) -> list[LabWork]:
    rows = [
        # s_idx, order, title, seat_type, min_s, max_s, hours
        (0, 1, "Введение в QGIS. Интерфейс и базовые операции",  "device", 1, 1, 2),
        (0, 2, "Работа с векторными слоями и атрибутами",         "device", 1, 2, 2),
        (0, 3, "Пространственный анализ. Оверлейные операции",    "device", 1, 2, 4),
        (1, 1, "Загрузка и визуализация растровых снимков",        "device", 1, 1, 2),
        (1, 2, "Классификация объектов на снимке",                 "device", 1, 2, 4),
        (2, 1, "Нивелирование трассы замкнутого хода",            "desk",   2, 3, 4),
        (2, 2, "Тахеометрическая съёмка участка",                 "desk",   2, 3, 4),
    ]
    eq_map = {
        (2, 1): [(0, 2)],
        (2, 2): [(1, 1)],
    }
    lab_works = []
    for s_idx, order, title, seat_type, min_s, max_s, hours in rows:
        lw, created = _get_or_create(
            session, LabWork,
            subject_id=subjects[s_idx].id, order_number=order,
            defaults=dict(title=title, required_seat_type=seat_type,
                          min_students=min_s, max_students=max_s,
                          hours_to_complete=hours),
        )
        if created:
            log.info("  + LabWork [%s] #%d: %s", subjects[s_idx].name, order, title)
        if created and (s_idx, order) in eq_map:
            for eq_idx, req in eq_map[(s_idx, order)]:
                lwe = LabWorkEquipment(
                    lab_work_id=lw.id,
                    equipment_id=all_eq[eq_idx].id,
                    required_units=req,
                )
                session.add(lwe)
                session.flush()
                log.info("    + LabWorkEquipment: %s ×%d", all_eq[eq_idx].name, req)
        lab_works.append(lw)
    return lab_works


def seed_audience_slots(session) -> list[AudienceSlot]:
    rows = [
        # audience_number, weekday, pair, desk, device
        ("301А",  1, 1, 15, 10),
        ("301А",  1, 2, 15, 10),
        ("301А",  3, 1, 15, 10),
        ("Б-201", 1, 3,  0, 20),
        ("Б-201", 2, 2,  0, 20),
        ("205",   2, 1, 20,  0),
        ("205",   4, 1, 20,  0),
    ]
    slots = []
    for audience_number, weekday, pair, desk, device in rows:
        s, created = _get_or_create(
            session, AudienceSlot,
            audience_number=audience_number, weekday=weekday, pair_number=pair,
            defaults=dict(desk_capacity=desk, device_capacity=device),
        )
        if created:
            log.info("  + AudienceSlot: %s день=%d пара=%d (столы=%d, ПК=%d)",
                     audience_number, weekday, pair, desk, device)
        slots.append(s)
    return slots


def seed_lab_works_registrations(
    session, slots, lab_works, students, all_units,
) -> None:
    """
    reg_0 — слот 301А пн.1, ГИС Л1 (device)
             создатель: Петров; участники: Петров (confirmed) + Кузнецова (pending)

    reg_1 — слот Б-201 вт.2, ДЗЗ Л1 (device)
             создатель: Морозова; участники: Морозова + Новиков (оба confirmed)

    reg_2 — слот 205 вт.1, Геодезия Л1 (desk)
             создатель: Соколов; участники: Соколов + Попова + Фёдоров
             оборудование: Нивелир №1, Нивелир №2
    """

    def _make_reg(slot, lab_work, creator, seat_type, status,
                  participants, units=None):
        existing = (
            session.query(LabWorksRegistration)
            .filter_by(slot_id=slot.id, lab_work_id=lab_work.id)
            .first()
        )
        if existing:
            return
        reg = LabWorksRegistration(
            slot_id=slot.id,
            lab_work_id=lab_work.id,
            creator_id=creator.id,
            seat_type=seat_type,
            status=status,
        )
        session.add(reg)
        session.flush()
        for student, st_status in participants:
            session.add(StudentRegistration(
                student_id=student.id,
                lab_works_registration_id=reg.id,
                status=st_status,
            ))
        if units:
            for unit in units:
                session.add(RegistrationEquipment(
                    lab_works_registration_id=reg.id,
                    equipment_unit_id=unit.id,
                ))
        session.flush()
        log.info(
            "  + LabWorksRegistration #%d: %s → %s (%d участников%s)",
            reg.id, slot.audience_number, lab_work.title,
            len(participants),
            f", {len(units)} ед. оборудования" if units else "",
        )

    _make_reg(
        slot=slots[0], lab_work=lab_works[0],
        creator=students[0], seat_type="device", status="pending",
        participants=[(students[0], "confirmed"), (students[1], "pending")],
    )
    _make_reg(
        slot=slots[4], lab_work=lab_works[3],
        creator=students[3], seat_type="device", status="confirmed",
        participants=[(students[3], "confirmed"), (students[4], "confirmed")],
    )
    _make_reg(
        slot=slots[5], lab_work=lab_works[5],
        creator=students[6], seat_type="desk", status="pending",
        participants=[
            (students[6], "confirmed"),
            (students[7], "pending"),
            (students[8], "pending"),
        ],
        units=all_units[:2],  # Нивелир №1, Нивелир №2
    )


# ──────────────────────────────────────────────────────────────────────────────
# main
# ──────────────────────────────────────────────────────────────────────────────

def run() -> None:
    log.info("=== SurveyHub seed start | %s ===", DATABASE_URL)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        try:
            log.info("-- groups")
            groups = seed_groups(session)
            log.info("-- subjects")
            subjects = seed_subjects(session)
            log.info("-- teachers")
            teachers = seed_teachers(session)
            log.info("-- equipment + units")
            all_eq, all_units = seed_equipment(session)
            log.info("-- students")
            students = seed_students(session, groups)
            log.info("-- group ↔ subject links")
            seed_group_subject_links(session, groups, subjects)
            log.info("-- teacher assignments")
            seed_teacher_assignments(session, teachers, groups, subjects)
            log.info("-- lab works")
            lab_works = seed_lab_works(session, subjects, all_eq)
            log.info("-- audience slots")
            slots = seed_audience_slots(session)
            log.info("-- lab works registrations")
            seed_lab_works_registrations(session, slots, lab_works, students, all_units)

            session.commit()
            log.info("=== seed completed successfully ===")
        except Exception as exc:
            session.rollback()
            log.exception("seed FAILED: %s", exc)
            raise


if __name__ == "__main__":
    run()
