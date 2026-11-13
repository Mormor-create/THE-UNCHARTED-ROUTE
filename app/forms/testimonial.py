"""
===============================================================================
THE UNCHARTED ROUTE
Testimonial Forms
===============================================================================
Forms for testimonial administration, filtering and public submissions.
===============================================================================
"""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    HiddenField,)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    URL,
    ValidationError, Email, )

# =============================================================================
# Choices
# =============================================================================
TESTIMONIAL_SOURCE_CHOICES = [
    ("", "Select source"),
    ("Website", "Website"),
    ("Google", "Google"),
    ("TripAdvisor", "TripAdvisor"),
    ("Facebook", "Facebook"),
    ("LinkedIn", "LinkedIn"),
    ("Email", "Email"),]

TESTIMONIAL_SORT_CHOICES = [
    ("sort_order", "Custom order"),
    ("newest", "Newest first"),
    ("oldest", "Oldest first"),
    ("name_asc", "Customer A–Z"),
    ("name_desc", "Customer Z–A"),
    ("rating_desc", "Highest rated"),
    ("rating_asc", "Lowest rated"),]

TESTIMONIAL_RATING_CHOICES = [
    (5, "★★★★★ — 5 stars"),
    (4, "★★★★☆ — 4 stars"),
    (3, "★★★☆☆ — 3 stars"),
    (2, "★★☆☆☆ — 2 stars"),
    (1, "★☆☆☆☆ — 1 star"),]

TESTIMONIAL_SERVICE_CHOICES = [
    ("", "Not linked to a specific service"),
    ("experience", "Experiences"),
    ("stay", "Stays"),
    ("safari", "Safaris"),]

TESTIMONIAL_FOLDER_NAME = "Testimonials"
TESTIMONIAL_FOLDER_SLUG = "testimonials"

# =============================================================================
# Validators
# =============================================================================

def validate_rating(form, field):
    """Ensure ratings are between one and five."""
    if field.data is None:
        return

    if not 1 <= field.data <= 5:
        raise ValidationError("Rating must be between 1 and 5 stars.")


# =============================================================================
# Shared Choice Setup
# =============================================================================
class TestimonialChoiceMixin:
    """
    Helpers for populating listing and Media Library selectors.

    WTForms creates the declared fields automatically. This mixin must not
    replace those fields with None in __init__.
    """

    def set_listing_choices(
        self,
        experiences=None,
        stays=None,
        safari_packages=None,
    ):
        """Populate independent Experience, Stay and Safari selectors."""

        def get_label(item, *attributes):
            """Return the first non-empty display attribute."""
            for attribute in attributes:
                value = getattr(item, attribute, None)

                if value:
                    return str(value)

            return f"Listing #{item.id}"

        experience_choices = [
            (0, "— No experience selected —"),
        ]

        for item in experiences or []:
            experience_choices.append(
                (
                    item.id,
                    get_label(
                        item,
                        "title",
                        "name",
                        "experience_code",
                        "slug",
                    ),
                )
            )

        stay_choices = [
            (0, "— No stay selected —"),
        ]

        for item in stays or []:
            stay_choices.append(
                (
                    item.id,
                    get_label(
                        item,
                        "name",
                        "title",
                        "property_name",
                        "stay_name",
                        "slug",
                        "code",
                    ),
                )
            )

        safari_choices = [
            (0, "— No safari package selected —"),
        ]

        for item in safari_packages or []:
            package_name = (
                getattr(item, "name", None)
                or getattr(item, "title", None)
                or getattr(item, "package_name", None)
                or getattr(item, "option_name", None)
            )

            property_obj = (
                getattr(item, "property", None)
                or getattr(item, "safari_property", None)
            )

            destination_obj = (
                getattr(item, "destination", None)
                or getattr(property_obj, "destination", None)
            )

            if not package_name:
                package_name = get_label(
                    item,
                    "title",
                    "package_name",
                    "option_name",
                    "slug",
                    "code",
                )

            parts = [str(package_name)]

            if property_obj is not None:
                property_name = get_label(
                    property_obj,
                    "name",
                    "title",
                    "property_name",
                )

                if property_name.startswith("Listing #"):
                    property_name = None

                if property_name:
                    parts.append(property_name)

            if destination_obj is not None:
                destination_name = get_label(
                    destination_obj,
                    "name",
                    "title",
                    "slug",
                )

                if destination_name.startswith("Listing #"):
                    destination_name = None

                if destination_name:
                    parts.append(destination_name)

            safari_choices.append(
                (item.id, " — ".join(parts))
            )

        self.experience_id.choices = experience_choices
        self.stay_id.choices = stay_choices
        self.safari_package_option_id.choices = safari_choices

    def set_media_choices(
        self,
        profile_assets=None,
        customer_assets=None,
        video_assets=None,
    ):
        """
        Populate image and video selectors.

        The route is responsible for retrieving active assets from the
        Testimonials folder and filtering each list by media type.
        """

        def build_choices(assets, empty_label):
            choices = [(0, empty_label)]

            for asset in assets or []:
                label = (
                    getattr(asset, "title", None)
                    or getattr(asset, "original_filename", None)
                    or getattr(asset, "filename", None)
                    or f"Media asset #{asset.id}"
                )

                choices.append((asset.id, str(label)))

            return choices

        self.profile_photo_asset_id.choices = build_choices(
            profile_assets,
            "— Select a profile photo —",
        )

        self.customer_photo_asset_id.choices = build_choices(
            customer_assets,
            "— Select a customer photo —",
        )

        self.video_asset_id.choices = build_choices(
            video_assets,
            "— Select a testimonial video —",
        )


