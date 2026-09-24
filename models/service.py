from . import db


class Service(db.Model):

    __tablename__ = "services"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        nullable=False,
        default=30
    )

    description = db.Column(
        db.String(255)
    )

    slots = db.relationship(
        "Slot",
        back_populates="service",
        cascade="all, delete-orphan"
    )
