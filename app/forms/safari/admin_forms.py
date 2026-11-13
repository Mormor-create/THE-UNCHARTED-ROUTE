"""Admin forms for managing safari destinations, properties and rates."""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    URL,
    ValidationError,
)
from app.forms.safari.field_utils import coerce_optional_int

class SafariDestinationForm(FlaskForm):
    name = StringField(
        "Destination name",
        validators=[DataRequired(), Length(max=150)],
    )
    slug = StringField(
        "URL slug",
        validators=[Optional(), Length(max=180)],
    )
    short_description = StringField(
        "Short description",
        validators=[Optional(), Length(max=500)],
    )
    introduction = TextAreaField("Introduction", validators=[Optional()])
    history = TextAreaField("History", validators=[Optional()])
    landscape_and_wildlife = TextAreaField(
        "Landscape and wildlife",
        validators=[Optional()],
    )
    conservation_story = TextAreaField(
        "Conservation story",
        validators=[Optional()],
    )
    travel_information = TextAreaField(
        "Travel information",
        validators=[Optional()],
    )

    media_folder_id = SelectField(
        "Media folder",
        coerce=coerce_optional_int,
        choices=[],
        validators=[Optional()],
    )
    card_media_asset_id = SelectField(
        "Safari Card Image",
        coerce=coerce_optional_int,
        choices=[],
        validators=[Optional()],
    )
    hero_media_asset_id = SelectField(
        "Safari hero image",
        coerce=coerce_optional_int,
        choices=[],
        validators=[Optional()],
    )

    display_order = IntegerField(
        "Display order",
        default=0,
        validators=[NumberRange(min=0)],
    )
    active = BooleanField("Active", default=True)
    featured = BooleanField("Featured", default=False)

    submit = SubmitField("Save destination")


