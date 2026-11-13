"""
===============================================================================
The Uncharted Route
Administrative Experience Category Forms
===============================================================================

Forms for creating, editing, filtering, and managing experience categories.
Media choices are populated by the routes from the central Media Library.
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,)

CATEGORY_COLORS = [
    ("#0F766E", "Teal"),
    ("#2563EB", "Blue"),
    ("#7C3AED", "Purple"),
    ("#DC2626", "Red"),
    ("#EA580C", "Orange"),
    ("#CA8A04", "Gold"),
    ("#15803D", "Green"),
    ("#DB2777", "Pink"),
    ("#0891B2", "Cyan"),
    ("#475569", "Slate"),
]
EXPERIENCE_CATEGORY_FOLDER_NAME = "Experience Categories"

class ExperienceCategoryFieldsMixin:
    """Shared fields for creating and editing experience categories."""

    name = StringField(
        "Category Name",
        validators=[
            DataRequired(),
            Length(min=2, max=150),
        ],
    )

    short_description = StringField(
        "Short Description",
        validators=[
            Optional(),
            Length(max=300),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()],
    )

    # Values are browser-accessible URLs or static paths for selected assets.
    # The routes populate these choices from the Media Library.
    icon = SelectField(
        "Category Icon",
        choices=[("", "Select an icon image")],
        validators=[Optional()],
    )

    color = SelectField(
        "Category Color",
        choices=CATEGORY_COLORS,
        default="#0F766E",
        validators=[Optional()],
    )

    featured_image = SelectField(
        "Featured Image",
        choices=[("", "Select a featured image")],
        validators=[Optional()],
    )

    banner_image = SelectField(
        "Banner Image",
        choices=[("", "Select a banner image")],
        validators=[Optional()],
    )

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            Optional(),
            NumberRange(min=0),
        ],
    )

    featured = BooleanField(
        "Featured Category",
        default=False,
    )

    active = BooleanField(
        "Active",
        default=True,
    )


class AdminExperienceCategoryCreateForm(
    ExperienceCategoryFieldsMixin,
    FlaskForm,
):
    """Form for creating a new experience category."""

    submit = SubmitField("Create Category")


class AdminExperienceCategoryEditForm(
    ExperienceCategoryFieldsMixin,
    FlaskForm,
):
    """Form for editing an existing experience category."""

    submit = SubmitField("Save Changes")


class AdminExperienceCategoryFilterForm(FlaskForm):
    """Search and filter experience categories."""

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    status = SelectField(
        "Status",
        choices=[
            ("", "All Categories"),
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        default="",
        validators=[Optional()],
    )

    featured = SelectField(
        "Featured",
        choices=[
            ("", "All"),
            ("featured", "Featured"),
            ("not_featured", "Not Featured"),
        ],
        default="",
        validators=[Optional()],
    )

    submit = SubmitField("Filter")


class AdminExperienceCategoryStatusForm(FlaskForm):
    """Confirmation form for category status actions."""

    submit = SubmitField("Confirm")


class AdminExperienceCategoryFeaturedForm(FlaskForm):
    """Confirmation form for featured-status actions."""

    submit = SubmitField("Confirm")


class AdminExperienceCategoryOrderForm(FlaskForm):
    """Form for changing category display order."""

    display_order = IntegerField(
        "Display Order",
        validators=[
            DataRequired(),
            NumberRange(min=0),
        ],
    )

    submit = SubmitField("Save Order")
