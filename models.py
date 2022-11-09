from app import db
from slugify import slugify
from flask_security import RoleMixin, UserMixin
from datetime import datetime
from app import bcrypt



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


class CourseModel(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer(), primary_key=True)
    slug = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    students = db.relationship('StudentModel', secondary=students_courses, backref="courses")

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
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    activate = db.Column(db.Boolean())
    registration = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    role = db.relationship('RoleModel', secondary=users_roles, backref="user")

    def __init__(self, *args, **kwargs):
        super(UserModel, self).__init__(*args, **kwargs)
        self.password = bcrypt.generate_password_hash(self.password).decode("utf-8")


class RoleModel(db.Model, RoleMixin):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))






