"""
===============================================================================
The Uncharted Route
Legal & Help Admin Forms
===============================================================================
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

class LegalHelpPageForm(FlaskForm):
    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    page_type = SelectField(
        "Page Type",
        choices=[
            ("about", "About"),
            ("faq", "FAQ"),
            ("privacy", "Privacy Policy"),
            ("terms", "Terms & Conditions"),
        ],
        validators=[DataRequired()],
    )

    eyebrow = StringField(
        "Eyebrow",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    intro = TextAreaField(
        "Introduction",
        validators=[Optional()],
    )

    meta_title = StringField(
        "Meta Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    meta_description = TextAreaField(
        "Meta Description",
        validators=[Optional()],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField("Save Page")


class LegalHelpSectionForm(FlaskForm):
    section_key = StringField(
        "Section Key",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    section_type = SelectField(
        "Section Type",
        choices=[
            ("hero", "Hero"),
            ("content", "Content"),
            ("cards", "Cards"),
            ("split", "Split"),
            ("feature", "Feature"),
            ("faq", "FAQ"),
            ("legal", "Legal Content"),
            ("cta", "Call To Action"),
        ],
        validators=[DataRequired()],
    )

    eyebrow = StringField(
        "Eyebrow",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    title = StringField(
        "Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    body = TextAreaField(
        "Body",
        validators=[Optional()],
    )

    secondary_body = TextAreaField(
        "Secondary Body",
        validators=[Optional()],
    )

    primary_cta_label = StringField(
        "Primary CTA Label",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    primary_cta_url = StringField(
        "Primary CTA URL",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    secondary_cta_label = StringField(
        "Secondary CTA Label",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    secondary_cta_url = StringField(
        "Secondary CTA URL",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    sort_order = IntegerField(
        "Sort Order",
        default=0,
        validators=[
            NumberRange(min=0),
        ],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField("Save Section")


class LegalHelpItemForm(FlaskForm):
    item_type = SelectField(
        "Item Type",
        choices=[
            ("content", "Content"),
            ("faq", "FAQ"),
            ("card", "Card"),
            ("legal", "Legal Section"),
        ],
        validators=[DataRequired()],
    )

    eyebrow = StringField(
        "Eyebrow",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    title = StringField(
        "Title / Question",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    body = TextAreaField(
        "Answer / Content",
        validators=[Optional()],
    )

    link_label = StringField(
        "Link Label",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    link_url = StringField(
        "Link URL",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    sort_order = IntegerField(
        "Sort Order",
        default=0,
        validators=[
            NumberRange(min=0),
        ],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField("Save Item")