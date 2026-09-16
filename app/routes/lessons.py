from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Lesson

lessons_bp = Blueprint("lessons", __name__, url_prefix="/lessons")


@lessons_bp.route("", methods=["POST"])
def create_lesson():
    data = request.get_json()
    lesson = Lesson(
        group_id=data["group_id"],
        teacher_id=data["teacher_id"],
        subject_id=data["subject_id"],
        classroom_id=data.get("classroom_id") or None,
        day=data["day"],
        week1_lesson=data.get("week1_lesson") or None,
        week2_lesson=data.get("week2_lesson") or None,
        lesson_type=data.get("lesson_type", "Лекция"),
    )
    db.session.add(lesson)
    db.session.commit()
    return jsonify({"id": lesson.id}), 201


@lessons_bp.route("/<int:lesson_id>", methods=["PUT"])
def update_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    data = request.get_json()

    lesson.group_id = data.get("group_id", lesson.group_id)
    lesson.teacher_id = data.get("teacher_id", lesson.teacher_id)
    lesson.subject_id = data.get("subject_id", lesson.subject_id)
    lesson.classroom_id = data.get("classroom_id") or None
    lesson.day = data.get("day", lesson.day)
    lesson.week1_lesson = data.get("week1_lesson") or None
    lesson.week2_lesson = data.get("week2_lesson") or None
    lesson.lesson_type = data.get("lesson_type", lesson.lesson_type)

    db.session.commit()
    return jsonify({"ok": True})


@lessons_bp.route("/<int:lesson_id>", methods=["DELETE"])
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    db.session.delete(lesson)
    db.session.commit()
    return jsonify({"ok": True})