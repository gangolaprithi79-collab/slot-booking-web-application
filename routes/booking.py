from datetime import datetime, date

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import (
    login_required,
    current_user
)

from sqlalchemy.exc import IntegrityError

from models import db
from models.service import Service
from models.slot import Slot
from models.booking import Booking


booking_bp = Blueprint(
    "booking",
    __name__
)


@booking_bp.route("/")
def home():

    services = Service.query.order_by(
        Service.name.asc()
    ).all()

    return render_template(
        "slots.html",
        services=services,
        slots=[],
        home_mode=True
    )


@booking_bp.route("/dashboard")
@login_required
def dashboard():

    services = Service.query.order_by(
        Service.name.asc()
    ).all()

    service_id = request.args.get(
        "service_id",
        type=int
    )

    selected_date = request.args.get(
        "date",
        ""
    ).strip()

    query = Slot.query.filter(
        Slot.is_booked.is_(False),
        Slot.slot_date >= date.today()
    )

    if service_id:

        query = query.filter_by(
            service_id=service_id
        )

    if selected_date:

        try:

            chosen_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).date()

            query = query.filter_by(
                slot_date=chosen_date
            )

        except ValueError:

            flash(
                "Invalid date.",
                "danger"
            )

    slots = query.order_by(
        Slot.slot_date.asc(),
        Slot.start_time.asc()
    ).all()

    return render_template(
        "dashboard.html",
        services=services,
        slots=slots,
        selected_service=service_id,
        selected_date=selected_date
    )


@booking_bp.route("/slots")
def slots():

    services = Service.query.order_by(
        Service.name.asc()
    ).all()

    service_id = request.args.get(
        "service_id",
        type=int
    )

    selected_date = request.args.get(
        "date",
        ""
    ).strip()

    query = Slot.query.filter(
        Slot.slot_date >= date.today()
    )

    if service_id:

        query = query.filter_by(
            service_id=service_id
        )

    if selected_date:

        try:

            chosen_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).date()

            query = query.filter_by(
                slot_date=chosen_date
            )

        except ValueError:

            flash(
                "Invalid date.",
                "danger"
            )

    slots = query.order_by(
        Slot.slot_date.asc(),
        Slot.start_time.asc()
    ).all()

    return render_template(
        "slots.html",
        services=services,
        slots=slots,
        selected_service=service_id,
        selected_date=selected_date,
        home_mode=False
    )


@booking_bp.route(
    "/book/<int:slot_id>",
    methods=["POST"]
)
@login_required
def book_slot(slot_id):

    try:

        slot = (
            db.session.query(Slot)
            .filter(Slot.id == slot_id)
            .with_for_update()
            .first()
        )

        if not slot:

            flash(
                "Slot not found.",
                "danger"
            )

            return redirect(
                url_for("booking.dashboard")
            )

        if slot.slot_date < date.today():

            flash(
                "You cannot book a past slot.",
                "danger"
            )

            return redirect(
                url_for("booking.dashboard")
            )

        if slot.is_booked:

            flash(
                "This slot is already booked.",
                "warning"
            )

            return redirect(
                url_for("booking.dashboard")
            )

        booking = Booking(
            user_id=current_user.id,
            slot_id=slot.id,
            status="Booked"
        )

        slot.is_booked = True

        db.session.add(booking)

        db.session.commit()

        flash(
            "Slot booked successfully.",
            "success"
        )

        return redirect(
            url_for("booking.my_bookings")
        )

    except IntegrityError:

        db.session.rollback()

        flash(
            "This slot was already booked.",
            "warning"
        )

        return redirect(
            url_for("booking.dashboard")
        )


@booking_bp.route("/my-bookings")
@login_required
def my_bookings():

    bookings = (
        Booking.query
        .filter_by(
            user_id=current_user.id
        )
        .join(Slot)
        .order_by(
            Slot.slot_date.desc(),
            Slot.start_time.desc()
        )
        .all()
    )

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )


@booking_bp.route(
    "/cancel/<int:booking_id>",
    methods=["POST"]
)
@login_required
def cancel_booking(booking_id):

    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=current_user.id
    ).first_or_404()

    if booking.status == "Cancelled":

        flash(
            "Booking already cancelled.",
            "info"
        )

        return redirect(
            url_for("booking.my_bookings")
        )

    booking.status = "Cancelled"

    booking.slot.is_booked = False

    db.session.commit()

    flash(
        "Booking cancelled successfully.",
        "success"
    )

    return redirect(
        url_for("booking.my_bookings")
    )


@booking_bp.route("/api/slots")
def api_slots():

    slots = (
        Slot.query
        .filter(
            Slot.is_booked.is_(False),
            Slot.slot_date >= date.today()
        )
        .order_by(
            Slot.slot_date,
            Slot.start_time
        )
        .all()
    )

    return jsonify([
        {
            "id": slot.id,
            "service": slot.service.name,
            "date": slot.slot_date.isoformat(),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M")
        }
        for slot in slots
    ])