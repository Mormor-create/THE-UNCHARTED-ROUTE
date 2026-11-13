from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Optional,
    NumberRange,
    Length,
)


class ExperienceItineraryForm(FlaskForm):
    """
    Form for creating and editing experiences itinerary items.
    """

    day_number = IntegerField(
        "Day Number",
        validators=[
            DataRequired(),
            NumberRange(min=1),
        ],
        default=1,
    )

    title = StringField(
        "Activity Title",
        validators=[
            DataRequired(),
            Length(max=200),
        ],
    )

    activity_time = StringField(
        "Activity Time",
        validators=[
            Optional(),
            Length(max=50),
        ],
        render_kw={
            "placeholder": "e.g. 08:00"
        },
    )

    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(),
        ],
    )

    display_order = IntegerField(
        "Display Order",
        validators=[
            Optional(),
            NumberRange(min=0),
        ],
        default=0,
    )

    submit = SubmitField(
        "Save Itinerary Item"
    )