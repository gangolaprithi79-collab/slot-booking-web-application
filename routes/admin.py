from datetime import datetime, date
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import current_user

from sqlalchemy.exc import IntegrityError

from models import db
from models.user import User
from models.service import Service
from models.slot import Slot
from models.booking import Booking


# ==========================================================
# ADMIN BLUEPRINT
# ==========================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ==========================================================
# ADMIN CHECK
# ==========================================================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:

            return redirect(
                url_for("auth.login")
            )

        if current_user.role != "admin":

            abort(403)

        return function(
            *args,
            **kwargs
        )

    return wrapper


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@admin_bp.route("/")
@admin_required
def dashboard():

    users_count = User.query.count()

    services_count = Service.query.count()

    slots_count = Slot.query.count()

    bookings_count = Booking.query.filter_by(
        status="Booked"
    ).count()

    services = Service.query.order_by(
        Service.name.asc()
    ).all()

    recent_bookings = Booking.query.order_by(
        Booking.created_at.desc()
    ).limit(20).all()

    return render_template(
        "admin.html",
        users_count=users_count,
        services_count=services_count,
        slots_count=slots_count,
        bookings_count=bookings_count,
        services=services,
        recent_bookings=recent_bookings
    )


# ==========================================================
# ADD SERVICE
# ==========================================================

@admin_bp.route(
    "/service/add",
    methods=["POST"]
)
@admin_required
def add_service():

    name = request.form.get(
        "name",
        ""
    ).strip()

    duration = request.form.get(
        "duration",
        type=int
    )

    description = request.form.get(
        "description",
        ""
    ).strip()

    if not name:

        flash(
            "Service name is required.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if duration is None or duration <= 0:

        flash(
            "Duration must be greater than 0.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    existing_service = Service.query.filter_by(
        name=name
    ).first()

    if existing_service:

        flash(
            "This service already exists.",
            "warning"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    service = Service(
        name=name,
        duration=duration,
        description=description
    )

    db.session.add(service)

    db.session.commit()

    flash(
        "Service added successfully.",
        "success"
    )

    return redirect(
        url_for("admin.dashboard")
    )


# ==========================================================
# CREATE SLOT
# ==========================================================

@admin_bp.route(
    "/slot/add",
    methods=["POST"]
)
@admin_required
def add_slot():

    print("\n================================")
    print("CREATE SLOT ROUTE CALLED")
    print("================================")

    print("FORM DATA:")
    print(request.form)


    # ------------------------------------------------------
    # Get form values
    # ------------------------------------------------------

    service_id = request.form.get(
        "service_id",
        type=int
    )

    slot_date_text = request.form.get(
        "slot_date",
        ""
    ).strip()

    start_time_text = request.form.get(
        "start_time",
        ""
    ).strip()

    end_time_text = request.form.get(
        "end_time",
        ""
    ).strip()


    print("service_id =", service_id)
    print("slot_date =", slot_date_text)
    print("start_time =", start_time_text)
    print("end_time =", end_time_text)


    # ------------------------------------------------------
    # Validate service
    # ------------------------------------------------------

    if not service_id:

        flash(
            "Please select a service.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # Validate date
    # ------------------------------------------------------

    if not slot_date_text:

        flash(
            "Please select a date.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # Validate start time
    # ------------------------------------------------------

    if not start_time_text:

        flash(
            "Please select a start time.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # Validate end time
    # ------------------------------------------------------

    if not end_time_text:

        flash(
            "Please select an end time.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # Convert date/time
    # ------------------------------------------------------

    try:

        slot_date = datetime.strptime(
            slot_date_text,
            "%Y-%m-%d"
        ).date()

        start_time = datetime.strptime(
            start_time_text,
            "%H:%M"
        ).time()

        end_time = datetime.strptime(
            end_time_text,
            "%H:%M"
        ).time()

    except ValueError as error:

        print("DATE/TIME ERROR:", error)

        flash(
            "Invalid date or time.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # Past date check
    # ------------------------------------------------------

    if slot_date < date.today():

        flash(
            "You cannot create a slot for a past date.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # Time check
    # ------------------------------------------------------

    if start_time >= end_time:

        flash(
            "End time must be after start time.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # Find service
    # ------------------------------------------------------

    service = db.session.get(
        Service,
        service_id
    )

    if not service:

        flash(
            "Selected service does not exist.",
            "danger"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # Check duplicate
    # ------------------------------------------------------

    existing_slot = Slot.query.filter_by(
        service_id=service_id,
        slot_date=slot_date,
        start_time=start_time
    ).first()

    if existing_slot:

        flash(
            "This slot already exists.",
            "warning"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ------------------------------------------------------
    # CREATE SLOT
    # ------------------------------------------------------

    try:

        new_slot = Slot(
            service_id=service_id,
            slot_date=slot_date,
            start_time=start_time,
            end_time=end_time,
            is_booked=False
        )

        db.session.add(new_slot)

        db.session.commit()


        print("\n================================")
        print("SLOT CREATED SUCCESSFULLY")
        print("SLOT ID:", new_slot.id)
        print("================================")


        flash(
            "Slot created successfully.",
            "success"
        )

    except IntegrityError as error:

        db.session.rollback()

        print("DATABASE INTEGRITY ERROR:")
        print(error)

        flash(
            "This slot already exists.",
            "warning"
        )

    except Exception as error:

        db.session.rollback()

        print("DATABASE ERROR:")
        print(error)

        flash(
            f"Error creating slot: {error}",
            "danger"
        )


    return redirect(
        url_for("admin.dashboard")
    )