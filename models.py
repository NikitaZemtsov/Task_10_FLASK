from app import db
from slugify import slugify



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
