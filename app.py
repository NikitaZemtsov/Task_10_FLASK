from flask import Flask
from config import Configuration
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from courses.blueprint import courses
app.register_blueprint(courses, url_prefix="/courses")


