from flask import Blueprint, render_template
from flask import request, flash, redirect, url_for
from models import CourseModel
from .forms import CourseForm
from app import db

courses = Blueprint('courses', __name__, template_folder='templates')


@courses.route('/create_course', methods=["POST", "GET"])
def create_course():
    title = "Create course"
    form = CourseForm()
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        course = CourseModel(name=name, description=description)
        try:
            db.session.add(course)
            db.session.commit()
        except:
            flash("Not saved! Try again!", 'danger')
            return redirect(url_for("courses.create_course"))
        print("name - ", course.name, "desc - ", course.description, "slug -", course.slug)
        flash("Success! Course created!", 'success')
        return redirect(url_for("courses.courses_index"))
    return render_template("courses/create_course.html", title=title, form=form)


@courses.route('/')
def courses_index():
    title = "Courses"
    courses_list = CourseModel.query.all()
    return render_template('courses/index.html', title=title, courses=courses_list, description=False)


@courses.route('/<slug>')
def courses_description(slug):
    course = CourseModel.query.where(CourseModel.slug == slug).first()
    title = course.name
    description = course.description
    return render_template('courses/index.html', title=title, description=description)
