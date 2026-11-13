"""
===============================================================================
The Uncharted Route — Accessibility Profiles Admin Forms
===============================================================================

WTForms used by the Accessibility Profiles CMS.

Forms
-----

    AdminAccessibilityFilterForm
    AdminAccessibilityForm
    AdminAccessibilityDeleteForm

===============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
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

FITNESS_LEVELS = [
    ("Very Low", "Very Low"),
    ("Low", "Low"),
    ("Low to Moderate", "Low to Moderate"),
    ("Moderate", "Moderate"),
    ("Good", "Good"),
    ("High", "High"),
    ("Extreme", "Extreme"),
]


# =============================================================================
# Filter Form
# =============================================================================

class AdminAccessibilityFilterForm(FlaskForm):
    """
    Accessibility profile listing/filter form.

    This form is intended for GET requests.
    """

    class Meta:
        csrf = False

    q = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=120),
        ],
    )

    active = SelectField(
        "Status",
        choices=[
            ("", "All statuses"),
            ("1", "Active"),
            ("0", "Inactive"),
        ],
        default="",
    )

    wheelchair_accessible = SelectField(
        "Wheelchair Access",
        choices=[
            ("", "All"),
            ("1", "Accessible"),
            ("0", "Not accessible"),
        ],
        default="",
    )

    child_friendly = SelectField(
        "Child Friendly",
        choices=[
            ("", "All"),
            ("1", "Yes"),
            ("0", "No"),
        ],
        default="",
    )

    fitness_level = SelectField(
        "Fitness Level",
        choices=[
            ("", "All fitness levels"),
        ] + FITNESS_LEVELS,
        default="",
    )

    submit = SubmitField(
        "Filter"
    )


# =============================================================================
# Create / Edit Form
# =============================================================================

class AdminAccessibilityForm(FlaskForm):
    """
    Create or edit an Accessibility profile.
    """

    # =========================================================================
    # Basic Information
    # =========================================================================

    name = StringField(
        "Profile Name",
        validators=[
            DataRequired(
                message="Accessibility profile name is required."
            ),
            Length(
                max=120,
                message="Profile name cannot exceed 120 characters."
            ),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            Optional(),
            Length(
                max=150,
                message="Slug cannot exceed 150 characters."
            ),
        ],
    )

    summary = TextAreaField(
        "Summary",
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # Mobility
    # =========================================================================

    wheelchair_accessible = BooleanField(
        "Wheelchair Accessible"
    )

    stroller_friendly = BooleanField(
        "Stroller Friendly"
    )

    walking_required = BooleanField(
        "Walking Required",
        default=True,
    )

    hiking_required = BooleanField(
        "Hiking Required"
    )

    uneven_terrain = BooleanField(
        "Uneven Terrain"
    )

    stairs_required = BooleanField(
        "Stairs Required"
    )

    # =========================================================================
    # Guest Suitability
    # =========================================================================

    child_friendly = BooleanField(
        "Child Friendly",
        default=True,
    )

    elderly_friendly = BooleanField(
        "Elderly Friendly",
        default=True,
    )

    pregnancy_friendly = BooleanField(
        "Pregnancy Friendly",
        default=True,
    )

    pet_friendly = BooleanField(
        "Pet Friendly"
    )

    # =========================================================================
    # Physical Requirements
    # =========================================================================

    minimum_fitness_level = SelectField(
        "Minimum Fitness Level",
        choices=FITNESS_LEVELS,
        default="Easy",
        validators=[
            DataRequired(
                message="Please select a fitness level."
            ),
        ],
    )

    maximum_altitude_meters = IntegerField(
        "Maximum Altitude (metres)",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Altitude cannot be negative."
            ),
        ],
    )

    # =========================================================================
    # Facilities
    # =========================================================================

    accessible_restrooms = BooleanField(
        "Accessible Restrooms"
    )

    changing_facilities = BooleanField(
        "Changing Facilities"
    )

    medical_support_available = BooleanField(
        "Medical Support Available"
    )

    # =========================================================================
    # Dietary Support
    # =========================================================================

    vegetarian_available = BooleanField(
        "Vegetarian Available"
    )

    vegan_available = BooleanField(
        "Vegan Available"
    )

    halal_available = BooleanField(
        "Halal Available"
    )

    kosher_available = BooleanField(
        "Kosher Available"
    )

    gluten_free_available = BooleanField(
        "Gluten-Free Available"
    )

    allergy_support = BooleanField(
        "Allergy Support"
    )

    # =========================================================================
    # Communication
    # =========================================================================

    multilingual_guides = BooleanField(
        "Multilingual Guides",
        default=True,
    )

    sign_language_available = BooleanField(
        "Sign Language Available"
    )

    braille_materials = BooleanField(
        "Braille Materials"
    )

    audio_guides = BooleanField(
        "Audio Guides"
    )

    # =========================================================================
    # Additional Information
    # =========================================================================

    notes = TextAreaField(
        "Additional Notes",
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # Status
    # =========================================================================

    active = BooleanField(
        "Active",
        default=True,
    )

    # =========================================================================
    # Submit
    # =========================================================================

    submit = SubmitField(
        "Save Accessibility Profile"
    )


# =============================================================================
# Delete Form
# =============================================================================

class AdminAccessibilityDeleteForm(FlaskForm):
    """
    Confirmation form for deleting an accessibility profile.
    """

    submit = SubmitField(
        "Delete Accessibility Profile"
    )