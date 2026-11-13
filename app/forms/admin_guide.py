"""
===============================================================================
The Uncharted Route
Admin Guide Forms
===============================================================================

Forms used by the Guide Dashboard administration module.

Responsibilities
----------------
• Filter and search guides
• Create guide operational profiles
• Edit guide profiles
• Change guide status
• Create and edit guide schedules
• Create and edit guide availability
• Filter guide assignments
• Update guide assignment status
• Filter guide booking
• Add guide operational notes

Architecture
------------

    Admin Guide Route
            ↓
      Admin Guide Forms
            ↓
       Guide Service
            ↓
       Staff Service
            ↓
          Models
            ↓
        Database

Important
---------

These forms handle input validation only.

Business operations such as:

• creating guide profiles
• changing guide status
• assigning guides
• updating assignments
• creating schedules
• managing availability

belong to the Guide Service / Staff Service layer.
"""
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DateTimeField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    ValidationError,)
from app.models.staff import (
    STAFF_TYPES,
    STAFF_STATUSES,
    EMPLOYMENT_TYPES,)
from app.models.staff_availability import (
    STAFF_AVAILABILITY_STATUSES,)
from app.models.staff_schedule import (
    STAFF_SCHEDULE_STATUSES,)
from app.models.staff_assignment import (
    STAFF_ASSIGNMENT_ROLES,
    STAFF_ASSIGNMENT_STATUSES,)

# =============================================================================
# Helpers
# =============================================================================
def _choice_values(values):
    """
    Convert a collection of allowed values into WTForms choices.
    """
    return [
        (value, value)
        for value in values]

def _status_choices():
    """
    Return Staff status choices.
    """
    return _choice_values(
        STAFF_STATUSES)

def _staff_type_choices():
    """
    Return Staff type choices.
    """
    return _choice_values(
        STAFF_TYPES)

def _employment_type_choices():
    """
    Return employment type choices.
    """
    return _choice_values(EMPLOYMENT_TYPES)

def _availability_status_choices():
    """
    Return Staff availability status choices.
    """
    return _choice_values(
        STAFF_AVAILABILITY_STATUSES
    )

def _schedule_status_choices():
    """
    Return Staff schedule status choices.
    """
    return _choice_values(
        STAFF_SCHEDULE_STATUSES
    )


def _assignment_role_choices():
    """
    Return Staff assignment role choices.
    """

    return _choice_values(
        STAFF_ASSIGNMENT_ROLES
    )

def _assignment_status_choices():
    """
    Return Staff assignment status choices.
    """

    return _choice_values(
        STAFF_ASSIGNMENT_STATUSES
    )

# =============================================================================
# Guide Catalogue / Filter Form
# =============================================================================
class GuideFilterForm(FlaskForm):
    """Filter and search Guide records."""

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": (
                "Name, employee number, "
                "email, job title..."
            )
        },
    )

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    status = SelectField(
        "Status",
        choices=[
            ("", "All statuses"),
            *_status_choices(),
        ],
        validators=[Optional()],
    )

    active_only = BooleanField(
        "Active guides only"
    )

    submit = SubmitField(
        "Apply Filters"
    )

    reset = SubmitField(
        "Reset"
    )

