"""
===============================================================================
The Uncharted Route
Admin Experience FAQ Forms
===============================================================================

Forms used by administrators to create and edit Frequently Asked Questions
attached to experiences.

Supports:

- FAQ question
- FAQ answer
- FAQ category
- Display order
- Featured status
- Active status
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    BooleanField,
    SubmitField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
)


# =============================================================================
# Constants
# =============================================================================

FAQ_CATEGORY_CHOICES = [
    ("General", "General"),
    ("Booking", "Booking"),
    ("Transport", "Transport"),
    ("Accommodation", "Accommodation"),
    ("Meals", "Meals"),
    ("Wildlife", "Wildlife"),
    ("Children", "Children"),
    ("Accessibility", "Accessibility"),
    ("Weather", "Weather"),
]


# =============================================================================
# Base Fields
# =============================================================================

class ExperienceFAQBaseForm(FlaskForm):
    """
    Shared fields for creating and editing experiences FAQs.
    """

    # -------------------------------------------------------------------------
    # Question
    # -------------------------------------------------------------------------

    question = StringField(
        "Question",
        validators=[
            DataRequired(
                message="FAQ question is required."
            ),
            Length(
                min=3,
                max=500,
                message="Question must be between 3 and 500 characters."
            ),
        ],
        render_kw={
            "placeholder": "e.g. Is transport included?",
        },
    )

    # -------------------------------------------------------------------------
    # Answer
    # -------------------------------------------------------------------------

    answer = TextAreaField(
        "Answer",
        validators=[
            DataRequired(
                message="FAQ answer is required."
            ),
            Length(
                min=3,
                message="Answer must contain at least 3 characters."
            ),
        ],
        render_kw={
            "rows": 6,
            "placeholder": (
                "Provide a clear and helpful answer to this question."
            ),
        },
    )

    # -------------------------------------------------------------------------
    # Category
    # -------------------------------------------------------------------------

    category = SelectField(
        "Category",
        choices=FAQ_CATEGORY_CHOICES,
        default="General",
        validators=[
            DataRequired(
                message="FAQ category is required."
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Display Order
    # -------------------------------------------------------------------------

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Display order cannot be negative."
            ),
        ],
        render_kw={
            "min": 0,
        },
    )

    # -------------------------------------------------------------------------
    # Featured
    # -------------------------------------------------------------------------

    featured = BooleanField(
        "Featured",
        default=False,
        description=(
            "Display this FAQ prominently in featured FAQ sections."
        ),
    )

    # -------------------------------------------------------------------------
    # Active
    # -------------------------------------------------------------------------

    active = BooleanField(
        "Active",
        default=True,
        description=(
            "Active FAQs can be displayed on the public experiences page."
        ),
    )


# =============================================================================
# Create Form
# =============================================================================

class ExperienceFAQCreateForm(ExperienceFAQBaseForm):
    """
    Form used to create a new experiences FAQ.
    """

    submit = SubmitField(
        "Create FAQ"
    )


# =============================================================================
# Edit Form
# =============================================================================

class ExperienceFAQEditForm(ExperienceFAQBaseForm):
    """
    Form used to edit an existing experiences FAQ.
    """

    submit = SubmitField(
        "Save Changes"
    )