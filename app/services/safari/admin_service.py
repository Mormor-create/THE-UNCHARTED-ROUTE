"""Admin business logic for the safari catalogue."""

import re
import unicodedata
from sqlalchemy.exc import IntegrityError
from extensions import db
from app.models.safari import (
    SafariDestination,
    SafariProperty,
    SafariPropertyMedia,
    SafariPackageOption,
    SafariItineraryDay,
    SafariPackageRate,
)

def make_slug(value):
    """Create a predictable URL slug from a name."""
    value = unicodedata.normalize("NFKD", value or "")
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")

def _populate_instance(form, instance, excluded=None):
    """Copy matching submitted form fields to a model instance."""
    excluded = set(excluded or ())
    excluded.update({"csrf_token", "submit"})

    for field_name, field in form._fields.items():
        if field_name in excluded:
            continue

        if hasattr(instance, field_name):
            setattr(instance, field_name, field.data)

def _save(instance):
    """Commit a model change and roll back on database errors."""
    try:
        db.session.add(instance)
        db.session.commit()
        return instance
    except IntegrityError:
        db.session.rollback()
        raise

def _save_named(form, model, instance=None, excluded=None):
    """Save a named record with a generated slug when needed."""
    instance = instance or model()
    _populate_instance(form, instance, excluded=excluded)

    if hasattr(instance, "name") and hasattr(instance, "slug"):
        instance.slug = make_slug(
            getattr(instance, "slug", None)
            or getattr(instance, "name", "")
        )

    return _save(instance)

# -----------------------------------------------------------------------------
# Destinations
# -----------------------------------------------------------------------------
def list_destinations(include_inactive=True):
    query = SafariDestination.query

    if not include_inactive:
        query = query.filter_by(active=True)

    return query.order_by(
        SafariDestination.display_order,
        SafariDestination.name,
    ).all()

def get_destination(destination_id):
    return db.session.get(SafariDestination, destination_id)

def save_destination(form, instance=None):
    return _save_named(form, SafariDestination, instance)

def set_destination_active(destination, active):
    destination.active = bool(active)
    return _save(destination)

# -----------------------------------------------------------------------------
# Properties
# -----------------------------------------------------------------------------
def list_properties(destination_id=None, include_inactive=True):
    query = SafariProperty.query

    if destination_id is not None:
        query = query.filter_by(destination_id=destination_id)

    if not include_inactive:
        query = query.filter_by(active=True)

    return query.order_by(
        SafariProperty.display_order,
        SafariProperty.name,
    ).all()

def get_property(property_id):
    return db.session.get(SafariProperty, property_id)

def save_property(form, instance=None):
    return _save_named(form, SafariProperty, instance)

def set_property_active(property_obj, active):
    property_obj.active = bool(active)
    return _save(property_obj)

# -----------------------------------------------------------------------------
# Property gallery
# -----------------------------------------------------------------------------
def list_property_media(property_id, include_inactive=True):
    query = SafariPropertyMedia.query.filter_by(property_id=property_id)

    if not include_inactive:
        query = query.filter_by(active=True)

    return query.order_by(
        SafariPropertyMedia.display_order,
        SafariPropertyMedia.id,
    ).all()

def save_property_media(property_obj, form, media_item=None):
    """
    Add or update an asset association.

    The route must populate the asset select choices from the existing DAM.
    This function does not upload or duplicate files.
    """
    media_item = media_item or SafariPropertyMedia()
    media_item.property_id = property_obj.id

    _populate_instance(
        form,
        media_item,
        excluded={"property_id"},
    )

    if media_item.is_primary:
        SafariPropertyMedia.query.filter(
            SafariPropertyMedia.property_id == property_obj.id,
            SafariPropertyMedia.id != media_item.id,
        ).update(
            {SafariPropertyMedia.is_primary: False},
            synchronize_session=False,
        )

    return _save(media_item)

def delete_property_media(media_item):
    db.session.delete(media_item)
    db.session.commit()

# -----------------------------------------------------------------------------
# Duration options
# -----------------------------------------------------------------------------
def list_package_options(property_id, include_inactive=True):
    query = SafariPackageOption.query.filter_by(property_id=property_id)

    if not include_inactive:
        query = query.filter_by(active=True)

    return query.order_by(
        SafariPackageOption.display_order,
        SafariPackageOption.duration_days,
    ).all()

def get_package_option(option_id):
    return db.session.get(SafariPackageOption, option_id)

def save_package_option(property_obj, form, option=None):
    option = option or SafariPackageOption()
    option.property_id = property_obj.id

    _populate_instance(
        form,
        option,
        excluded={"property_id"},
    )

    option.slug = make_slug(option.slug or option.name)

    return _save(option)

def set_package_option_active(option, active):
    option.active = bool(active)
    return _save(option)

# -----------------------------------------------------------------------------
# Itinerary
# -----------------------------------------------------------------------------
def list_itinerary_days(option_id, active_only=False):
    """List itinerary days, including inactive days in admin by default."""
    query = SafariItineraryDay.query.filter_by(
        package_option_id=option_id
    )

    if active_only:
        query = query.filter_by(active=True)

    return query.order_by(
        SafariItineraryDay.day_number.asc()
    ).all()

def save_itinerary_day(option, form, day=None):
    day = day or SafariItineraryDay()
    day.package_option_id = option.id

    _populate_instance(
        form,
        day,
        excluded={"package_option_id"},
    )

    return _save(day)

def delete_itinerary_day(day):
    db.session.delete(day)
    db.session.commit()

# -----------------------------------------------------------------------------
# Rates
# -----------------------------------------------------------------------------
def list_rates(option_id, include_inactive=True):
    query = SafariPackageRate.query.filter_by(
        package_option_id=option_id
    )

    if not include_inactive:
        query = query.filter_by(active=True)

    return query.order_by(
        SafariPackageRate.display_order,
        SafariPackageRate.amount,
    ).all()

def save_rate(option, form, rate=None):
    rate = rate or SafariPackageRate()
    rate.package_option_id = option.id

    _populate_instance(
        form,
        rate,
        excluded={"package_option_id"},
    )

    return _save(rate)

def set_rate_active(rate, active):
    rate.active = bool(active)
    return _save(rate)