# =============================================================================
# Guide Creation Form
# =============================================================================
class GuideCreateForm(FlaskForm):
    """
    Create a Guide operational profile.

    The selected User account must already exist and must have
    the Guide role. The route/service layer is responsible for
    supplying and validating the User.
    """
    user_id = IntegerField(
        "User ID",
        validators=[
            DataRequired(),
            NumberRange(
                min=1),],)

    employee_number = StringField(
        "Employee Number",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    staff_type = SelectField(
        "Staff Type",
        choices=_staff_type_choices(),
        default="Guide",
        validators=[
            DataRequired()
        ],
    )

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    job_title = StringField(
        "Job Title",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    employment_type = SelectField(
        "Employment Type",
        choices=_employment_type_choices(),
        default="Full Time",
        validators=[
            DataRequired()],)

    hire_date = DateField(
        "Hire Date",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",)

    end_date = DateField(
        "End Date",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    status = SelectField(
        "Status",
        choices=_status_choices(),
        default="Active",
        validators=[
            DataRequired()
        ],
    )

    skills = TextAreaField(
        "Skills",
        validators=[
            Optional()
        ],
        render_kw={
            "placeholder": (
                "Wildlife guiding, hiking, "
                "photography, first aid..."
            )
        },
    )

    languages = TextAreaField(
        "Languages",
        validators=[
            Optional()
        ],
        render_kw={
            "placeholder": (
                "English, Kiswahili, French..."
            )
        },
    )

    certifications = TextAreaField(
        "Certifications",
        validators=[
            Optional()
        ],
    )

    qualifications = TextAreaField(
        "Qualifications",
        validators=[
            Optional()
        ],
    )

    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[
            Optional(),
            Length(
                max=200
            ),
        ],
    )

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[
            Optional(),
            Length(
                max=50
            ),
        ],
    )

    emergency_contact_relationship = StringField(
        "Emergency Contact Relationship",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Optional()
        ],
    )

    internal_notes = TextAreaField(
        "Internal Notes",
        validators=[
            Optional()
        ],
    )

    submit = SubmitField(
        "Create Guide"
    )


# =============================================================================
# Guide Edit Form
# =============================================================================


class GuideEditForm(FlaskForm):
    """
    Edit an existing Guide operational profile.
    """

    employee_number = StringField(
        "Employee Number",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    staff_type = SelectField(
        "Staff Type",
        choices=_staff_type_choices(),
        validators=[
            DataRequired()
        ],
    )

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    job_title = StringField(
        "Job Title",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    employment_type = SelectField(
        "Employment Type",
        choices=_employment_type_choices(),
        validators=[
            DataRequired()
        ],
    )

    hire_date = DateField(
        "Hire Date",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    end_date = DateField(
        "End Date",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    status = SelectField(
        "Status",
        choices=_status_choices(),
        validators=[
            DataRequired()
        ],
    )

    skills = TextAreaField(
        "Skills",
        validators=[
            Optional()
        ],
    )

    languages = TextAreaField(
        "Languages",
        validators=[
            Optional()
        ],
    )

    certifications = TextAreaField(
        "Certifications",
        validators=[
            Optional()
        ],
    )

    qualifications = TextAreaField(
        "Qualifications",
        validators=[
            Optional()
        ],
    )

    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[
            Optional(),
            Length(
                max=200
            ),
        ],
    )

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[
            Optional(),
            Length(
                max=50
            ),
        ],
    )

    emergency_contact_relationship = StringField(
        "Emergency Contact Relationship",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Optional()
        ],
    )

    internal_notes = TextAreaField(
        "Internal Notes",
        validators=[
            Optional()
        ],
    )

    submit = SubmitField(
        "Save Changes"
    )


# =============================================================================
# Guide Status Form
# =============================================================================


class GuideStatusForm(FlaskForm):
    """
    Change a Guide's operational status.
    """

    status = SelectField(
        "Guide Status",
        choices=_status_choices(),
        validators=[
            DataRequired()
        ],
    )

    submit = SubmitField(
        "Update Status"
    )


# =============================================================================
# Guide Schedule Filter Form
# =============================================================================


class GuideScheduleFilterForm(FlaskForm):
    """
    Filter Guide schedules by date range and status.
    """

    start_date = DateField(
        "From",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    end_date = DateField(
        "To",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    status = SelectField(
        "Status",
        choices=[
            ("", "All statuses"),
            *_schedule_status_choices(),
        ],
        validators=[
            Optional()
        ],
    )

    submit = SubmitField(
        "Filter Schedule"
    )


# =============================================================================
# Guide Schedule Form
# =============================================================================


class GuideScheduleForm(FlaskForm):
    """
    Create or edit a Guide schedule.
    """

    title = StringField(
        "Schedule Title",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=200,
            ),
        ],
        render_kw={
            "placeholder": (
                "e.g. Nairobi National Park Tour"
            )
        },
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional()
        ],
    )

    start_datetime = DateTimeField(
        "Start",
        validators=[
            DataRequired()
        ],
        format="%Y-%m-%d %H:%M",
    )

    end_datetime = DateTimeField(
        "End",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d %H:%M",
    )

    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(
                max=255
            ),
        ],
    )

    status = SelectField(
        "Status",
        choices=_schedule_status_choices(),
        default="Scheduled",
        validators=[
            DataRequired()
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Optional()
        ],
    )

    submit = SubmitField("Save Schedule")

    def validate_end_datetime(self, field):
        """
        Ensure the schedule end is after its start.
        """

        if (
            field.data
            and self.start_datetime.data
            and field.data <= self.start_datetime.data
        ):
            raise ValidationError(
                "End time must be after start time."
            )

