from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Teacher, Subject

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.route("/", methods=["GET", "POST"])
def list_teachers():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        short_name = request.form.get("short_name", "").strip()
        color = request.form.get("color", "#4A90D9")
        subject_ids = request.form.getlist("subject_ids", type=int)

        if not name or not short_name:
            flash("Заполните ФИО и краткое обозначение.", "error")
        else:
            teacher = Teacher(name=name, short_name=short_name, color=color)
            if subject_ids:
                teacher.subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
            db.session.add(teacher)
            db.session.commit()
            flash(f"Преподаватель {short_name} добавлен.", "success")
        return redirect(url_for("teachers.list_teachers"))

    return render_template(
        "teachers.html",
        teachers=Teacher.query.order_by(Teacher.name).all(),
        subjects=Subject.query.order_by(Subject.name).all(),
    )


@teachers_bp.route("/<int:teacher_id>/delete", methods=["POST"])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash("Преподаватель удалён.", "success")
    return redirect(url_for("teachers.list_teachers"))

from flask import jsonify

@teachers_bp.route("/<int:teacher_id>/subjects")
def teacher_subjects(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    return jsonify([
        {"id": s.id, "name": s.name, "short_name": s.short_name}
        for s in teacher.subjects
    ])