# =============================================================================
# Admin Create / Edit Form
# =============================================================================
class TestimonialForm(TestimonialChoiceMixin, FlaskForm):
    """Create or edit a testimonial in the admin CMS."""

    # Customer information
    customer_name = StringField(
        "Customer name",
        validators=[
            DataRequired(message="Customer name is required."),
            Length(min=2, max=150),
        ],
        render_kw={"placeholder": "e.g. Sarah Johnson"},
    )

    customer_country = StringField(
        "Country",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g. United Kingdom"},
    )

    customer_city = StringField(
        "City",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g. London"},
    )

    company = StringField(
        "Company / organization",
        validators=[Optional(), Length(max=150)],
        render_kw={"placeholder": "Optional company or organization"},
    )

    position = StringField(
        "Position / role",
        validators=[Optional(), Length(max=150)],
        render_kw={"placeholder": "Optional role"},
    )

    # Testimonial content
    title = StringField(
        "Testimonial title",
        validators=[Optional(), Length(max=255)],
        render_kw={
            "placeholder": "e.g. An unforgettable Kenyan adventure",
        },
    )

    testimonial = TextAreaField(
        "Testimonial",
        validators=[
            DataRequired(
                message="Testimonial content is required."
            ),
        ],
        render_kw={
            "rows": 8,
            "placeholder": "Enter the full customer testimonial...",
        },
    )

    short_testimonial = TextAreaField(
        "Short testimonial",
        validators=[Optional(), Length(max=300)],
        render_kw={
            "rows": 4,
            "placeholder": (
                "Optional shorter version for cards and previews"
            ),
        },
    )

    # Rating
    rating = SelectField(
        "Rating",
        coerce=int,
        choices=TESTIMONIAL_RATING_CHOICES,
        default=5,
        validators=[InputRequired(), validate_rating],
    )

    # Listing relationships
    experience_id = SelectField(
        "Related experience",
        coerce=int,
        choices=[(0, "— No experience selected —")],
        default=0,
        validators=[Optional()],
    )

    stay_id = SelectField(
        "Related stay",
        coerce=int,
        choices=[(0, "— No stay selected —")],
        default=0,
        validators=[Optional()],
    )

    safari_package_option_id = SelectField(
        "Related safari package",
        coerce=int,
        choices=[(0, "— No safari package selected —")],
        default=0,
        validators=[Optional()],
    )

    # Media Library selectors
    profile_photo_asset_id = SelectField(
        "Profile photo — Media Library",
        coerce=int,
        choices=[(0, "— Select a profile photo —")],
        default=0,
        validators=[Optional()],
    )

    customer_photo_asset_id = SelectField(
        "Customer / experience photo — Media Library",
        coerce=int,
        choices=[(0, "— Select a customer photo —")],
        default=0,
        validators=[Optional()],
    )

    video_asset_id = SelectField(
        "Testimonial Video — Media Library",
        coerce=int,
        choices=[(0, "— Select a testimonial video —")],
        default=0,
        validators=[Optional()],
    )

    # Optional external video URL; the Media Library selector is separate.
    video_url = StringField(
        "External video URL (optional)",
        validators=[
            Optional(),
            Length(max=500),
            URL(message="Enter a valid URL, including https://."),
        ],
        render_kw={
            "placeholder": "https://...",
        },
    )

    # Source and display
    source = SelectField(
        "Testimonial source",
        choices=TESTIMONIAL_SOURCE_CHOICES,
        default="",
        validators=[Optional()],
    )

    featured = BooleanField(
        "Featured testimonial",
        default=False,
    )

    homepage = BooleanField(
        "Display on homepage",
        default=False,
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    sort_order = IntegerField(
        "Sort order",
        default=0,
        validators=[
            Optional(),
            NumberRange(min=0, max=9999),
        ],
    )

    verified = BooleanField(
        "Verified testimonial",
        default=True,)

    submit = SubmitField("Save testimonial")

# =============================================================================
# Public Testimonial Submission Form
# =============================================================================
class PublicTestimonialForm(FlaskForm):
    """
    Public form for submitting a testimonial for moderation.

    The public route must save submissions as inactive and unverified.
    Admin moderation fields are deliberately excluded.
    """

    customer_name = StringField(
        "Your name",
        validators=[
            DataRequired(message="Please enter your name."),
            Length(min=2, max=150),
        ],
        render_kw={"placeholder": "Your name"},
    )

    customer_country = StringField(
        "Country",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Country (optional)"},
    )

    customer_city = StringField(
        "City",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "City (optional)"},
    )

    title = StringField(
        "Give your testimonial a title",
        validators=[Optional(), Length(max=255)],
        render_kw={"placeholder": "A memorable experience..."},
    )

    testimonial = TextAreaField(
        "Your testimonial",
        validators=[
            DataRequired(
                message="Please share your experience."
            ),
            Length(min=10, max=5000),
        ],
        render_kw={
            "rows": 7,
            "placeholder": (
                "Tell us about your experience with The Uncharted Route..."
            ),
        },
    )

    rating = SelectField(
        "Your rating",
        coerce=int,
        choices=TESTIMONIAL_RATING_CHOICES,
        default=5,
        validators=[InputRequired(), validate_rating],
    )

    service_category = SelectField(
        "What was your experience with?",
        choices=TESTIMONIAL_SERVICE_CHOICES,
        default="",
        validators=[Optional()],
    )

    experience_id = SelectField(
        "Experience",
        coerce=int,
        choices=[(0, "Choose an experience (optional)")],
        default=0,
        validators=[Optional()],)

    stay_id = SelectField(
        "Stay",
        coerce=int,
        choices=[(0, "Choose a stay (optional)")],
        default=0,
        validators=[Optional()],)

    safari_package_option_id = SelectField(
        "Safari package",
        coerce=int,
        choices=[(0, "Choose a safari package (optional)")],
        default=0,
        validators=[Optional()],)

    # These are selectors, not file-upload controls. Populate them only
    # with assets that the public submission workflow is allowed to use.
    profile_photo_asset_id = SelectField(
        "Profile photo",
        coerce=int,
        choices=[(0, "No image selected")],
        default=0,
        validators=[Optional()],)

    customer_photo_asset_id = SelectField(
        "Customer / experience photo",
        coerce=int,
        choices=[(0, "No image selected")],
        default=0,
        validators=[Optional()],)

    customer_email = StringField(
        "Your email address",
        validators=[
            DataRequired(message="Please enter your email address."),
            Email(message="Please enter a valid email address."),
            Length(max=255),
        ],
        render_kw={
            "type": "email",
            "placeholder": "you@example.com",
            "autocomplete": "email",},)
    submit = SubmitField("Submit testimonial")

