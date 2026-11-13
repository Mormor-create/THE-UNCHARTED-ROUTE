"""
Shared Add-on Catalogue Forms
"""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    Regexp,
    ValidationError,)

class AddonCatalogueForm(FlaskForm):
    code = StringField(
        "Add-on Code",
        validators=[
            DataRequired(),
            Length(max=50),
            Regexp(
                r"^[A-Za-z0-9_-]+$",
                message="Use letters, numbers, hyphens or underscores.",
            ),
        ],
    )

    name = StringField(
        "Name", validators=[DataRequired(), Length(max=160)]
    )
    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(max=180),
            Regexp(
                r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
                message="Use lowercase letters, numbers and hyphens.",
            ),
        ],
    )
    short_description = StringField(
        "Short Description", validators=[Optional(), Length(max=300)]
    )
    description = TextAreaField("Full Description", validators=[Optional()])

    category = SelectField(
        "Category",
        choices=[
            ("transport", "Transport"),
            ("accommodation", "Accommodation"),
            ("activity", "Activity / Excursion"),
            ("equipment", "Equipment"),
            ("meal", "Meals"),
            ("insurance", "Insurance"),
            ("guide", "Guide"),
            ("park_fee", "Park / Conservation Fee"),
            ("upgrade", "Upgrade"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )

    applicable_services = SelectMultipleField(
        "Applicable Services",
        choices=[
            ("experience", "Experiences"),
            ("safari", "Safaris"),
            ("stay", "Stays"),
            ("destination_journey", "Destination Journeys"),
        ],
        validators=[DataRequired()],
        coerce=str,
    )

    pricing_basis = SelectField(
        "Pricing Basis",
        choices=[
            ("per_booking", "Per Booking"),
            ("per_person", "Per Person"),
            ("per_day", "Per Day"),
            ("per_night", "Per Night"),
            ("per_unit", "Per Unit"),
        ],
        validators=[DataRequired()],
    )

    unit_price = DecimalField(
        "Unit Price",
        places=2,
        validators=[InputRequired(), NumberRange(min=0)],
    )
    currency = SelectField(
        "Currency",
        choices=[
            (code, code)
            for code in (
                "KES", "USD", "EUR", "GBP", "UGX",
                "TZS", "ZAR", "NGN", "GHS",
            )
        ],
        validators=[DataRequired()],
    )

    minimum_quantity = IntegerField(
        "Minimum Quantity",
        default=1,
        validators=[InputRequired(), NumberRange(min=1)],
    )
    maximum_quantity = IntegerField(
        "Maximum Quantity", validators=[Optional(), NumberRange(min=1)]
    )
    available_quantity = IntegerField(
        "Available Inventory",
        validators=[Optional(), NumberRange(min=0)],
    )

    available_from = DateField(
        "Available From", validators=[Optional()]
    )
    available_until = DateField(
        "Available Until", validators=[Optional()]
    )

    image_url = StringField(
        "Image URL", validators=[Optional(), Length(max=500)]
    )

    is_optional = BooleanField("Optional Add-on", default=True)
    can_be_booked_independently = BooleanField(
        "Can Be Booked Independently"
    )
    requires_confirmation = BooleanField("Requires Manual Confirmation")
    featured = BooleanField("Featured")
    active = BooleanField("Active", default=True)
    display_order = IntegerField(
        "Display Order", default=0, validators=[InputRequired()]
    )

    submit = SubmitField("Save Add-on")

    def validate_maximum_quantity(self, field):
        if (
            field.data is not None
            and self.minimum_quantity.data is not None
            and field.data < self.minimum_quantity.data
        ):
            raise ValidationError(
                "Maximum quantity cannot be less than minimum quantity."
            )

    def validate_available_until(self, field):
        if (
            field.data
            and self.available_from.data
            and field.data < self.available_from.data
        ):
            raise ValidationError(
                "The end date cannot be earlier than the start date.")