"""
===============================================================================
The Uncharted Route
Public Experience Inquiry Form
===============================================================================
"""
from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    IntegerField,
    DateField,
    SelectField,
    TextAreaField,
    SubmitField,)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional, InputRequired, )

class ExperienceInquiryForm(FlaskForm):
    """Public form for enquiring about an experience."""
    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=2, max=150),],)

    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=254),],)

    phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Length(min=7, max=40),],)

    country = StringField(
        "Country of Residence",
        validators=[
            Optional(),
            Length(max=100),],)

    preferred_date = DateField(
        "Preferred Experience Date",
        format="%Y-%m-%d",
        validators=[Optional()],
        render_kw={"min": date.today().isoformat()},)

    adults = IntegerField(
        "Adults",
        default=1,
        validators=[
            InputRequired(),
            NumberRange(min=1, max=100),],)

    children = IntegerField(
        "Children",
        default=0,
        validators=[
            InputRequired(),
            NumberRange(min=0, max=100),],)

    infants = IntegerField(
        "Infants",
        default=0,
        validators=[
            InputRequired(),
            NumberRange(min=0, max=100),],)

    preferred_currency = SelectField(
        "Preferred Currency",
        choices=[
            ("KES", "Kenyan Shilling (KES)"),
            ("USD", "US Dollar (USD)"),
            ("EUR", "Euro (EUR)"),
            ("GBP", "British Pound (GBP)"),],
        default="KES",
        validators=[DataRequired()],)

    special_requests = TextAreaField(
        "Special Requests or Questions",
        validators=[
            Optional(),
            Length(max=5000),],
        render_kw={
            "rows": 5,
            "placeholder": (
                "Tell us about your interests, special requirements, " "or anything else we should know."),},)

    submit = SubmitField("Send Experience Enquiry")