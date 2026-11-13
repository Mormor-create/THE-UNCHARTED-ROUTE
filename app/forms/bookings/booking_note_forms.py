
"""Forms for the Booking Notes CMS."""

from flask_wtf import FlaskForm
from wtforms import (
    SelectField, StringField, TextAreaField, HiddenField, SubmitField,
)
from wtforms.validators import DataRequired, Length, Optional, ValidationError

NOTE_TYPES = [
    ("internal_note", "Internal Note"),
    ("customer_message", "Customer Message"),
    ("phone_call", "Phone Call"),
    ("email", "Email"),
    ("whatsapp", "WhatsApp"),
    ("sms", "SMS"),
    ("payment", "Payment"),
    ("operations", "Operations"),
    ("complaint", "Complaint"),
    ("resolution", "Resolution"),
    ("reminder", "Reminder"),
    ("system_event", "System Event"),
]

VISIBILITIES = [
    ("internal", "Internal Only"),
    ("customer", "Customer Visible"),
]

CHANNELS = [
    ("", "Not specified"),
    ("phone", "Phone"),
    ("whatsapp", "WhatsApp"),
    ("email", "Email"),
    ("sms", "SMS"),
    ("in_person", "In Person"),
    ("internal", "Internal"),
    ("system", "System"),
]

DIRECTIONS = [
    ("", "Not specified"),
    ("inbound", "Inbound"),
    ("outbound", "Outbound"),
    ("internal", "Internal"),
]

DELIVERY_STATUSES = [
    ("", "Not applicable"),
    ("pending", "Pending"),
    ("queued", "Queued"),
    ("sent", "Sent"),
    ("delivered", "Delivered"),
    ("failed", "Failed"),
    ("not_applicable", "Not applicable"),
]


class BookingNoteForm(FlaskForm):
    booking_id = SelectField(
        "Booking",
        coerce=int,
        validators=[DataRequired(message="Select a booking.")],
    )
    title = StringField("Title", validators=[Optional(), Length(max=255)])
    content = TextAreaField(
        "Note / Communication",
        validators=[DataRequired(), Length(max=100000)],
    )
    note_type = SelectField(
        "Note Type", choices=NOTE_TYPES, validators=[DataRequired()]
    )
    visibility = SelectField(
        "Visibility", choices=VISIBILITIES, validators=[DataRequired()]
    )
    communication_channel = SelectField(
        "Communication Channel", choices=CHANNELS, validators=[Optional()]
    )
    direction = SelectField(
        "Direction", choices=DIRECTIONS, validators=[Optional()]
    )
    recipient = StringField("Recipient", validators=[Optional(), Length(max=255)])
    subject = StringField("Subject", validators=[Optional(), Length(max=255)])
    external_reference = StringField(
        "External Reference", validators=[Optional(), Length(max=255)]
    )
    delivery_status = SelectField(
        "Delivery Status", choices=DELIVERY_STATUSES, validators=[Optional()]
    )
    delivery_error = TextAreaField("Delivery Error", validators=[Optional()])
    author_name_snapshot = StringField(
        "Author Name Snapshot", validators=[Optional(), Length(max=200)]
    )
    author_role_snapshot = StringField(
        "Author Role Snapshot", validators=[Optional(), Length(max=100)]
    )
    submit = SubmitField("Save Note")

    def validate_visibility(self, field):
        if field.data == "internal" and self.delivery_status.data in {
            "sent", "delivered"
        }:
            raise ValidationError(
                "A note marked sent or delivered cannot be internal-only."
            )