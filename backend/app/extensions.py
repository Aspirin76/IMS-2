"""Flask 擴充物件的單一來源（避免循環 import）。"""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
