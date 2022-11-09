from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)

from courses.blueprint import courses
app.register_blueprint(courses, url_prefix="/courses")


from models import GroupModel, StudentModel, CourseModel, UserModel, RoleModel, db
admin = Admin(app)
admin.add_view(ModelView(GroupModel, db.session))
admin.add_view(ModelView(StudentModel, db.session))
admin.add_view(ModelView(UserModel, db.session))
admin.add_view(ModelView(CourseModel, db.session))
admin.add_view(ModelView(RoleModel, db.session))
