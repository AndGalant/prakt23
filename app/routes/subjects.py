from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Subject, Teacher

subjects_bp = Blueprint("subjects", __name__)


@subjects_bp.route("/", methods=["GET", "POST"])
def list_subjects():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        short_name = request.form.get("short_name", "").strip()
        teacher_id = request.form.get("teacher_id", type=int)

        if not name or not short_name:
            flash("Заполните название и сокращение.", "error")
        else:
            subject = Subject(name=name, short_name=short_name)
            if teacher_id:
                teacher = Teacher.query.get(teacher_id)
                if teacher:
                    subject.teachers.append(teacher)
            db.session.add(subject)
            db.session.commit()
            flash(f"Дисциплина {name} добавлена.", "success")
        return redirect(url_for("subjects.list_subjects"))

    return render_template(
        "subjects.html",
        subjects=Subject.query.order_by(Subject.name).all(),
        teachers=Teacher.query.order_by(Teacher.name).all(),
    )


@subjects_bp.route("/<int:subject_id>/delete", methods=["POST"])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash("Дисциплина удалена.", "success")
    return redirect(url_for("subjects.list_subjects"))