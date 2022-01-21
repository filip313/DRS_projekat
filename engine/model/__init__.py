from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from multiprocessing import Pipe

pc, cc = Pipe()

db = SQLAlchemy()
ma = Marshmallow()