# =============================================================================
# Guide Availability Form
# =============================================================================
class GuideAvailabilityForm(FlaskForm):
    """
    Create or edit Guide availability.
    """

    date = DateField(
        "Date",
        validators=[
            DataRequired()
        ],
        format="%Y-%m-%d",
    )

    status = SelectField(
        "Availability Status",
        choices=_availability_status_choices(),
        default="Available",
        validators=[
            DataRequired()
        ],
    )

    start_time = TimeField(
        "Start Time",
        validators=[
            Optional()
        ],
        format="%H:%M",
    )

    end_time = TimeField(
        "End Time",
        validators=[
            Optional()
        ],
        format="%H:%M",
    )

    reason = TextAreaField(
        "Reason / Notes",
        validators=[
            Optional()
        ],
    )

    submit = SubmitField(
        "Save Availability"
    )

    def validate_end_time(self, field):
        """
        Ensure the availability end time is after the start time.
        """

        if (
            field.data
            and self.start_time.data
            and field.data <= self.start_time.data
        ):
            raise ValidationError(
                "End time must be after start time."
            )

# =============================================================================
# Guide Availability Filter Form
# =============================================================================
class GuideAvailabilityFilterForm(FlaskForm):
    """
    Filter Guide availability records.
    """
    start_date = DateField(
        "From",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    end_date = DateField(
        "To",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    status = SelectField(
        "Status",
        choices=[
            ("", "All statuses"),
            *_availability_status_choices(),
        ],
        validators=[
            Optional()
        ],
    )

    submit = SubmitField(
        "Filter"
    )

# =============================================================================
# Guide Assignment Filter Form
# =============================================================================
class GuideAssignmentFilterForm(FlaskForm):
    """
    Filter Guide assignments.
    """
    status = SelectField(
        "Assignment Status",
        choices=[
            ("", "All statuses"),
            *_assignment_status_choices(),
        ],
        validators=[
            Optional()],)

    role = SelectField(
        "Assignment Role",
        choices=[
            ("", "All roles"),
            *_assignment_role_choices(),
        ],
        validators=[
            Optional()],)
    submit = SubmitField("Apply Filters")

# =============================================================================
# Guide Assignment Action Form
# =============================================================================
class GuideAssignmentActionForm(FlaskForm):
    """
    Update the status of a Guide assignment.
    """
    status = SelectField(
        "Assignment Status",
        choices=_assignment_status_choices(),
        validators=[
            DataRequired()],)

    notes = TextAreaField(
        "Assignment Notes",
        validators=[
            Optional()],)
    submit = SubmitField("Update Assignment")

# =============================================================================
# Guide Assignment Creation Form
# =============================================================================
class GuideAssignmentForm(FlaskForm):
    """
    Assign a Guide to a booking.
    The route should populate the guide and booking selections
    dynamically from the database.
    """
    guide_id = IntegerField(
        "Guide",
        validators=[
            DataRequired(),
            NumberRange(
                min=1),],)

    booking_id = IntegerField(
        "Booking",
        validators=[
            DataRequired(),
            NumberRange(
                min=1),],)

    role = SelectField(
        "Assignment Role",
        choices=_assignment_role_choices(),
        default="Other",
        validators=[
            DataRequired()],)

    is_primary = BooleanField("Primary Guide")
    check_availability = BooleanField(
        "Check Guide Availability",
        default=True,)

    notes = TextAreaField(
        "Assignment Notes",
        validators=[
            Optional()],)
    submit = SubmitField("Assign Guide")

# =============================================================================
# Guide Booking Filter Form
# =============================================================================
class GuideBookingFilterForm(FlaskForm):
    """
    Filter booking assigned to Guides.
    """
    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(
                max=255
            ),
        ],
        render_kw={
            "placeholder": (
                "Booking reference, guest, email...")},)

    status = SelectField(
        "Booking Status",
        choices=[
            ("", "All statuses"),
            (
                "Inquiry",
                "Inquiry",
            ),
            (
                "Pending",
                "Pending",
            ),
            (
                "Awaiting Payment",
                "Awaiting Payment",
            ),
            (
                "Partially Paid",
                "Partially Paid",
            ),
            (
                "Confirmed",
                "Confirmed",
            ),
            (
                "In Progress",
                "In Progress",
            ),
            (
                "Completed",
                "Completed",
            ),
            (
                "Reviewed",
                "Reviewed",
            ),
            (
                "Cancelled",
                "Cancelled",
            ),
            (
                "Refunded",
                "Refunded",
            ),
            (
                "Archived",
                "Archived",
            ),
        ],
        validators=[
            Optional()
        ],
    )

    start_date = DateField(
        "Experience From",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    end_date = DateField(
        "Experience To",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    submit = SubmitField(
        "Apply Filters"
    )

# =============================================================================
# Guide Booking Action Form
# =============================================================================
class GuideBookingActionForm(FlaskForm):
    """
    Perform an administrative action associated with a Guide booking.
    Actual booking business logic remains in Booking Service.
    """
    action = SelectField(
        "Action",
        choices=[
            (
                "view",
                "View Booking",),
            (
                "start",
                "Start Experience",),
            (
                "complete",
                "Mark Experience Completed",
            ),
        ],
        validators=[
            DataRequired()
        ],
    )

    notes = TextAreaField(
        "Operational Notes",
        validators=[
            Optional()
        ],
    )

    submit = SubmitField(
        "Continue"
    )

# =============================================================================
# Guide Notes Form
# =============================================================================
class GuideNotesForm(FlaskForm):
    """
    Add operational notes to a Guide-related record.
    """

    notes = TextAreaField(
        "Notes",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=5000,
            ),
        ],
        render_kw={
            "placeholder": (
                "Enter operational notes..."
            )
        },
    )

    submit = SubmitField("Save Notes")
