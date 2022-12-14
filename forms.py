from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app import app
from models import UserModel


class RegistrationForm(FlaskForm):

    first_name = StringField("First name",
                           validators=[DataRequired()])
    last_name = StringField("Last name",
                             validators=[DataRequired()])
    username = StringField("Username",
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(),
                                    Email(granular_message=True)])
    password = PasswordField("Password",
                             validators=[DataRequired(),
                                         Length(min=6, max=12, message="Password lenght should be from 6 to 12")])
    password_confirm = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        if UserModel.query.filter_by(email=email.data).first():
            raise ValidationError('User with this email is already registered!')

    def validate_username(self, username):
        if UserModel.query.filter_by(username=username.data).first():
            raise ValidationError('Username already taken!')


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):

    first_name = StringField("First name",
                           validators=[DataRequired()])
    last_name = StringField("Last name",
                             validators=[DataRequired()])
    username = StringField("Username",
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(),
                                    Email(granular_message=True, check_deliverability=True)])
    role = SelectField('Role', coerce=int, choices=[], validate_choice=False)

    picture = FileField("Update Profile Picture",
                        validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if current_user.email != email.data:
            UserModel.query.filter_by(email=email.data).first()
            raise ValidationError('User with this email is already registered!')

    def validate_username(self, username):
        if current_user.username != username.data:
            UserModel.query.filter_by(username=username.data).first()
            raise ValidationError('Username already taken!')


class CreateCourseForm(FlaskForm):
    name = StringField("Name")
    description = TextAreaField("Description")
    submit = SubmitField('Create')




