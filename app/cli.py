import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import Group, Teacher, Subject, Classroom


def register_cli(app):
    @app.cli.command("init-db")
    @with_appcontext
    def init_db():
        """Создать таблицы и наполнить тестовыми данными."""
        db.create_all()

        if not Group.query.first():
            db.session.add_all([
                Group(name="П-21", speciality="Программирование", course=2),
                Group(name="П-22", speciality="Программирование", course=2),
                Group(name="П-23", speciality="Программирование", course=2),
                Group(name="ИС-21", speciality="Информационные системы", course=2),
            ])

        if not Subject.query.first():
            inf  = Subject(name="Информатика", short_name="ИНФ")
            oap  = Subject(name="Основы алгоритмизации и программирования", short_name="ОАП")
            prog = Subject(name="Программирование", short_name="ПРОГ")
            math = Subject(name="Математика", short_name="МАТ")
            phys = Subject(name="Физика", short_name="ФИЗ")
            bd   = Subject(name="Базы данных", short_name="БД")
            db.session.add_all([inf, oap, prog, math, phys, bd])
            db.session.flush()

            ivanov = Teacher(name="Иванов Сергей Владимирович", short_name="ИВ", color="#4A90D9")
            ivanov.subjects = [inf, oap, prog]

            petrova = Teacher(name="Петрова Анна Ивановна", short_name="ПЕ", color="#4CAF50")
            petrova.subjects = [math, phys]

            sidorov = Teacher(name="Сидоров Дмитрий Алексеевич", short_name="СИ", color="#F5C542")
            sidorov.subjects = [prog, bd]

            morozova = Teacher(name="Морозова Елена Викторовна", short_name="МО", color="#9C27B0")
            morozova.subjects = [inf]

            db.session.add_all([ivanov, petrova, sidorov, morozova])

        if not Classroom.query.first():
            db.session.add_all([
                Classroom(name="305", type="Компьютерный класс", capacity=25),
                Classroom(name="204", type="Учебный кабинет", capacity=30),
                Classroom(name="312", type="Компьютерный класс", capacity=25),
            ])

        db.session.commit()
        click.echo("База данных инициализирована.")