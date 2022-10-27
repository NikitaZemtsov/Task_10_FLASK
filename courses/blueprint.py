from flask import Blueprint, render_template

from models import CourseModel

courses = Blueprint('courses', __name__, template_folder='templates')


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
