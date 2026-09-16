from app.extensions import db


# Связь «преподаватель — несколько дисциплин»
teacher_subjects = db.Table(
    "teacher_subjects",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teachers.id"), primary_key=True),
    db.Column("subject_id", db.Integer, db.ForeignKey("subjects.id"), primary_key=True),
)


class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    speciality = db.Column(db.String(150), nullable=False)
    course = db.Column(db.Integer, nullable=False)

    lessons = db.relationship("Lesson", backref="group", cascade="all, delete-orphan")


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    short_name = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(20), default="#4A90D9")

    subjects = db.relationship(
        "Subject",
        secondary=teacher_subjects,
        backref=db.backref("teachers", lazy="dynamic"),
    )
    lessons = db.relationship("Lesson", backref="teacher", cascade="all, delete-orphan")


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    short_name = db.Column(db.String(20), nullable=False)


class Classroom(db.Model):
    __tablename__ = "classrooms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    type = db.Column(db.String(50))
    capacity = db.Column(db.Integer)

    lessons = db.relationship("Lesson", backref="classroom")


class Lesson(db.Model):
    __tablename__ = "lessons"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey("classrooms.id"))

    day = db.Column(db.String(20), nullable=False)
    week1_lesson = db.Column(db.Integer)
    week2_lesson = db.Column(db.Integer)
    lesson_type = db.Column(db.String(30), default="Лекция")

    subject = db.relationship("Subject")