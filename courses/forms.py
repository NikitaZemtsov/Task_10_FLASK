from wtforms import Form, StringField, TextAreaField


class CourseForm(Form):
    name = StringField("Name")
    description = TextAreaField("Description")