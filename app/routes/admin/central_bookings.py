"""
===============================================================================
The Uncharted Route
Central Booking Management Routes
===============================================================================
"""
from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators.admin import admin_required
from app.services.bookings.dashboard_service import (
    get_central_booking_dashboard,)

central_bookings_bp = Blueprint(
    "admin_central_bookings",
    __name__,
    url_prefix="/admin/central-booking",)

@central_bookings_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():
    dashboard = get_central_booking_dashboard()

    return render_template(
        "admin/bookings/central_bookings/index.html",
        dashboard=dashboard,)