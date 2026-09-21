from app.models import Lesson


def check_conflicts(teacher_id, group_id, classroom_id, day,
                    week1_lesson, week2_lesson, exclude_id=None):
    """
    Проверяет конфликты для новой/редактируемой пары.
    Возвращает список dict: {"type", "week", "pair", "message"}.
    """
    conflicts = []

    for week_num, pair in (("1", week1_lesson), ("2", week2_lesson)):
        if not pair:
            continue

        # Конфликт преподавателя
        q = Lesson.query.filter_by(teacher_id=teacher_id, day=day)
        q = q.filter(Lesson.week1_lesson == pair) if week_num == "1" \
            else q.filter(Lesson.week2_lesson == pair)
        if exclude_id:
            q = q.filter(Lesson.id != exclude_id)
        found = q.first()
        if found:
            conflicts.append({
                "type": "teacher",
                "week": week_num,
                "pair": pair,
                "message": (
                    f"Преподаватель уже занят в {day}, {pair} пара, "
                    f"{week_num} неделя (группа {found.group.name})"
                ),
            })

        # Конфликт группы
        q = Lesson.query.filter_by(group_id=group_id, day=day)
        q = q.filter(Lesson.week1_lesson == pair) if week_num == "1" \
            else q.filter(Lesson.week2_lesson == pair)
        if exclude_id:
            q = q.filter(Lesson.id != exclude_id)
        found = q.first()
        if found:
            conflicts.append({
                "type": "group",
                "week": week_num,
                "pair": pair,
                "message": (
                    f"У группы уже есть занятие в {day}, {pair} пара, "
                    f"{week_num} неделя ({found.subject.name})"
                ),
            })

        # Конфликт кабинета
        if classroom_id:
            q = Lesson.query.filter_by(classroom_id=classroom_id, day=day)
            q = q.filter(Lesson.week1_lesson == pair) if week_num == "1" \
                else q.filter(Lesson.week2_lesson == pair)
            if exclude_id:
                q = q.filter(Lesson.id != exclude_id)
            found = q.first()
            if found:
                conflicts.append({
                    "type": "classroom",
                    "week": week_num,
                    "pair": pair,
                    "message": (
                        f"Кабинет {found.classroom.name} уже занят в {day}, "
                        f"{pair} пара, {week_num} неделя "
                        f"(группа {found.group.name})"
                    ),
                })

    return conflicts