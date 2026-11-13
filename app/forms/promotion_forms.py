"""
===============================================================================
The Uncharted Route
Promotion CMS and Inquiry Forms
===============================================================================

Forms for:
- Creating and managing promotional offers.
- Submitting public promotion inquiries.
- Managing promotion inquiry follow-ups.

===============================================================================
"""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    ValidationError,)

# =============================================================================
# Promotion CMS Form
# =============================================================================
class PromotionForm(FlaskForm):
    """Create or update a poster-first promotion."""

    title = StringField(
        "Promotion Title",
        validators=[
            DataRequired(message="Enter a promotion title."),
            Length(max=200),],)

    poster_media_asset_id = SelectField(
        "Promotion Poster",
        coerce=lambda value: int(value) if value not in (None, "") else 0,
        choices=[
            (0, "Choose a poster from the Promotions folder"),
        ],
        validators=[
            DataRequired(
                message="Please select a promotion poster."),],)

    description = TextAreaField(
        "Short Description (Optional)",
        validators=[
            Optional(),
            Length(max=5000),],)

    starts_at = DateField(
        "Offer Starts",
        format="%Y-%m-%d",
        validators=[
            Optional(),],)

    ends_at = DateField(
        "Offer Ends",
        format="%Y-%m-%d",
        validators=[
            Optional(),],)

    status = SelectField(
        "Publication Status",
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
        ],
        validators=[
            DataRequired(),],)

    show_on_homepage = BooleanField(
        "Show this offer on the homepage",
        default=False,)
    submit = SubmitField("Save Promotion")

    def validate_poster_media_asset_id(self, field):
        if not field.data or field.data <= 0:
            raise ValidationError(
                "Please select a poster from the Promotions folder."
            )

    def validate_ends_at(self, field):
        if (
            field.data
            and self.starts_at.data
            and field.data < self.starts_at.data
        ):
            raise ValidationError(
                "The end date cannot be earlier than the start date."
            )


# =============================================================================
# Public Promotion Inquiry Form
# =============================================================================
class PromotionInquiryForm(FlaskForm):
    """Allow visitors to enquire about a promotional offer."""

    customer_name = StringField(
        "Full Name",
        validators=[
            DataRequired(message="Please enter your full name."),
            Length(max=150),],)

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Please enter your email address."),
            Email(message="Enter a valid email address."),
            Length(max=255),],)

    phone = StringField(
        "Phone / WhatsApp Number",
        validators=[
            DataRequired(message="Please enter your phone number."),
            Length(max=40),
        ],
    )

    country = StringField(
        "Country",
        validators=[
            Optional(),
            Length(max=100),],)

    contact_method = SelectField(
        "Preferred Contact Method",
        choices=[
            ("email", "Email"),
            ("phone", "Phone Call"),
            ("whatsapp", "WhatsApp"),
        ],
        default="email",
        validators=[
            DataRequired(),],)

    message = TextAreaField(
        "Your Inquiry",
        validators=[
            DataRequired(
                message="Please tell us what you would like to know."
            ),
            Length(
                min=10,
                max=5000,
                message="Your inquiry must be between 10 and 5000 characters.",),],)

    submit = SubmitField("Send Inquiry")

# =============================================================================
# Admin Promotion Inquiry Management Form
# =============================================================================
class PromotionInquiryUpdateForm(FlaskForm):
    """Allow administrators to update inquiry progress and notes."""

    status = SelectField(
        "Inquiry Status",
        choices=[
            ("new", "New"),
            ("in_progress", "In Progress"),
            ("contacted", "Contacted"),
            ("converted", "Converted"),
            ("closed", "Closed"),],
        validators=[
            DataRequired(),],)

    admin_notes = TextAreaField(
        "Internal Notes",
        validators=[
            Optional(),
            Length(max=10000),],)

    submit = SubmitField("Update Inquiry")