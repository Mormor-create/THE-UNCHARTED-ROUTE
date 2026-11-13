# =============================================================================
# The Uncharted Route
# Booking Add-on Forms
# =============================================================================

from flask_wtf import FlaskForm
from wtforms import (
    DecimalField,
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


ADDON_TYPES = [
    ("transport", "Transport"),
    ("accommodation", "Accommodation"),
    ("activity", "Activity"),
    ("equipment", "Equipment"),
    ("meal", "Meal"),
    ("insurance", "Insurance"),
    ("guide", "Guide service"),
    ("other", "Other"),
]

PRICING_BASES = [
    ("per_booking", "Per booking"),
    ("per_person", "Per person"),
    ("per_day", "Per day"),
    ("per_night", "Per night"),
    ("per_unit", "Per unit"),
]

ADDON_STATUSES = [
    ("selected", "Selected"),
    ("confirmed", "Confirmed"),
    ("fulfilled", "Fulfilled"),
    ("cancelled", "Cancelled"),
]

CURRENCIES = [
    ("KES", "KES — Kenyan Shilling"),
    ("USD", "USD — US Dollar"),
    ("EUR", "EUR — Euro"),
    ("GBP", "GBP — British Pound"),
    ("UGX", "UGX — Ugandan Shilling"),
    ("TZS", "TZS — Tanzanian Shilling"),
    ("ZAR", "ZAR — South African Rand"),
    ("NGN", "NGN — Nigerian Naira"),
    ("GHS", "GHS — Ghanaian Cedi"),
]


class BookingAddonForm(FlaskForm):
    """Create or edit a booking add-on."""

    addon_code = StringField(
        "Add-on code",
        validators=[Optional(), Length(max=60)],
    )
    addon_type = SelectField(
        "Add-on type",
        choices=ADDON_TYPES,
        default="other",
        validators=[DataRequired()],
    )
    experience_addon_id = SelectField(
        "Experience add-on catalogue item",
        coerce=int,
        choices=[(0, "No catalogue link")],
        default=0,
        validators=[Optional()],
    )

    name_snapshot = StringField(
        "Add-on name",
        validators=[DataRequired(), Length(max=255)],
    )
    description_snapshot = TextAreaField(
        "Description snapshot",
        validators=[Optional(), Length(max=10000)],
    )
    pricing_basis = SelectField(
        "Pricing basis",
        choices=PRICING_BASES,
        default="per_booking",
        validators=[DataRequired()],
    )

    quantity = IntegerField(
        "Quantity",
        default=1,
        validators=[DataRequired(), NumberRange(min=1)],
    )
    unit_price = DecimalField(
        "Unit price",
        places=2,
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )
    currency = SelectField(
        "Currency",
        choices=CURRENCIES,
        default="KES",
        validators=[DataRequired()],
    )
    discount_amount = DecimalField(
        "Discount amount",
        places=2,
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )
    tax_amount = DecimalField(
        "Tax amount",
        places=2,
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )

    status = SelectField(
        "Status",
        choices=ADDON_STATUSES,
        default="selected",
        validators=[DataRequired()],
    )
    cancellation_reason = TextAreaField(
        "Cancellation reason",
        validators=[Optional(), Length(max=5000)],
    )
    internal_notes = TextAreaField(
        "Internal notes",
        validators=[Optional(), Length(max=10000)],
    )

    submit = SubmitField("Save add-on")

    def validate_discount_amount(self, field):
        if field.data is None:
            return

        unit_price = self.unit_price.data or 0
        quantity = self.quantity.data or 0
        gross = unit_price * quantity

        if field.data > gross:
            raise ValueError(
                "Discount cannot exceed the gross add-on amount."
            )

    def validate_tax_amount(self, field):
        if field.data is None:
            return

        unit_price = self.unit_price.data or 0
        quantity = self.quantity.data or 0
        discount = self.discount_amount.data or 0

        if field.data > (unit_price * quantity) - discount:
            raise ValueError(
                "Tax cannot exceed the amount remaining after discount."
            )


class BookingAddonStatusForm(FlaskForm):
    status = SelectField(
        "Add-on status",
        choices=ADDON_STATUSES,
        validators=[DataRequired()],
    )
    cancellation_reason = TextAreaField(
        "Cancellation reason",
        validators=[Optional(), Length(max=5000)],
    )
    internal_notes = TextAreaField(
        "Internal notes",
        validators=[Optional(), Length(max=10000)],
    )
    submit = SubmitField("Update status")