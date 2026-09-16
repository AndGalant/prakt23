from flask import Blueprint, render_template, jsonify
from app.models import Group, Teacher, Lesson

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    groups = Group.query.order_by(Group.name).all()
    teachers = Teacher.query.order_by(Teacher.name).all()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    pairs = [1, 2, 3, 4, 5, 6]
    return render_template(
        "index.html",
        groups=groups,
        teachers=teachers,
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
    return jsonify(result)