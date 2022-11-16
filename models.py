from app import db, login_manager
from slugify import slugify
from datetime import datetime
from app import bcrypt
from flask_login import UserMixin
from flask_principal import Permission, RoleNeed


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

# Перенес инициализацию Permission с view для корректного импорта.
# Для добавления метода mentor_access в current_user.
admin = Permission(RoleNeed('admin'))
mentor = Permission(RoleNeed('mentor'))
student = Permission(RoleNeed('student'))


class GroupModel(db.Model):
    __tablename__ = "groups"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    students = db.relationship('StudentModel', backref="group")


students_courses = db.Table("students_courses",
                            db.Column("student_id", db.Integer, db.ForeignKey("students.id")),
                            db.Column("course_id", db.Integer, db.ForeignKey("courses.id")))


class StudentModel(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer(), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "{id}_{f_n}_{l_n}".format(id=self.id, f_n=self.first_name, l_n=self.last_name)


courses_mentors = db.Table("courses_mentors",
                       db.Column("mentor_id", db.Integer, db.ForeignKey("users.id")),
                       db.Column("course_id", db.Integer, db.ForeignKey("courses.id")))


class CourseModel(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer(), primary_key=True)
    slug = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    students = db.relationship('StudentModel', secondary=students_courses, backref="courses")
    mentors = db.relationship('UserModel', secondary=courses_mentors, backref="courses")

    def __init__(self, *args, **kwargs):
        super(CourseModel, self).__init__(*args, **kwargs)
        if self.name:
            self.slug = slugify(self.name)


users_roles = db.Table("users_roles",
                       db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                       db.Column("role_id", db.Integer, db.ForeignKey("roles.id")))


class UserModel(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    activate = db.Column(db.Boolean())
    registration = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    role = db.relationship('RoleModel', secondary=users_roles, backref="user", lazy=True)

    def __init__(self, *args, **kwargs):
        super(UserModel, self).__init__(*args, **kwargs)
        self.password = bcrypt.generate_password_hash(self.password).decode("utf-8")

    def __repr__(self):
        return "{id}_{f_n}_{l_n}".format(id=self.id, f_n=self.first_name, l_n=self.last_name)

    # Реализовал для динамического отображения вкладок на base.html в зависимости от роли юзера.
    # Чтобы не пробрасывать лишнюю переменную mentor в каждую вьюху
    @property
    def mentor_access(self):
        return mentor.can()


class RoleModel(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))






