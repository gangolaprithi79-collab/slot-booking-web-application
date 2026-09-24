from datetime import datetime

from . import db


class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    slot_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "slots.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Booked"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="bookings"
    )

    slot = db.relationship(
        "Slot",
        back_populates="booking"
    )