from flask import Blueprint, render_template
from app.models import Group, Teacher, Lesson, Classroom

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    groups = Group.query.order_by(Group.name).all()
    teachers = Teacher.query.order_by(Teacher.name).all()
    classrooms = Classroom.query.order_by(Classroom.name).all()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    pairs = [1, 2, 3, 4, 5, 6]
    return render_template(
        "index.html",
        groups=groups,
        teachers=teachers,
        classrooms=classrooms,
        days=days,
        pairs=pairs,
    )


@main_bp.route("/api/schedule")
def api_schedule():
    lessons = Lesson.query.all()
    result = []
    for l in lessons:
        result.append({
            "id": l.id,
            "group_id": l.group_id,
            "group_name": l.group.name,
            "teacher_id": l.teacher_id,
            "teacher_short": l.teacher.short_name,
            "teacher_name": l.teacher.name,
            "teacher_color": l.teacher.color,
            "subject_id": l.subject_id,
            "subject_name": l.subject.name,
            "subject_short": l.subject.short_name,
            "classroom_id": l.classroom_id,
            "classroom_name": l.classroom.name if l.classroom else "—",
            "day": l.day,
            "week1_lesson": l.week1_lesson,
            "week2_lesson": l.week2_lesson,
            "lesson_type": l.lesson_type,
        })
    return jsonify_result(result)


def jsonify_result(data):
    from flask import jsonify
    return jsonify(data)


# ===== Сравнение недель (индивидуальное задание №23) =====
@main_bp.route("/compare")
def compare():
    groups = Group.query.order_by(Group.name).all()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    pairs = [1, 2, 3, 4, 5, 6]

    # Матрица: (group_id, day, pair) -> (lesson_w1, lesson_w2)
    matrix = {}
    for g in groups:
        for day in days:
            for pair in pairs:
                lessons = Lesson.query.filter_by(group_id=g.id, day=day).all()
                w1 = None
                w2 = None
                for l in lessons:
                    if l.week1_lesson == pair:
                        w1 = l
                    if l.week2_lesson == pair:
                        w2 = l
                matrix[(g.id, day, pair)] = (w1, w2)

    # Список различий
    differences = []
    for g in groups:
        for day in days:
            for pair in pairs:
                w1, w2 = matrix[(g.id, day, pair)]
                if not w1 and not w2:
                    continue
                if w1 and not w2:
                    differences.append({
                        "group": g.name, "day": day, "pair": pair,
                        "status": "only1",
                        "text": _lesson_text(w1),
                    })
                elif w2 and not w1:
                    differences.append({
                        "group": g.name, "day": day, "pair": pair,
                        "status": "only2",
                        "text": _lesson_text(w2),
                    })
                elif w1 and w2:
                    if w1.id == w2.id:
                        differences.append({
                            "group": g.name, "day": day, "pair": pair,
                            "status": "same",
                            "text": _lesson_text(w1),
                        })
                    else:
                        differences.append({
                            "group": g.name, "day": day, "pair": pair,
                            "status": "diff",
                            "text": f"1 нед: {_lesson_text(w1)} / 2 нед: {_lesson_text(w2)}",
                        })

    return render_template(
        "compare.html",
        groups=groups,
        days=days,
        pairs=pairs,
        matrix=matrix,
        differences=differences,
    )


def _lesson_text(l):
    if not l:
        return "—"
    return f"{l.teacher.short_name} • {l.subject.short_name}"


# ===== Печать =====
@main_bp.route("/print")
def print_schedule():
    groups = Group.query.order_by(Group.name).all()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    pairs = [1, 2, 3, 4, 5, 6]

    matrix = {}
    for g in groups:
        for day in days:
            for pair in pairs:
                lessons = Lesson.query.filter_by(group_id=g.id, day=day).all()
                w1 = next((l for l in lessons if l.week1_lesson == pair), None)
                w2 = next((l for l in lessons if l.week2_lesson == pair), None)
                matrix[(g.id, day, pair)] = (w1, w2)

    return render_template(
        "print.html",
        groups=groups, days=days, pairs=pairs, matrix=matrix,
    )