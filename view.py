from flask_bcrypt import check_password_hash
import secrets
import os
from PIL import Image

from app import app
from flask import request, render_template, flash, redirect, url_for
from models import GroupModel, StudentModel, UserModel
from flask import request
from forms import RegistrationForm, LoginForm, UpdateAccountForm
from app import db
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps

title = "IT_school"
description="The School of Information Technology prepares students for career opportunities in cybersecurity, information systems, and other I.T. fields through accelerated I.T. degree programs. Multiple industry certifications are included in every information technology degree program, and many are covered by tuition. Cybersecurity and information technology industry employers look at certifications such as CompTIA Security+ and Network+ alongside degrees. When you graduate from IT_school with an I.T. or Cybersecurity degree, you can be confident that you have the education that employers are looking for."


def role(view):

    @wraps(view)
    def decorator(*args, **kwargs):
        if current_user.is_authenticated and current_user.role == 'mentor':
            return view(*args, **kwargs)
        else:
            flash(f"Ops! This page is not available", "danger")
            return redirect(url_for("login"))

    return decorator


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
                             password=form.password.data,
                             first_name=form.first_name.data,
                             last_name=form.last_name.data)
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
            next_link = request.args.get("next")
            login_user(user, remember=form.remember.data)
            flash(f"You have been logged in!", "success")
            return redirect(next_link) if next_link else redirect(url_for("index"))
        else:
            flash(f"Log in Unsuccessful. Please check email and password", "danger")
    return render_template('login.html', title='Log In', form=form)


@app.route("/groups")
@login_required
@role
def groups():
    title = "Groups"
    groups = GroupModel.query.all()
    return render_template('groups.html',
                           title=title,
                           groups=groups)


@app.route("/groups/<slug>")
@login_required
@role
def group(slug):
    group = GroupModel.query.where(GroupModel.slug == slug).first()
    title = group.name
    students = group.students
    return render_template('group.html',
                           title=title,
                           students=students)


@app.route("/students/")
@login_required
@role
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
@login_required
@role
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


def save_picture(form_picture) -> str:
    random_hex = secrets.token_hex(8)
    _, f_exp = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_exp
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

    out_image_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(out_image_size)
    i.save(picture_path)

    return picture_fn


def delete_picture(file_name):
    picture_path = os.path.join(app.root_path, "static/profile_pics", file_name)
    os.remove(picture_path)


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    form = UpdateAccountForm()
    fn_for_delete = ""
    if form.validate_on_submit():
        if form.picture.data:
            picture_file_name = save_picture(form.picture.data)
            fn_for_delete = current_user.image_file
            current_user.image_file = picture_file_name
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.username = form.username.data
        try:
            db.session.commit()
            flash(f"You account has been updated!", "success")
            if fn_for_delete:
                delete_picture(fn_for_delete)
        except:
            flash("Oops! We have some problem with our server! Please try later!", 'danger')
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.username.data = current_user.username
    profile_img = url_for("static", filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', profile_img=profile_img, form=form)





