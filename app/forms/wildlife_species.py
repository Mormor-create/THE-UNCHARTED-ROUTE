from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional


class WildlifeSpeciesForm(FlaskForm):
    common_name = StringField(
        "Common Name",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    scientific_name = StringField(
        "Scientific Name",
        validators=[Optional(), Length(max=255)],
    )

    family = StringField(
        "Family",
        validators=[Optional(), Length(max=255)],
    )

    animal_class = SelectField(
        "Animal Class",
        choices=[
            ("", "Select animal class"),
            ("Mammal", "Mammal"),
            ("Bird", "Bird"),
            ("Reptile", "Reptile"),
            ("Amphibian", "Amphibian"),
            ("Fish", "Fish"),
            ("Insect", "Insect"),
        ],
        validators=[DataRequired()],
    )

    category = SelectField(
        "Category",
        choices=[
            ("", "Select category"),
            ("Big Five", "Big Five"),
            ("Big Cats", "Big Cats"),
            ("Herbivore", "Herbivore"),
            ("Carnivore", "Carnivore"),
            ("Bird of Prey", "Bird of Prey"),
            ("Water Bird", "Water Bird"),
            ("Marine Life", "Marine Life"),
            ("Primate", "Primate"),
        ],
        validators=[Optional()],
    )

    conservation_status = SelectField(
        "Conservation Status",
        choices=[
            ("", "Select conservation status"),
            ("Least Concern", "Least Concern"),
            ("Near Threatened", "Near Threatened"),
            ("Vulnerable", "Vulnerable"),
            ("Endangered", "Endangered"),
            ("Critically Endangered", "Critically Endangered"),
        ],
        validators=[Optional()],
    )

    protected = BooleanField("Protected Species")
    endemic = BooleanField("Endemic Species")

    description = TextAreaField(
        "Description",
        validators=[Optional()],
    )

    interesting_fact = TextAreaField(
        "Interesting Fact",
        validators=[Optional()],
    )

    habitat = StringField(
        "Habitat",
        validators=[Optional(), Length(max=255)],
    )

    diet = StringField(
        "Diet",
        validators=[Optional(), Length(max=255)],
    )

    best_viewing_time = StringField(
        "Best Viewing Time",
        validators=[Optional(), Length(max=255)],
    )

    photography_difficulty = SelectField(
        "Photography Difficulty",
        choices=[
            ("Easy", "Easy"),
            ("Medium", "Medium"),
            ("Difficult", "Difficult"),
        ],
        default="Medium",
        validators=[DataRequired()],
    )

    featured = BooleanField("Featured Species")
    active = BooleanField("Active", default=True)

    submit = SubmitField("Save Wildlife Species")