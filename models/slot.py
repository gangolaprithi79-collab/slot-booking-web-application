from . import db


class Slot(db.Model):

    __tablename__ = "slots"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "services.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    slot_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    start_time = db.Column(
        db.Time,
        nullable=False
    )

    end_time = db.Column(
        db.Time,
        nullable=False
    )

    is_booked = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    service = db.relationship(
        "Service",
        back_populates="slots"
    )

    booking = db.relationship(
        "Booking",
        back_populates="slot",
        uselist=False,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "service_id",
            "slot_date",
            "start_time",
            name="uq_service_date_time"
        ),
    )