# =============================================================================
# Filter Form
# =============================================================================
class TestimonialFilterForm(TestimonialChoiceMixin, FlaskForm):
    """Filter and search testimonials in the admin CMS."""

    search = StringField(
        "Search",
        validators=[Optional(), Length(max=255)],
        render_kw={
            "placeholder": (
                "Search customer, country, company or testimonial..."
            ),
        },
    )

    experience_id = SelectField(
        "Experience",
        coerce=int,
        choices=[(0, "All experiences")],
        default=0,
        validators=[Optional()],
    )

    stay_id = SelectField(
        "Stay",
        coerce=int,
        choices=[(0, "All stays")],
        default=0,
        validators=[Optional()],
    )

    safari_package_option_id = SelectField(
        "Safari package",
        coerce=int,
        choices=[(0, "All safari packages")],
        default=0,
        validators=[Optional()],
    )

    rating = SelectField(
        "Rating",
        coerce=int,
        choices=[(0, "All ratings")] + TESTIMONIAL_RATING_CHOICES,
        default=0,
        validators=[Optional()],
    )

    source = SelectField(
        "Source",
        choices=[("", "All sources")] + TESTIMONIAL_SOURCE_CHOICES[1:],
        default="",
        validators=[Optional()],
    )

    featured = SelectField(
        "Featured",
        choices=[
            ("", "All"),
            ("1", "Featured"),
            ("0", "Not featured"),
        ],
        default="",)

    homepage = SelectField(
        "Homepage",
        choices=[
            ("", "All"),
            ("1", "On homepage"),
            ("0", "Not on homepage"),
        ],
        default="",)

    active = SelectField(
        "Status",
        choices=[
            ("", "All statuses"),
            ("1", "Active"),
            ("0", "Inactive"),
        ],
        default="",
    )

    verified = SelectField(
        "Verification",
        choices=[
            ("", "All"),
            ("1", "Verified"),
            ("0", "Unverified"),
        ],
        default="",)

    sort = SelectField(
        "Sort by",
        choices=TESTIMONIAL_SORT_CHOICES,
        default="sort_order",)

    submit = SubmitField("Filter")


