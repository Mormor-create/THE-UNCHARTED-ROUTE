"""
===============================================================================
The Uncharted Route
Newsletter CMS Forms
===============================================================================
Forms for managing newsletter subscribers and composing newsletters.
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,)

# =============================================================================
# Subscriber Filters
# =============================================================================
class NewsletterSubscriberFilterForm(FlaskForm):
    """Filter newsletter subscribers."""
    search = StringField(
        "Search subscribers",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": "Search by email address...",
        },
    )

    status = SelectField(
        "Subscription status",
        choices=[
            ("", "All subscribers"),
            ("subscribed", "Subscribed"),
            ("unsubscribed", "Unsubscribed"),
            ("verified", "Verified"),
            ("unverified", "Unverified"),
        ],
        validators=[Optional()],
        default="",)

    submit = SubmitField("Filter")

# =============================================================================
# Subscriber Management
# =============================================================================
class NewsletterSubscriberForm(FlaskForm):
    """Create or update a newsletter subscriber."""
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(
                message="An email address is required."
            ),
            Email(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": "subscriber@example.com",
            "autocomplete": "email",},)

    first_name = StringField(
        "First Name",
        validators=[
            Optional(),
            Length(max=100),
        ],
        render_kw={
            "placeholder": "Enter first name",
            "autocomplete": "given-name",},)

    last_name = StringField(
        "Last Name",
        validators=[
            Optional(),
            Length(max=100),
        ],
        render_kw={
            "placeholder": "Enter last name",
            "autocomplete": "family-name",},)

    country = StringField(
        "Country",
        validators=[
            Optional(),
            Length(max=100),
        ],
        render_kw={
            "placeholder": "e.g. Kenya",
            "autocomplete": "country-name",},)

    subscribed = BooleanField(
        "Subscribed",
        default=True,)

    verified = BooleanField(
        "Email verified",
        default=False,)

    marketing_consent = BooleanField(
        "Marketing consent",
        default=False,
    )

    submit = SubmitField("Save Subscriber")

# =============================================================================
# Newsletter Composer
# =============================================================================
class NewsletterComposeForm(FlaskForm):
    """Compose and send a newsletter to eligible subscribers."""

    subject = StringField(
        "Email Subject",
        validators=[
            DataRequired(
                message="Enter an email subject."
            ),
            Length(max=255),
        ],
        render_kw={
            "placeholder": (
                "Your next unforgettable adventure awaits"
            ),
        },
    )

    body = TextAreaField(
        "Newsletter Content",
        validators=[
            DataRequired(
                message="Enter the newsletter content."
            ),
            Length(max=50000),
        ],
        render_kw={
            "rows": 14,
            "placeholder": (
                "Write your newsletter content here..."
            ),
        },
    )

    html_body = TextAreaField(
        "HTML Email Content (Optional)",
        validators=[
            Optional(),
            Length(max=100000),
        ],
        render_kw={
            "rows": 12,
            "placeholder": (
                "Optional HTML version of your newsletter."
            ),
        },
    )

    confirm_send = BooleanField(
        "I confirm that this newsletter should be sent "
        "to all eligible subscribers."
    )

    submit = SubmitField("Send Newsletter")