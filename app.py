from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_principal import Principal


app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
Principal(app)

login_manager.login_view = "login"


from models import GroupModel, CourseModel, UserModel, db
admin = Admin(app)
admin.add_view(ModelView(GroupModel, db.session))
admin.add_view(ModelView(UserModel, db.session))
admin.add_view(ModelView(CourseModel, db.session))






