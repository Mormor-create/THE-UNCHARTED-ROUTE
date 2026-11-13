
"""Forms for inviting guides and accepting guide invitations."""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    SelectField,
    PasswordField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
)

class GuideInvitationForm(FlaskForm):
    first_name = StringField(
        "First name",
        validators=[DataRequired(), Length(max=100)],
    )
    last_name = StringField(
        "Last name",
        validators=[DataRequired(), Length(max=100)],
    )
    email = EmailField(
        "Email address",
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    phone = StringField(
        "Phone number",
        validators=[Optional(), Length(max=30)],
    )
    employee_number = StringField(
        "Employee number",
        validators=[Optional(), Length(max=50)],
    )
    department = StringField(
        "Department",
        default="Guiding",
        validators=[Optional(), Length(max=100)],
    )
    job_title = StringField(
        "Job title",
        default="Guide",
        validators=[Optional(), Length(max=150)],
    )
    employment_type = SelectField(
        "Employment type",
        choices=[
            ("Freelance", "Freelance"),
            ("Full Time", "Full Time"),
            ("Part Time", "Part Time"),
            ("Contract", "Contract"),
            ("Seasonal", "Seasonal"),
            ("Other", "Other"),
        ],
        default="Freelance",
        validators=[DataRequired()],
    )
    submit = SubmitField("Create guide and send invitation")

class AcceptGuideInvitationForm(FlaskForm):
    password = PasswordField(
        "Create password",
        validators=[
            DataRequired(),
            Length(min=12, max=128),
        ],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="The passwords must match."),
        ],
    )
    submit = SubmitField("Activate my guide account")
