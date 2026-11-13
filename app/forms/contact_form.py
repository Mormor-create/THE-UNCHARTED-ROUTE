"""
===============================================================================
The Uncharted Route
Contact Form
===============================================================================
Public website form for submitting contact enquiries.
The form collects customer information and enquiry details. Persistence is
handled by ContactService rather than directly by the form.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    TextAreaField,
    BooleanField,
    SubmitField,)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,)

# =============================================================================
# Contact Form
# =============================================================================
class ContactForm(FlaskForm):
    """
    Public contact enquiry form.
    """

    # =========================================================================
    # Contact Information
    # =========================================================================
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(
                message="Please enter your first name."
            ),
            Length(
                max=100,
                message="First name cannot exceed 100 characters."),],)

    last_name = StringField(
        "Last Name",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Last name cannot exceed 100 characters."),],)

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(
                message="Please enter your email address."
            ),
            Email(
                message="Please enter a valid email address."
            ),
            Length(
                max=255,
                message="Email address cannot exceed 255 characters."),],)

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(
                max=50,
                message="Phone number cannot exceed 50 characters."
            ),
        ],
    )

    company = StringField(
        "Company",
        validators=[
            Optional(),
            Length(
                max=150,
                message="Company name cannot exceed 150 characters."),],)

    country = StringField(
        "Country",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Country cannot exceed 100 characters."),],)

    # =========================================================================
    # Enquiry Details
    # =========================================================================
    enquiry_type = SelectField(
        "Enquiry Type",
        choices=[
            ("General", "General Question"),
            ("Booking", "Booking Support"),
            ("Corporate", "Corporate Travel"),
            ("Partnership", "Partnership Request"),
            ("Media", "Media Enquiry"),
            ("Supplier", "Supplier Inquiry"),
            ("Complaint", "Complaint"),
            ("Compliment", "Compliment"),
            ("Support", "General Support"),
            ("Custom Experience", "Custom Experience Request"),
        ],
        default="General",
        validators=[
            DataRequired(message="Please select an enquiry type."),],)

    subject = StringField(
        "Subject",
        validators=[
            DataRequired(message="Please enter a subject."),
            Length(
                max=255,
                message="Subject cannot exceed 255 characters."),],)

    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(message="Please enter your message."),
            Length(
                min=10,
                max=10000,
                message="Your message must be between 10 and 10,000 characters."),],)

    # =========================================================================
    # Marketing
    # =========================================================================
    newsletter_opt_in = BooleanField(
        "Yes, I agree to receive marketing emails about promotions and offers, "
        "new experiences, blog updates, and company news. I can unsubscribe "
        "at any time."
    )

    # =========================================================================
    # Submit
    # =========================================================================
    submit = SubmitField("Send Message")