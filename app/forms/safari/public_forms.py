"""Public-facing safari inquiry form."""
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    ValidationError,)

class SafariInquiryForm(FlaskForm):
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=2, max=180)],)
    email = StringField(
        "Email address",
        validators=[DataRequired(), Email(), Length(max=254)],)
    phone = StringField(
        "Phone number",
        validators=[Optional(), Length(max=40)],)

    preferred_start_date = DateField(
        "Preferred arrival date",
        format="%Y-%m-%d",
        validators=[Optional()],)
    preferred_end_date = DateField(
        "Preferred departure date",
        format="%Y-%m-%d",
        validators=[Optional()],)

    adults = IntegerField(
        "Adults",
        default=2,
        validators=[InputRequired(),NumberRange(min=1, max=100),],)

    children = IntegerField(
        "Children",
        default=0,
        validators=[InputRequired(),NumberRange(min=0, max=100),],)

    infants = IntegerField(
        "Infants",
        default=0,
        validators=[InputRequired(),NumberRange(min=0, max=100),],)

    children_ages = StringField(
        "Children's ages",
        description="If applicable, separate ages with commas.",
        validators=[Optional(), Length(max=200)],)

    preferred_currency = SelectField(
        "Preferred currency",
        choices=[
            ("KES", "KES — Kenyan Shilling"),
            ("USD", "USD — US Dollar"),
            ("EUR", "EUR — Euro"),
            ("GBP", "GBP — British Pound"),
            ("UGX", "UGX — Ugandan Shilling"),
            ("TZS", "TZS — Tanzanian Shilling"),
            ("ZAR", "ZAR — South African Rand"),
            ("NGN", "NGN — Nigerian Naira"),
            ("GHS", "GHS — Ghanaian Cedi"),
        ],
        default="KES",
        validators=[DataRequired()],)

    special_requests = TextAreaField(
        "Special requests",
        validators=[Optional(), Length(max=5000)],)

    submit = SubmitField("Send safari inquiry")

    def validate_preferred_end_date(self, field):
        start = self.preferred_start_date.data
        end = field.data

        if start is not None and end is not None and end < start:
            raise ValidationError(
                "Departure date must be on or after arrival date.")