class SafariPropertyForm(FlaskForm):
    destination_id = SelectField(
        "Destination",
        coerce=coerce_optional_int,
        choices=[],
        validators=[DataRequired()],
    )

    name = StringField(
        "Property name",
        validators=[DataRequired(), Length(max=200)],
    )
    slug = StringField(
        "URL slug",
        validators=[Optional(), Length(max=220)],
    )
    property_type = SelectField(
        "Property type",
        choices=[
            ("lodge", "Safari lodge"),
            ("hotel", "Hotel"),
            ("tented_camp", "Tented camp"),
            ("villa", "Villa"),
            ("mobile_camp", "Mobile camp"),
            ("private_conservancy", "Private conservancy accommodation"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )

    short_description = StringField(
        "Short description",
        validators=[Optional(), Length(max=500)],
    )
    overview = TextAreaField("Overview", validators=[Optional()])
    property_story = TextAreaField("Property story", validators=[Optional()])
    location_description = TextAreaField(
        "Location description",
        validators=[Optional()],
    )
    location_name = StringField(
        "Location name",
        validators=[Optional(), Length(max=200)],
    )

    accommodation_details = TextAreaField(
        "Accommodation details",
        validators=[Optional()],
    )
    facilities = TextAreaField("Facilities", validators=[Optional()])
    dining_information = TextAreaField(
        "Dining information",
        validators=[Optional()],
    )
    activities = TextAreaField("Activities", validators=[Optional()])
    wildlife_experience = TextAreaField(
        "Wildlife experience",
        validators=[Optional()],
    )
    transport_information = TextAreaField(
        "Transport information",
        validators=[Optional()],
    )
    check_in_information = TextAreaField(
        "Check-in information",
        validators=[Optional()],
    )
    check_out_information = TextAreaField(
        "Check-out information",
        validators=[Optional()],
    )
    child_policy = TextAreaField("Child policy", validators=[Optional()])
    accessibility_information = TextAreaField(
        "Accessibility information",
        validators=[Optional()],
    )
    booking_conditions = TextAreaField(
        "Booking conditions",
        validators=[Optional()],
    )

    official_website_url = StringField(
        "Official website",
        validators=[Optional(), URL(), Length(max=500)],
    )

    media_folder_id = SelectField(
        "Property media folder",
        coerce=coerce_optional_int,
        choices=[],
        validators=[Optional()],
    )

    display_order = IntegerField(
        "Display order",
        default=0,
        validators=[NumberRange(min=0)],
    )
    active = BooleanField("Active", default=True)
    featured = BooleanField("Featured", default=False)

    submit = SubmitField("Save property")


class SafariPropertyMediaForm(FlaskForm):
    media_asset_id = SelectField(
        "Media asset",
        coerce=coerce_optional_int,
        choices=[],
        validators=[DataRequired()],
    )
    usage = SelectField(
        "Image usage",
        choices=[
            ("hero", "Hero"),
            ("gallery", "Gallery"),
            ("room", "Accommodation / room"),
            ("dining", "Dining"),
            ("activity", "Activity"),
        ],
        validators=[DataRequired()],
    )
    caption = StringField(
        "Caption",
        validators=[Optional(), Length(max=300)],
    )
    alt_text = StringField(
        "Accessibility description",
        validators=[Optional(), Length(max=300)],
    )
    display_order = IntegerField(
        "Display order",
        default=0,
        validators=[NumberRange(min=0)],
    )
    is_primary = BooleanField("Primary image", default=False)
    active = BooleanField("Active", default=True)

    submit = SubmitField("Save gallery image")

class SafariPackageOptionForm(FlaskForm):
    name = StringField(
        "Package option name",
        validators=[DataRequired(), Length(max=200)],
    )
    slug = StringField(
        "URL slug",
        validators=[Optional(), Length(max=220)],
    )
    summary = StringField(
        "Summary",
        validators=[Optional(), Length(max=500)],
    )
    description = TextAreaField("Description", validators=[Optional()])

    duration_days = SelectField(
        "Duration in days",
        coerce=coerce_optional_int,
        choices=[(n, f"{n} days") for n in range(3, 11)],
        validators=[DataRequired()],
    )
    duration_nights = SelectField(
        "Duration in nights",
        coerce=coerce_optional_int,
        choices=[(n, f"{n} nights") for n in range(2, 10)],
        validators=[DataRequired()],
    )

    display_currency = SelectField(
        "Display currency",
        choices=[
            ("KES", "KES — Kenyan Shilling"),
            ("USD", "USD — US Dollar"),
            ("EUR", "EUR — Euro"),
            ("GBP", "GBP — British Pound"),
        ],
        validators=[DataRequired()],
    )

    inclusions = TextAreaField(
        "Inclusions",
        description="Enter one item per line.",
        validators=[Optional()],
    )
    exclusions = TextAreaField(
        "Exclusions",
        description="Enter one item per line.",
        validators=[Optional()],
    )
    transport_details = TextAreaField(
        "Transport arrangements",
        validators=[Optional()],
    )
    meals_information = TextAreaField(
        "Meals and board basis",
        validators=[Optional()],
    )
    important_information = TextAreaField(
        "Important information",
        validators=[Optional()],
    )

    display_order = IntegerField(
        "Display order",
        default=0,
        validators=[NumberRange(min=0)],
    )
    active = BooleanField("Active", default=True)
    featured = BooleanField("Featured", default=False)

    submit = SubmitField("Save duration option")

    def validate_duration_nights(self, field):
        if (
            self.duration_days.data is not None
            and field.data is not None
            and field.data >= self.duration_days.data
        ):
            raise ValidationError(
                "The number of nights must be less than the number of days."
            )


class SafariItineraryDayForm(FlaskForm):
    day_number = IntegerField(
        "Day number",
        validators=[DataRequired(), NumberRange(min=1, max=10)],
    )
    title = StringField(
        "Day title",
        validators=[DataRequired(), Length(max=200)],
    )
    description = TextAreaField(
        "Day description",
        validators=[DataRequired()],
    )
    morning_activities = TextAreaField(
        "Morning activities",
        validators=[Optional()],
    )
    afternoon_activities = TextAreaField(
        "Afternoon activities",
        validators=[Optional()],
    )
    evening_activities = TextAreaField(
        "Evening activities",
        validators=[Optional()],
    )
    meals_included = StringField(
        "Meals included",
        validators=[Optional(), Length(max=200)],
    )
    overnight_location = StringField(
        "Overnight location",
        validators=[Optional(), Length(max=200)],
    )
    transport_details = TextAreaField(
        "Transport details",
        validators=[Optional()],
    )
    notes = TextAreaField("Additional notes", validators=[Optional()])

    submit = SubmitField("Save itinerary day")


class SafariPackageRateForm(FlaskForm):
    name = StringField(
        "Rate name",
        validators=[DataRequired(), Length(max=180)],
    )

    pricing_basis = SelectField(
        "Pricing basis",
        choices=[
            ("per_person_sharing", "Per person sharing"),
            ("per_person", "Per person"),
            ("per_person_single", "Per person, single occupancy"),
            ("per_room_per_night", "Per room, per night"),
            ("per_room_per_stay", "Per room, entire stay"),
            ("per_group", "Per group"),
            ("per_vehicle", "Per vehicle"),
            ("exclusive_use", "Exclusive use"),
        ],
        validators=[DataRequired()],
    )

    guest_category = SelectField(
        "Guest category",
        choices=[
            ("all", "All guests"),
            ("adult", "Adult"),
            ("child", "Child"),
            ("infant", "Infant"),
        ],
        validators=[DataRequired()],
    )

    min_guest_age = IntegerField(
        "Minimum age",
        validators=[Optional(), NumberRange(min=0, max=120)],
    )
    max_guest_age = IntegerField(
        "Maximum age",
        validators=[Optional(), NumberRange(min=0, max=120)],
    )

    occupancy_type = SelectField(
        "Occupancy",
        choices=[
            ("any", "Any occupancy"),
            ("sharing", "Sharing"),
            ("single", "Single"),
            ("double", "Double"),
            ("triple", "Triple"),
            ("family", "Family"),
        ],
        validators=[DataRequired()],
    )

    min_guests = IntegerField(
        "Minimum guests",
        default=1,
        validators=[DataRequired(), NumberRange(min=1)],
    )
    max_guests = IntegerField(
        "Maximum guests",
        validators=[Optional(), NumberRange(min=1)],
    )

    amount = DecimalField(
        "Rate amount",
        places=2,
        validators=[DataRequired(), NumberRange(min=0)],
    )
    currency = SelectField(
        "Currency",
        choices=[
            ("KES", "KES"),
            ("USD", "USD"),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
        ],
        validators=[DataRequired()],
    )

    season_name = StringField(
        "Season",
        validators=[Optional(), Length(max=100)],
    )
    valid_from = DateField(
        "Valid from",
        format="%Y-%m-%d",
        validators=[Optional()],
    )
    valid_to = DateField(
        "Valid until",
        format="%Y-%m-%d",
        validators=[Optional()],
    )

    board_basis = StringField(
        "Board basis",
        validators=[Optional(), Length(max=60)],
    )
    supplier_rate_reference = StringField(
        "Supplier rate reference",
        validators=[Optional(), Length(max=150)],
    )
    rate_notes = TextAreaField("Rate notes", validators=[Optional()])

    active = BooleanField("Active", default=True)
    display_order = IntegerField(
        "Display order",
        default=0,
        validators=[NumberRange(min=0)],
    )

    submit = SubmitField("Save rate")

    def validate_max_guest_age(self, field):
        minimum = self.min_guest_age.data
        maximum = field.data

        if minimum is not None and maximum is not None and maximum < minimum:
            raise ValidationError(
                "Maximum age must be greater than or equal to minimum age."
            )

    def validate_max_guests(self, field):
        minimum = self.min_guests.data
        maximum = field.data

        if minimum is not None and maximum is not None and maximum < minimum:
            raise ValidationError(
                "Maximum guests must be greater than or equal to minimum guests."
            )

    def validate_valid_to(self, field):
        start = self.valid_from.data
        end = field.data

        if start is not None and end is not None and end < start:
            raise ValidationError(
                "The end date must be on or after the start date."
            )