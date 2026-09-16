from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Group

groups_bp = Blueprint("groups", __name__)


@groups_bp.route("/", methods=["GET", "POST"])
def list_groups():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        speciality = request.form.get("speciality", "").strip()
        course = request.form.get("course", type=int)

        if not name or not speciality or not course:
            flash("Заполните все поля группы.", "error")
        elif Group.query.filter_by(name=name).first():
            flash(f"Группа {name} уже существует.", "error")
        else:
            db.session.add(Group(name=name, speciality=speciality, course=course))
            db.session.commit()
            flash(f"Группа {name} добавлена.", "success")
        return redirect(url_for("groups.list_groups"))

    return render_template("groups.html", groups=Group.query.order_by(Group.name).all())


@groups_bp.route("/<int:group_id>/delete", methods=["POST"])
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash("Группа удалена.", "success")
    return redirect(url_for("groups.list_groups"))