from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .service import Service
from .slot import Slot
from .booking import Booking