# =============================================================================
# Guide Performance Filter Form
# =============================================================================
class GuidePerformanceFilterForm(FlaskForm):
    """
    Filter Guide performance reporting.
    """
    start_date = DateField(
        "From",
        validators=[
            Optional()
        ],format="%Y-%m-%d",)

    end_date = DateField(
        "To",
        validators=[
            Optional()
        ],
        format="%Y-%m-%d",
    )

    guide_id = IntegerField(
        "Guide ID",
        validators=[
            Optional(),
            NumberRange(
                min=1),],)
    submit = SubmitField("Generate Report")
# =============================================================================
# Quick Guide Actions
# =============================================================================
class GuideQuickActionForm(FlaskForm):
    """
    Small form used by dashboard cards/actions.
    The actual operation is selected by the route and
    delegated to Guide Service.
    """
    action = SelectField(
        "Action",
        choices=[
            ("activate","Activate Guide",),
            ("deactivate","Deactivate Guide",),
            ("leave","Place on Leave",),],
        validators=[
            DataRequired()],)
    submit = SubmitField("Apply")
# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # Catalogue
    "GuideFilterForm",

    # Guide
    "GuideCreateForm",
    "GuideEditForm",
    "GuideStatusForm",
    "GuideQuickActionForm",

    # Schedule
    "GuideScheduleFilterForm",
    "GuideScheduleForm",

    # Availability
    "GuideAvailabilityForm",
    "GuideAvailabilityFilterForm",

    # Assignments
    "GuideAssignmentFilterForm",
    "GuideAssignmentActionForm",
    "GuideAssignmentForm",

    # Bookings
    "GuideBookingFilterForm",
    "GuideBookingActionForm",

    # Performance
    "GuidePerformanceFilterForm",

    # Notes
    "GuideNotesForm",
]