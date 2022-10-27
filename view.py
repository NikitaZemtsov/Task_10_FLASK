from app import app
from flask import request, render_template
from models import GroupModel, StudentModel, CourseModel
from flask import request

title = "IT_school"
description="The School of Information Technology prepares students for career opportunities in cybersecurity, information systems, and other I.T. fields through accelerated I.T. degree programs. Multiple industry certifications are included in every information technology degree program, and many are covered by tuition. Cybersecurity and information technology industry employers look at certifications such as CompTIA Security+ and Network+ alongside degrees. When you graduate from IT_school with an I.T. or Cybersecurity degree, you can be confident that you have the education that employers are looking for."


@app.route("/")
def index():
    return render_template("index.html", title=title, description=description)


@app.route("/groups")
def groups():
    title = "Groups"
    groups = GroupModel.query.all()
    return render_template('groups.html', title=title, groups=groups)

@app.route("/groups/<slug>")
def group(slug):
    group = GroupModel.query.where(GroupModel.slug == slug).first()
    title = group.name
    students = group.students
    return render_template('group.html', title=title, students=students)

@app.route("/students")
def students():
    pass

@app.route("/students/<student_id>")
def student_profile(student_id):
    student = StudentModel.query.where(StudentModel.id == student_id).first()
    return render_template('student.html',
                           title="{} {}".format(student.first_name, student.last_name),
                           group=student.group,
                           courses=student.courses)