# =============================================================================
# Sort Form
# =============================================================================
class TestimonialSortForm(FlaskForm):
    """Update testimonial display order."""
    sort_order = IntegerField(
        "Sort order",
        validators=[
            InputRequired(),
            NumberRange(min=0, max=9999),],)

    submit = SubmitField("Update order")

# =============================================================================
# Featured Form
# =============================================================================
class TestimonialFeatureForm(FlaskForm):
    """Toggle featured status."""
    action = HiddenField(validators=[Optional()])
    submit = SubmitField("Update featured status")

# =============================================================================
# Homepage Form
# =============================================================================
class TestimonialHomepageForm(FlaskForm):
    """Toggle homepage visibility."""
    action = HiddenField(validators=[Optional()])
    submit = SubmitField("Update homepage status")

# =============================================================================
# Verification Form
# =============================================================================

class TestimonialVerificationForm(FlaskForm):
    """Toggle testimonial verification status."""

    action = HiddenField(validators=[Optional()])
    submit = SubmitField("Update verification")

# =============================================================================
# Status Form
# =============================================================================
class TestimonialStatusForm(FlaskForm):
    """Activate or deactivate a testimonial."""

    active = BooleanField("Active", default=True)
    submit = SubmitField("Update status")

# =============================================================================
# Delete Form
# =============================================================================
class TestimonialDeleteForm(FlaskForm):
    """Confirm deletion of a testimonial."""
    confirm = BooleanField(
        "Confirm deletion",
        validators=[
            DataRequired(message="Please confirm deletion."),],)

    submit = SubmitField("Delete testimonial")