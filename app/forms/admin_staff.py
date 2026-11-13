"""
===============================================================================
The Uncharted Route
Administrative Staff Forms
===============================================================================
WTForms used by the administrative Staff Management module.
Responsibilities
----------------
• Staff filtering
• Staff account creation
• Staff profile creation
• Staff account editing
• Staff type validation
• Employment validation
• Account status validation

Business logic such as password hashing, uniqueness checks, account creation,
and staff updates belongs to the appropriate services.
===============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,)
from app.models.staff import (
    STAFF_TYPES,
    STAFF_STATUSES,
    EMPLOYMENT_TYPES,)

# =============================================================================
# Shared Choices
# =============================================================================
STAFF_TYPE_CHOICES = [
    (
        staff_type,
        staff_type,
    )
    for staff_type in STAFF_TYPES
]

EMPLOYMENT_TYPE_CHOICES = [
    (
        employment_type,
        employment_type,)
    for employment_type in EMPLOYMENT_TYPES]

STAFF_STATUS_CHOICES = [
    (
        status,
        status,)for status in STAFF_STATUSES]

STATUS_FILTER_CHOICES = [
    ("", "All Statuses"),
    ("Active", "Active"),
    ("Inactive", "Inactive"),
]

# =============================================================================
# Staff Filter Form
# =============================================================================
class AdminStaffFilterForm(FlaskForm):
    """
    Filter form for the Staff Management catalogue.
    """
    class Meta:
        csrf = False

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=150),],
        render_kw={
            "placeholder": "Search name, username, email or employee number..."},)

    staff_type = SelectField(
        "Staff Type",
        choices=[
            ("", "All Staff Types"),
        ] + STAFF_TYPE_CHOICES,
        validators=[Optional(),],)

    status = SelectField(
        "Status",
        choices=STATUS_FILTER_CHOICES,
        validators=[Optional(),],)

    submit = SubmitField("Filter")

# =============================================================================
# Staff Create Form
# =============================================================================
class AdminStaffCreateForm(FlaskForm):
    """
    Create a new internal User account and Staff profile.
    """
    # =========================================================================
    # Personal Information
    # =========================================================================
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=100,),],)

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(
                min=2,max=100,),],)

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=30,),],)

    # =========================================================================
    # Account Information
    # =========================================================================
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=3,
                max=80,),],)

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255,),],)

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8,max=128,),],)

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password",
                message="Passwords must match.",),],)

    is_verified = BooleanField(
        "Verified Account",
        default=True,)

    # =========================================================================
    # Staff Profile
    # =========================================================================
    employee_number = StringField(
        "Employee Number",
        validators=[
            Optional(),
            Length(max=50,),],)

    staff_type = SelectField(
        "Staff Type",
        choices=STAFF_TYPE_CHOICES,
        validators=[DataRequired(),],)

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(max=150,),],)

    job_title = StringField(
        "Job Title",
        validators=[
            Optional(),
            Length(
                max=150,),],)

    employment_type = SelectField(
        "Employment Type",
        choices=EMPLOYMENT_TYPE_CHOICES,
        validators=[DataRequired(),],)

    hire_date = DateField(
        "Hire Date",
        validators=[Optional(),],)

    status = SelectField(
        "Staff Status",
        choices=STAFF_STATUS_CHOICES,
        validators=[DataRequired(),
        ],default="Active",)

    # =========================================================================
    # Professional Profile
    # =========================================================================
    skills = TextAreaField(
        "Skills",
        validators=[Optional(),],
        render_kw={
            "rows": 3,
            "placeholder": "Key skills, capabilities or areas of expertise",},)

    languages = TextAreaField(
        "Languages",
        validators=[
            Optional(),
        ],
        render_kw={
            "rows": 2,
            "placeholder": "Languages spoken",},)

    certifications = TextAreaField(
        "Certifications",
        validators=[Optional(),],
        render_kw={
            "rows": 3,
            "placeholder": "Professional certifications",},)

    qualifications = TextAreaField(
        "Qualifications",
        validators=[Optional(),],
        render_kw={
            "rows": 3,
            "placeholder": "Academic or professional qualifications",},)

    # =========================================================================
    # Emergency Contact
    # =========================================================================
    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[
            Optional(),
            Length(max=150,),],)

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[
            Optional(),
            Length(max=30,),],)

    emergency_contact_relationship = StringField(
        "Relationship",
        validators=[
            Optional(),
            Length(max=80,),],)

    # =========================================================================
    # Notes
    # =========================================================================
    notes = TextAreaField(
        "Notes",
        validators=[
            Optional(),],
        render_kw={
            "rows": 4,
            "placeholder": "General staff notes",},)

    internal_notes = TextAreaField(
        "Internal Notes",
        validators=[Optional(),],
        render_kw={
            "rows": 4,
            "placeholder": "Private operational notes",},)

    # =========================================================================
    # Submit
    # =========================================================================
    submit = SubmitField("Create Staff Member")

# =============================================================================
# Staff Edit Form
# =============================================================================
class AdminStaffEditForm(FlaskForm):
    """
    Edit an existing Staff account and profile.
    Password is optional. A blank password leaves the existing password
    unchanged.
    """
    # =========================================================================
    # Personal Information
    # =========================================================================
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=100,),],)

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=100,),],)

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=30,),],)

    # =========================================================================
    # Account Information
    # =========================================================================
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=3,
                max=80,),],)

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255,),],)

    password = PasswordField(
        "New Password",
        validators=[
            Optional(),
            Length(
                min=8,
                max=128,),],)

    is_active = BooleanField(
        "Active Account",
        default=True,)

    is_verified = BooleanField(
        "Verified Account",default=True,)

    # =========================================================================
    # Staff Profile
    # =========================================================================
    employee_number = StringField(
        "Employee Number",
        validators=[
            Optional(),
            Length(max=50,),],)

    staff_type = SelectField(
        "Staff Type",
        choices=STAFF_TYPE_CHOICES,
        validators=[DataRequired(),],)

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(max=150,),],)

    job_title = StringField(
        "Job Title",
        validators=[
            Optional(),
            Length(max=150,),],)

    employment_type = SelectField(
        "Employment Type",
        choices=EMPLOYMENT_TYPE_CHOICES,
        validators=[DataRequired(),],)

    hire_date = DateField(
        "Hire Date",
        validators=[Optional(),],)

    end_date = DateField(
        "End Date",
        validators=[Optional()],)

    status = SelectField(
        "Staff Status",
        choices=STAFF_STATUS_CHOICES,
        validators=[DataRequired(),],)

    # =========================================================================
    # Professional Profile
    # =========================================================================
    skills = TextAreaField(
        "Skills",
        validators=[Optional(),],)

    languages = TextAreaField(
        "Languages",
        validators=[Optional(),],)

    certifications = TextAreaField(
        "Certifications",
        validators=[Optional(),],)

    qualifications = TextAreaField(
        "Qualifications",
        validators=[Optional(),],)

    # =========================================================================
    # Emergency Contact
    # =========================================================================
    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[
            Optional(),
            Length(max=150,),],)

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[
            Optional(),
            Length(max=30,),],)

    emergency_contact_relationship = StringField(
        "Relationship",
        validators=[
            Optional(),
            Length(max=80,),],)

    # =========================================================================
    # Notes
    # =========================================================================
    notes = TextAreaField(
        "Notes",
        validators=[Optional(),],)

    internal_notes = TextAreaField(
        "Internal Notes",
        validators=[Optional(),],)

    # =========================================================================
    # Submit
    # =========================================================================
    submit = SubmitField("Save Changes")

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "AdminStaffFilterForm",
    "AdminStaffCreateForm",
    "AdminStaffEditForm",]