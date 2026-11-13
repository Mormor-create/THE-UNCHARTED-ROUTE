
"""
The Uncharted Route
Booking Document Forms
"""

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
    Length,
    Optional,
    NumberRange,
    ValidationError,)

DOCUMENT_TYPES = [
    ("passport", "Passport"),
    ("national_id", "National ID"),
    ("visa", "Visa"),
    ("insurance", "Travel Insurance"),
    ("waiver", "Waiver"),
    ("payment_receipt", "Payment Receipt"),
    ("booking_confirmation", "Booking Confirmation"),
    ("itinerary", "Itinerary"),
    ("medical", "Medical Document"),
    ("consent", "Consent Form"),
    ("other", "Other"),
]

DOCUMENT_STATUSES = [
    ("uploaded", "Uploaded"),
    ("under_review", "Under Review"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("archived", "Archived"),
]

VERIFICATION_STATUSES = [
    ("pending", "Pending Verification"),
    ("verified", "Verified"),
    ("rejected", "Rejected"),
]


class BookingDocumentForm(FlaskForm):
    booking_id = SelectField(
        "Booking",
        coerce=int,
        validators=[DataRequired()],
    )
    traveller_id = SelectField(
        "Traveller (optional)",
        coerce=int,
        validators=[Optional()],
    )
    title = StringField(
        "Document Title",
        validators=[DataRequired(), Length(max=255)],
    )
    document_type = SelectField(
        "Document Type",
        choices=DOCUMENT_TYPES,
        validators=[DataRequired()],
    )
    description = TextAreaField(
        "Description",
        validators=[Optional()],
    )
    original_filename = StringField(
        "Original Filename",
        validators=[DataRequired(), Length(max=255)],
    )
    storage_key = StringField(
        "Private Storage Key",
        validators=[DataRequired(), Length(max=500)],
        description="Internal storage identifier only; never a public URL.",
    )
    mime_type = StringField(
        "MIME Type",
        validators=[Optional(), Length(max=150)],
    )
    file_size_bytes = IntegerField(
        "File Size (bytes)",
        validators=[Optional(), NumberRange(min=0)],
    )
    checksum_sha256 = StringField(
        "SHA-256 Checksum",
        validators=[Optional(), Length(min=64, max=64)],
    )
    issuing_country = StringField(
        "Issuing Country",
        validators=[Optional(), Length(max=100)],
    )
    issued_at = DateField(
        "Issue Date",
        format="%Y-%m-%d",
        validators=[Optional()],
    )
    expires_at = DateField(
        "Expiry Date",
        format="%Y-%m-%d",
        validators=[Optional()],
    )
    status = SelectField(
        "Document Status",
        choices=DOCUMENT_STATUSES,
        validators=[DataRequired()],
    )
    verification_status = SelectField(
        "Verification Status",
        choices=VERIFICATION_STATUSES,
        validators=[DataRequired()],
    )
    verification_notes = TextAreaField(
        "Verification Notes",
        validators=[Optional()],
    )
    rejection_reason = TextAreaField(
        "Rejection Reason",
        validators=[Optional()],
    )
    submit = SubmitField("Save Document")

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators=extra_validators)
        if not valid:
            return False

        if (
            self.issued_at.data
            and self.expires_at.data
            and self.expires_at.data < self.issued_at.data
        ):
            self.expires_at.errors.append(
                "Expiry date cannot be earlier than issue date."
            )
            return False

        checksum = (self.checksum_sha256.data or "").strip()
        if checksum and any(
            character not in "0123456789abcdefABCDEF"
            for character in checksum
        ):
            self.checksum_sha256.errors.append(
                "Checksum must contain hexadecimal characters only."
            )
            return False

        if (
            self.verification_status.data == "rejected"
            and not (self.rejection_reason.data or "").strip()
        ):
            self.rejection_reason.errors.append(
                "Enter a reason when rejecting a document."
            )
            return False

        return True
