from flask_bcrypt import check_password_hash

from app import app
from flask import request, render_template, flash, redirect, url_for
from models import GroupModel, StudentModel, UserModel
from flask import request
from forms import RegistrationForm, LoginForm
from app import db
from flask_login import login_user, current_user, logout_user

title = "IT_school"
description="The School of Information Technology prepares students for career opportunities in cybersecurity, information systems, and other I.T. fields through accelerated I.T. degree programs. Multiple industry certifications are included in every information technology degree program, and many are covered by tuition. Cybersecurity and information technology industry employers look at certifications such as CompTIA Security+ and Network+ alongside degrees. When you graduate from IT_school with an I.T. or Cybersecurity degree, you can be confident that you have the education that employers are looking for."


@app.route("/")
def index():
    return render_template("index.html",
                           title=title,
                           description=description)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = UserModel(username=form.username.data,
                             email=form.email.data,
                             password=form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
        except:
            flash("Oops! We have some problem with our server! Please try later!", 'danger')
            return render_template('register.html', title='Register', form=form)
        flash(f"You account has been created! You are now able to log in!", "success")
        return redirect(url_for("login"))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = UserModel.query.filter_by(email=form.email.data).first()
        except:
            flash(f"Ops! We have some problem with server", "danger")
            return render_template('login.html', title='Log In', form=form)
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"You have been logged in!", "success")
            return redirect(url_for("admin.index"))
        else:
            flash(f"Log in Unsuccessful. Please check email and password", "danger")
    return render_template('login.html', title='Log In', form=form)


@app.route("/groups")
def groups():
    title = "Groups"
    groups = GroupModel.query.all()
    return render_template('groups.html',
                           title=title,
                           groups=groups)


@app.route("/groups/<slug>")
def group(slug):
    group = GroupModel.query.where(GroupModel.slug == slug).first()
    title = group.name
    students = group.students
    return render_template('group.html',
                           title=title,
                           students=students)


@app.route("/students/")
def students():
    title = "Students"
    page = request.args.get("page")
    per_page = 20
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    students = StudentModel.query
    pages = students.paginate(page=page, per_page=per_page)
    return render_template('students.html',
                           title=title,
                           students=students,
                           pages=pages,
                           per_page=per_page)


@app.route("/students/<student_id>")
def student_profile(student_id):
    student = StudentModel.query.where(StudentModel.id == student_id).first()
    return render_template('student.html',
                           title="{} {}".format(student.first_name, student.last_name),
                           group=student.group,
                           courses=student.courses)
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/account")
def account():

    return render_template('account.html', title='Account', username=current_user.username)
