"""
===============================================================================
The Uncharted Route
Admin Settings Routes
===============================================================================
Administration routes for global website settings.
"""
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,)
from app.decorators.admin import admin_required
from app.forms.settings import SiteSettingsForm
from app.services.settings_service import SettingsService

# =============================================================================
# Blueprint
# =============================================================================
admin_settings = Blueprint(
    "admin_settings",
    __name__,
    url_prefix="/admin/settings",)

# =============================================================================
# Site Settings
# =============================================================================
@admin_settings.route("/", methods=["GET", "POST"])
@admin_required
def index():
    """Display and update global website settings."""
    settings = SettingsService.get_settings()
    form = SiteSettingsForm(obj=settings)

    if form.validate_on_submit():
        excluded_fields = {"submit", "csrf_token"}

        form_data = {
            field.name: field.data
            for field in form
            if field.name not in excluded_fields
        }

        # Persist the global newsletter setting when the form contains it.
        if hasattr(form, "newsletter_enabled"):
            form_data["newsletter_enabled"] = (
                form.newsletter_enabled.data)

        SettingsService.update_settings(
            settings,
            **form_data,)

        flash(
            "Website settings updated successfully.",
            "success",)

        return redirect(url_for("admin_settings.index"))

    return render_template(
        "admin/settings/index.html",
        form=form,
        settings=settings,)