"""
===============================================================================
The Uncharted Route
Admin Stay Review Forms
===============================================================================
"""

from flask_wtf import FlaskForm

from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)

from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    Email,
)


# =============================================================================
# Choices
# =============================================================================

REVIEW_STATUSES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("hidden", "Hidden"),
]


# =============================================================================
# Stay Review Form
# =============================================================================

class AdminStayReviewForm(FlaskForm):
    """
    Create/edit/moderate a Stay review.
    """

    guest_name = StringField(
        "Guest Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    guest_email = StringField(
        "Guest Email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),
        ],
    )

    rating = IntegerField(
        "Rating",
        validators=[
            InputRequired(),
            NumberRange(
                min=1,
                max=5,
                message="Rating must be between 1 and 5."
            ),
        ],
    )

    title = StringField(
        "Review Title",
        validators=[
            Optional(),
            Length(max=200),
        ],
    )

    review = TextAreaField(
        "Review",
        validators=[
            DataRequired(),
        ],
    )

    room_name = StringField(
        "Room / Accommodation",
        validators=[
            Optional(),
            Length(max=200),
        ],
    )

    stay_date = DateField(
        "Stay Date",
        validators=[
            Optional(),
        ],
    )

    status = SelectField(
        "Status",
        choices=REVIEW_STATUSES,
        default="pending",
        validators=[
            DataRequired(),
        ],
    )

    verified_stay = BooleanField(
        "Verified Stay",
        default=False,
    )

    featured = BooleanField(
        "Featured Review",
        default=False,
    )

    admin_response = TextAreaField(
        "Admin Response",
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField(
        "Save Review"
    )