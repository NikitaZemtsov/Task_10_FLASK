import os
from PIL import Image
import secrets
from flask_bcrypt import check_password_hash
from flask import request, render_template, flash, redirect, url_for, session, g
from flask_principal import identity_loaded, identity_changed, UserNeed, RoleNeed, Identity, AnonymousIdentity
from flask_login import login_user, current_user, logout_user, login_required

from app import app, db
from models import GroupModel, StudentModel, UserModel, RoleModel, CourseModel, admin, mentor, student
from forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateCourseForm



title = "IT_school"
description="The School of Information Technology prepares students for career opportunities in cybersecurity, information systems, and other I.T. fields through accelerated I.T. degree programs. Multiple industry certifications are included in every information technology degree program, and many are covered by tuition. Cybersecurity and information technology industry employers look at certifications such as CompTIA Security+ and Network+ alongside degrees. When you graduate from IT_school with an I.T. or Cybersecurity degree, you can be confident that you have the education that employers are looking for."


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user
    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    role = getattr(current_user, 'role', [])
    needs = []
    if current_user.is_authenticated:
        if role[0].name in ('student', "mentor", "admin"):
            needs.append(RoleNeed('student'))
        if role[0].name in ("mentor", "admin"):
            needs.append(RoleNeed('mentor'))
        if role[0].name == "admin":
            needs.append(RoleNeed('admin'))

    if hasattr(current_user, 'role'):
        for need in needs:
            identity.provides.add(need)

# Заготовка под точечный доступ к редактированию курсов менторами. Менторы смогут редактировать только те курсы,
# к которым у них есть доступ.
# CoursesNeed = namedtuple('courses', ['method', 'value'])
# EditCoursesNeed = partial(CoursesNeed, 'edit')


# class CoursesPermission(Permission):
#     def __init__(self, post_id):
#         need = EditCoursesNeed(unicode(post_id))
#         super(CoursesPermission, self).__init__(need)
#
#
# @identity_loaded.connect_via(app)
# def on_identity_loaded(sender, identity):
#     # Set the identity user object
#     identity.user = current_user
#
#     # Add the UserNeed to the identity
#     if hasattr(current_user, 'id'):
#         identity.provides.add(UserNeed(current_user.id))
#
#     # Assuming the User model has a list of roles, update the
#     # identity with the roles that the user provides
#     if hasattr(current_user, 'roles'):
#         for role in current_user.role:
#             identity.provides.add(RoleNeed(role.name))
#
#     if hasattr(current_user, 'courses'):
#         for course in current_user.courses:
#             identity.provides.add(EditCoursesNeed(unicode(course.id)))


@app.route("/")
def index():
    print(g.identity.can(mentor))
    return render_template("index.html",
                           title=title,
                           description=description)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        role = RoleModel.query.filter_by(name="student").first()
        new_user = UserModel(username=form.username.data,
                             email=form.email.data,
                             password=form.password.data,
                             first_name=form.first_name.data,
                             last_name=form.last_name.data)
        new_user.role.append(role)
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

            identity_changed.send(app, identity=Identity(user.id))

            next_link = request.args.get("next")
            login_user(user, remember=form.remember.data)
            flash(f"You have been logged in!", "success")
            return redirect(next_link) if next_link else redirect(url_for("index"))
        else:
            flash(f"Log in Unsuccessful. Please check email and password", "danger")
    return render_template('login.html', title='Log In', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

        # Tell Flask-Principal the user is anonymous
    identity_changed.send(app,
                          identity=AnonymousIdentity())

    return redirect(url_for("index"))


@app.route("/groups")
@mentor.require(403)
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
@mentor.require(403)
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
@mentor.require(403)
def student_profile(student_id):
    student = StudentModel.query.where(StudentModel.id == student_id).first()
    return render_template('student.html',
                           title="{} {}".format(student.first_name, student.last_name),
                           group=student.group,
                           courses=student.courses)


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
        role = RoleModel.query.filter_by(id=form.role.data).first()
        current_user.role.append(role)
        current_user.role.pop(0)
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
        roles = correct_representetion_list(RoleModel.query.all(), current_user.role)
        form.role.choices = [(role.id, role.name) for role in roles]
    profile_img = url_for("static", filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', profile_img=profile_img, form=form, admin=admin)


def correct_representetion_list(roles, current_role):
    i = 0
    for role in roles:
        if role.id == current_role[0].id:
            roles.pop(i)
        i+=1
    roles.insert(0, current_role[0])
    return roles


@app.route('/courses/create', methods=["POST", "GET"])
@mentor.require(403)
def create_course():
    form = CreateCourseForm()
    if request.method == "GET":
        title = "Create course"
        return render_template("create_course.html", title=title, form=form, course=None)
    elif request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        course = CourseModel(name=name, description=description)
        flash("Success! Course created!", 'success')

    try:
        db.session.add(course)
        db.session.commit()
    except:
        flash("Not saved! Try again!", 'danger')
        return redirect(url_for("create_course"))

    return redirect(url_for("courses_index"))


@app.route('/courses/update/<course_slug>', methods=["POST", "GET"])
@mentor.require(403)
def update_course(course_slug=None):
    form = CreateCourseForm()
    course = CourseModel.query.filter_by(slug=course_slug).first()
    if request.method == "GET":
        title = "Edit course"
        form.name.data = course.name
        form.description.data = course.description
        return render_template("create_course.html", title=title, form=form, course=course)
    elif request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        course.name = name
        course.description = description
        flash("Success! Course updated!", 'success')
        try:
            db.session.commit()
        except:
            flash("Not saved! Try again!", 'danger')
            return redirect(url_for("create_course"))

    return redirect(url_for("courses_index"))


@app.route('/courses/')
def courses_index():
    title = "Courses"
    courses_list = CourseModel.query.all()
    return render_template('courses.html', title=title, courses=courses_list, description=False)


@app.route('/courses/description/<course_slug>')
def courses_description(course_slug):
    course = CourseModel.query.where(CourseModel.slug == course_slug).first()
    title = course.name
    description = course.description
    return render_template('courses.html', title=title, description=description, course=course)






