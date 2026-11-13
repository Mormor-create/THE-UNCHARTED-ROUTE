"""
===============================================================================
The Uncharted Route
Admin Experience Review Forms
===============================================================================

WTForms definitions for managing customer reviews associated with experiences.

Supports:

• Review creation
• Review editing
• Reviewer information
• Overall and category ratings
• Review content
• Recommendation status
• Verification status
• Featured reviews
• Moderation
• Rejection reasons
• Admin responses
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
)

# =============================================================================
# Constants
# =============================================================================

RATING_CHOICES = [
    (1, "1 — Poor"),
    (2, "2 — Fair"),
    (3, "3 — Good"),
    (4, "4 — Very Good"),
    (5, "5 — Excellent"),
]

COUNTRY_CHOICES = [
    ("", "Select country"),
    ("Kenya", "Kenya"),
    ("Uganda", "Uganda"),
    ("Tanzania", "Tanzania"),
    ("Rwanda", "Rwanda"),
    ("South Africa", "South Africa"),
    ("Nigeria", "Nigeria"),
    ("Ghana", "Ghana"),
    ("United Kingdom", "United Kingdom"),
    ("United States", "United States"),
    ("Canada", "Canada"),
    ("Australia", "Australia"),
    ("Germany", "Germany"),
    ("France", "France"),
    ("Italy", "Italy"),
    ("Spain", "Spain"),
    ("Netherlands", "Netherlands"),
    ("Switzerland", "Switzerland"),
    ("Other", "Other"),
]


# =============================================================================
# Base Review Form
# =============================================================================

class ExperienceReviewBaseForm(FlaskForm):
    """
    Shared fields used by experiences review forms.
    """

    # =========================================================================
    # Reviewer Information
    # =========================================================================

    reviewer_name = StringField(
        "Reviewer Name",
        validators=[
            DataRequired(
                message="Reviewer name is required."
            ),
            Length(
                max=150,
                message="Reviewer name cannot exceed 150 characters."
            ),
        ],
        render_kw={
            "placeholder": "Enter reviewer name"
        },
    )

    reviewer_email = StringField(
        "Reviewer Email",
        validators=[
            Optional(),
            Email(
                message="Please enter a valid email address."
            ),
            Length(
                max=255,
                message="Reviewer email cannot exceed 255 characters."
            ),
        ],
        render_kw={
            "placeholder": "reviewer@example.com"
        },
    )

    reviewer_country = SelectField(
        "Reviewer Country",
        choices=COUNTRY_CHOICES,
        validators=[
            Optional()
        ],
    )

    # =========================================================================
    # Ratings
    # =========================================================================

    overall_rating = SelectField(
        "Overall Rating",
        choices=RATING_CHOICES,
        coerce=int,
        validators=[
            DataRequired(
                message="Overall rating is required."
            ),
            NumberRange(
                min=1,
                max=5,
                message="Rating must be between 1 and 5."
            ),
        ],
    )

    guide_rating = SelectField(
        "Guide Rating",
        choices=[
            (0, "Not provided"),
            *RATING_CHOICES,
        ],
        coerce=int,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=5,
                message="Rating must be between 1 and 5."
            ),
        ],
    )

    transportation_rating = SelectField(
        "Transportation Rating",
        choices=[
            (0, "Not provided"),
            *RATING_CHOICES,
        ],
        coerce=int,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=5,
                message="Rating must be between 1 and 5."
            ),
        ],
    )

    accommodation_rating = SelectField(
        "Accommodation Rating",
        choices=[
            (0, "Not provided"),
            *RATING_CHOICES,
        ],
        coerce=int,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=5,
                message="Rating must be between 1 and 5."
            ),
        ],
    )

    value_rating = SelectField(
        "Value Rating",
        choices=[
            (0, "Not provided"),
            *RATING_CHOICES,
        ],
        coerce=int,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=5,
                message="Rating must be between 1 and 5."
            ),
        ],
    )

    organization_rating = SelectField(
        "Organization Rating",
        choices=[
            (0, "Not provided"),
            *RATING_CHOICES,
        ],
        coerce=int,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=5,
                message="Rating must be between 1 and 5."
            ),
        ],
    )

    # =========================================================================
    # Review Content
    # =========================================================================

    title = StringField(
        "Review Title",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Review title cannot exceed 255 characters."
            ),
        ],
        render_kw={
            "placeholder": "Enter a short review title"
        },
    )

    review = TextAreaField(
        "Review",
        validators=[
            DataRequired(
                message="Review content is required."
            ),
        ],
        render_kw={
            "rows": 7,
            "placeholder": "Enter the customer's review..."
        },
    )

    pros = TextAreaField(
        "Pros",
        validators=[
            Optional()
        ],
        render_kw={
            "rows": 4,
            "placeholder": "What did the guest particularly enjoy?"
        },
    )

    cons = TextAreaField(
        "Cons",
        validators=[
            Optional()
        ],
        render_kw={
            "rows": 4,
            "placeholder": "What could have been improved?"
        },
    )

    travel_date = DateField(
        "Travel Date",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    # =========================================================================
    # Recommendation
    # =========================================================================

    would_recommend = BooleanField(
        "Would Recommend",
        default=True,
    )

    # =========================================================================
    # Verification / Visibility
    # =========================================================================

    verified_booking = BooleanField(
        "Verified Booking",
        default=False,
    )

    featured = BooleanField(
        "Featured Review",
        default=False,
    )

    # =========================================================================
    # Moderation
    # =========================================================================

    approved = BooleanField(
        "Approved",
        default=False,
    )

    rejected = BooleanField(
        "Rejected",
        default=False,
    )

    rejection_reason = TextAreaField(
        "Rejection Reason",
        validators=[
            Optional()
        ],
        render_kw={
            "rows": 4,
            "placeholder": "Explain why this review was rejected..."
        },
    )

    # =========================================================================
    # Admin Response
    # =========================================================================

    admin_response = TextAreaField(
        "Admin Response",
        validators=[
            Optional()
        ],
        render_kw={
            "rows": 6,
            "placeholder": "Enter an official response to the customer..."
        },
    )

    admin_responded_by = StringField(
        "Responded By",
        validators=[
            Optional(),
            Length(
                max=150,
                message="Name cannot exceed 150 characters."
            ),
        ],
        render_kw={
            "placeholder": "Administrator name"
        },
    )


# =============================================================================
# Create Form
# =============================================================================

class ExperienceReviewCreateForm(
    ExperienceReviewBaseForm
):
    """
    Form used to create a new experiences review.
    """

    submit = SubmitField(
        "Create Review"
    )


# =============================================================================
# Edit Form
# =============================================================================

class ExperienceReviewEditForm(
    ExperienceReviewBaseForm
):
    """
    Form used to edit an existing experiences review.
    """

    submit = SubmitField(
        "Save Changes"
    )


# =============================================================================
# Moderation Form
# =============================================================================

class ExperienceReviewModerationForm(
    FlaskForm
):
    """
    Form used for approving or rejecting an existing review.
    """

    approved = BooleanField(
        "Approve Review",
        default=False,
    )

    rejected = BooleanField(
        "Reject Review",
        default=False,
    )

    rejection_reason = TextAreaField(
        "Rejection Reason",
        validators=[
            Optional()
        ],
        render_kw={
            "rows": 4,
            "placeholder": "Provide a reason when rejecting a review..."
        },
    )

    submit = SubmitField(
        "Save Moderation Status"
    )


# =============================================================================
# Admin Response Form
# =============================================================================

class ExperienceReviewResponseForm(
    FlaskForm
):
    """
    Form used by administrators to respond to a customer review.
    """

    admin_response = TextAreaField(
        "Admin Response",
        validators=[
            DataRequired(
                message="Response content is required."
            ),
        ],
        render_kw={
            "rows": 6,
            "placeholder": "Write the official response..."
        },
    )

    admin_responded_by = StringField(
        "Responded By",
        validators=[
            DataRequired(
                message="Administrator name is required."
            ),
            Length(
                max=150,
                message="Administrator name cannot exceed 150 characters."
            ),
        ],
        render_kw={
            "placeholder": "Administrator name"
        },
    )

    submit = SubmitField(
        "Post Response"
    )


# =============================================================================
# Search / Filter Form
# =============================================================================

class ExperienceReviewFilterForm(
    FlaskForm
):
    """
    Form used to filter reviews in the administration interface.

    This form intentionally contains no CSRF-protected submit action because
    it is intended for GET-based filtering.
    """

    reviewer_name = StringField(
        "Reviewer",
        validators=[
            Optional()
        ],
        render_kw={
            "placeholder": "Search reviewer..."
        },
    )

    rating = SelectField(
        "Overall Rating",
        choices=[
            ("", "All ratings"),
            *[
                (str(value), label)
                for value, label in RATING_CHOICES
            ],
        ],
        validators=[
            Optional()
        ],
    )

    verified = SelectField(
        "Verification",
        choices=[
            ("", "All"),
            ("verified", "Verified"),
            ("unverified", "Unverified"),
        ],
        validators=[
            Optional()
        ],
    )

    moderation = SelectField(
        "Moderation",
        choices=[
            ("", "All"),
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        validators=[
            Optional()
        ],
    )

    featured = SelectField(
        "Featured",
        choices=[
            ("", "All"),
            ("featured", "Featured"),
            ("not_featured", "Not Featured"),
        ],
        validators=[
            Optional()
        ],
    )

    submit = SubmitField(
        "Filter Reviews"
    )