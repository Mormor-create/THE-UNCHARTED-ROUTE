"""
===============================================================================
The Uncharted Route
Administrative Experience Pricing Forms
===============================================================================
Forms used to create and edit pricing tiers belonging to an experiences.
"""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,)
# =============================================================================
# Experience Pricing Form
# =============================================================================
class AdminExperiencePricingForm(FlaskForm):
    """
    Create and edit an experiences pricing tier.
    """
    # -------------------------------------------------------------------------
    # Pricing Tier
    # -------------------------------------------------------------------------
    experience_level = SelectField(
        "Experience Level",
        choices=[
            ("Explorer", "Explorer"),
            ("Signature", "Signature"),
            ("Luxury", "Luxury"),
            ("Bespoke", "Bespoke"),],
        validators=[
            DataRequired(
                message="Please select an experiences level."),],)

    # -------------------------------------------------------------------------
    # Group Size
    # -------------------------------------------------------------------------
    minimum_people = IntegerField(
        "Minimum People",
        default=1,
        validators=[
            DataRequired(
                message="Minimum group size is required."),
            NumberRange(
                min=1,
                message="Minimum group size must be at least 1."),],)

    maximum_people = IntegerField(
        "Maximum People",
        validators=[
            Optional(),
            NumberRange(
                min=1,
                message="Maximum group size must be at least 1."),],)

    # -------------------------------------------------------------------------
    # Price
    # -------------------------------------------------------------------------
    price = DecimalField(
        "Price",
        places=2,
        rounding=None,
        validators=[
            DataRequired(
                message="Price is required."
            ),
            NumberRange(
                min=0,
                message="Price cannot be negative."),],)

    currency = SelectField(
        "Currency",
        choices=[
            ("KES", "KES — Kenyan Shilling"),
            ("USD", "USD — US Dollar"),
            ("EUR", "EUR — Euro"),
            ("GBP", "GBP — British Pound"),],
        default="KES",
        validators=[
            DataRequired(
                message="Please select a currency."),],)

    # -------------------------------------------------------------------------
    # Notes
    # -------------------------------------------------------------------------
    notes = StringField(
        "Notes",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Notes cannot exceed 255 characters."),],)

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------
    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Display order cannot be negative."),],)

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------
    active = BooleanField(
        "Active",
        default=True,)

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------
    submit = SubmitField("Save Pricing")