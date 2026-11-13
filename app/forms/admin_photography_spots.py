from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FloatField,
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
from app.models.destination import Destination

class AdminPhotographySpotForm(FlaskForm):
    """Create and edit reusable photography spots."""

    name = StringField(
        "Spot Name",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    slug = StringField(
        "URL Slug",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()],
    )

    # Destination
    destination_id = SelectField(
        "Destination",
        coerce=lambda value: int(value) if value else None,
        validators=[DataRequired()],
        choices=[],
    )

    location = StringField(
        "Specific Location",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    # Coordinates
    latitude = FloatField(
        "Latitude",
        validators=[
            Optional(),
            NumberRange(min=-90, max=90),
        ],
    )

    longitude = FloatField(
        "Longitude",
        validators=[
            Optional(),
            NumberRange(min=-180, max=180),
        ],
    )

    altitude = IntegerField(
        "Altitude (metres)",
        validators=[
            Optional(),
            NumberRange(min=0),
        ],
    )

    # Photography type
    photography_type = SelectField(
        "Photography Type",
        choices=[
            ("", "Select photography type"),
            ("Wildlife", "Wildlife"),
            ("Landscape", "Landscape"),
            ("Sunrise", "Sunrise"),
            ("Sunset", "Sunset"),
            ("Astro", "Astrophotography (Astro)"),
            ("Portrait", "Portrait"),
            ("Macro", "Macro"),
            ("Birding", "Birding"),
            ("Architecture", "Architecture"),
            ("Street", "Street Photography"),
            ("Cultural & Heritage", "Cultural & Heritage"),
            ("Coastal & Marine", "Coastal & Marine"),
            ("Aerial Photography", "Aerial Photography"),
            ("Food Photography", "Food Photography"),
            ("Botanical", "Botanical"),
            ("Night Photography", "Night Photography"),
            ("Underwater Photography", "Underwater Photography"),
            ("Travel & Documentary", "Travel & Documentary"),
            ("Adventure & Action", "Adventure & Action"),
            ("Events & Festivals", "Events & Festivals"),
        ],
        validators=[Optional()],
    )

    difficulty = SelectField(
        "Difficulty",
        choices=[
            ("Easy", "Easy"),
            ("Moderate", "Moderate"),
            ("Advanced", "Advanced"),
        ],
        validators=[DataRequired()],
        default="Easy",
    )

    # Photography timing
    best_time = StringField(
        "Best Time (Legacy)",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    best_time_to_visit = StringField(
        "Best Time to Visit",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    best_time_to_photograph = StringField(
        "Best Time to Photograph",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    best_season = StringField(
        "Best Season",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    # Photography equipment
    recommended_lens = StringField(
        "Recommended Lens (Legacy)",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    recommended_lenses = TextAreaField(
        "Recommended Lenses",
        validators=[Optional()],
    )

    recommended_equipment = TextAreaField(
        "Recommended Equipment",
        validators=[Optional()],
    )

    # Photography conditions
    lighting_conditions = TextAreaField(
        "Lighting Conditions",
        validators=[Optional()],
    )

    weather_conditions = TextAreaField(
        "Weather Conditions",
        validators=[Optional()],
    )

    # Camera guidance
    camera_settings = TextAreaField(
        "Suggested Camera Settings",
        validators=[Optional()],
    )

    # Visitor information
    accessibility = SelectField(
        "Access Requirements",
        choices=[
            ("", "Select access requirements"),
            ("Easy Walk", "Easy Walk"),
            ("Moderate Walk", "Moderate Walk"),
            ("4x4 Required", "4x4 Required"),
            ("Boat Access", "Boat Access"),
            ("Hiking Required", "Hiking Required"),
        ],
        validators=[Optional()],
    )

    photography_tips = TextAreaField(
        "Photography Tips",
        validators=[Optional()],
    )

    safety_notes = TextAreaField(
        "Safety Notes",
        validators=[Optional()],
    )

    # Display
    featured = BooleanField("Featured Spot")

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField("Save Photography Spot")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        destinations = Destination.query.order_by(
            Destination.name.asc()
        ).all()

        self.destination_id.choices = [
            (None, "Select a destination"),
            *[
                (destination.id, destination.name)
                for destination in destinations
            ],
        ]
