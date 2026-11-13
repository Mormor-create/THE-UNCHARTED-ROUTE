"""
Booking payment administration forms.
"""
from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    TextAreaField,
    DecimalField,
    SubmitField,)
from wtforms.validators import (
    DataRequired,
    Optional,
    NumberRange,
    Length,)

CURRENCY_CHOICES = [
    (value, value)
    for value in [
        "KES", "USD", "EUR", "GBP", "UGX",
        "TZS", "ZAR", "NGN", "GHS",]]

PAYMENT_METHOD_CHOICES = [
    ("mpesa", "M-Pesa"),
    ("card", "Card"),
    ("bank_transfer", "Bank transfer"),
    ("cash", "Cash"),
    ("paypal", "PayPal"),
    ("other", "Other"),]

PAYMENT_PURPOSE_CHOICES = [
    ("deposit", "Deposit"),
    ("balance", "Balance"),
    ("full_payment", "Full payment"),
    ("addon", "Add-on"),
    ("other", "Other"),]

class BookingPaymentForm(FlaskForm):
    booking_id = SelectField(
        "Booking",
        coerce=int,
        validators=[DataRequired()],
    )
    transaction_type = SelectField(
        "Transaction type",
        choices=[
            ("payment", "Payment"),
            ("adjustment", "Adjustment"),
        ],
        validators=[DataRequired()],
    )
    payment_purpose = SelectField(
        "Payment purpose",
        choices=PAYMENT_PURPOSE_CHOICES,
        validators=[DataRequired()],
    )
    amount = DecimalField(
        "Amount",
        places=2,
        validators=[DataRequired(), NumberRange(min=0.01)],
    )
    currency = SelectField(
        "Currency",
        choices=CURRENCY_CHOICES,
        validators=[DataRequired()],
    )
    payment_method = SelectField(
        "Payment method",
        choices=PAYMENT_METHOD_CHOICES,
        validators=[DataRequired()],
    )
    payment_provider = StringField(
        "Payment provider",
        validators=[Optional(), Length(max=60)],
    )
    transaction_reference = StringField(
        "Transaction reference",
        validators=[Optional(), Length(max=100)],
    )
    provider_reference = StringField(
        "Provider reference",
        validators=[Optional(), Length(max=255)],
    )
    description = StringField(
        "Description",
        validators=[Optional(), Length(max=255)],
    )
    internal_notes = TextAreaField(
        "Internal notes",
        validators=[Optional()],
    )
    submit = SubmitField("Record transaction")


class BookingPaymentFilterForm(FlaskForm):
    booking_id = SelectField(
        "Booking",
        coerce=int,
        validators=[Optional()],
    )
    transaction_type = SelectField(
        "Transaction type",
        choices=[
            ("", "All transaction types"),
            ("payment", "Payment"),
            ("refund", "Refund"),
            ("adjustment", "Adjustment"),
        ],
        validators=[Optional()],
    )
    status = SelectField(
        "Status",
        choices=[
            ("", "All statuses"),
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("succeeded", "Succeeded"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField("Filter")


class BookingRefundForm(FlaskForm):
    amount = DecimalField(
        "Refund amount",
        places=2,
        validators=[Optional(), NumberRange(min=0.01)],
    )
    payment_method = SelectField(
        "Refund method",
        choices=PAYMENT_METHOD_CHOICES,
        validators=[Optional()],
    )
    payment_provider = StringField(
        "Payment provider",
        validators=[Optional(), Length(max=60)],
    )
    provider_reference = StringField(
        "Refund provider reference",
        validators=[Optional(), Length(max=255)],
    )
    description = StringField(
        "Refund description",
        validators=[Optional(), Length(max=255)],
    )
    internal_notes = TextAreaField(
        "Internal notes",
        validators=[Optional()],
    )
    submit = SubmitField("Create refund")