"""
===============================================================================
Core Public-Facing Routes
===============================================================================
This blueprint handles:
- Homepage
- About page
- Contact page
- Contact enquiry submission
- Contact submission confirmation
Business logic for contact enquiries is delegated to ContactService.
===============================================================================
"""
import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash, current_app, abort,)
from app.forms.contact_form import ContactForm
from app.forms.testimonial import PublicTestimonialForm
from app.models import Experience, Stay, SafariPackageOption, Testimonial, NewsletterSubscriber
from app.services.admin.admin_legal_help_service import LegalHelpService
from app.services.contact_service import ContactService
from app.services.page_hero_service import PageHeroService
from app.services.email_service import email_service
from app.services.settings_service import SettingsService
from app.services.testimonial_service import TestimonialService
import os
import uuid
from werkzeug.utils import secure_filename
from app.models.promotion import Promotion
from app.services.promotion_service import PromotionService
from extensions import db

# =============================================================================
# Blueprint
# =============================================================================
main_bp = Blueprint(
    "main",
    __name__,)

# =============================================================================
# Public Homepage
# =============================================================================
@main_bp.route("/")
def home():
    """
    Public homepage driven by the Homepage CMS and selected records.
    """

    from app.models import (
        Homepage,
        HomepageSection,
        Destination,
        Experience,
        Stay,
        Testimonial,
    )

    # -------------------------------------------------------------------------
    # Current homepage
    # -------------------------------------------------------------------------

    homepage = Homepage.get_current()

    if not homepage or not homepage.is_published:
        return render_template("404.html"), 404

    # -------------------------------------------------------------------------
    # Visible CMS sections
    # -------------------------------------------------------------------------

    sections = (
        HomepageSection.query
        .filter(
            HomepageSection.homepage_id == homepage.id,
            HomepageSection.is_visible.is_(True),
        )
        .order_by(
            HomepageSection.display_order.asc(),
            HomepageSection.id.asc(),
        )
        .all()
    )

    sections_by_type = {}

    for section in sections:
        sections_by_type.setdefault(
            section.section_type,
            [],
        ).append(section)

    # -------------------------------------------------------------------------
    # Homepage destinations
    # -------------------------------------------------------------------------
    featured_destinations = (
        Destination.query
        .filter(
            Destination.active.is_(True),
            Destination.featured.is_(True),
            Destination.show_on_homepage.is_(True),
        )
        .order_by(
            Destination.name.asc(),
            Destination.id.asc(),
        )
        .limit(3)
        .all()
    )

    # -------------------------------------------------------------------------
    # Homepage experiences
    # -------------------------------------------------------------------------
    featured_experiences = (
        Experience.query
        .filter(
            Experience.active.is_(True),
            Experience.featured.is_(True),
            Experience.show_on_homepage.is_(True),
        )
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
            Experience.id.asc(),
        )
        .limit(3)
        .all())

    # -------------------------------------------------------------------------
    # Homepage stays
    # -------------------------------------------------------------------------
    featured_stays = (
        Stay.query
        .filter(
            Stay.active.is_(True),
            Stay.show_on_homepage.is_(True),
        )
        .order_by(
            Stay.display_order.asc(),
            Stay.property_name.asc(),
            Stay.id.asc(),
        )
        .limit(3)
        .all())

    # -------------------------------------------------------------------------
    # Homepage testimonials
    # Active + Verified + Explicitly Selected for Homepage
    # -------------------------------------------------------------------------
    homepage_testimonials = (
        Testimonial.query
        .filter(
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
            Testimonial.homepage.is_(True),
        )
        .order_by(
            Testimonial.sort_order.asc(),
            Testimonial.created_at.desc(),
            Testimonial.id.desc(),
        )
        .all())

    # -------------------------------------------------------------------------
    # Featured Promotions
    # -------------------------------------------------------------------------
    featured_promotions = (
        PromotionService.get_public_query()
        .filter(Promotion.show_on_homepage.is_(True))
        .order_by(
            Promotion.created_at.desc(),
            Promotion.id.desc(),
        )
        .limit(3)
        .all())

    return render_template(
        "index.html",
        homepage=homepage,
        sections=sections,
        sections_by_type=sections_by_type,
        featured_destinations=featured_destinations,
        featured_experiences=featured_experiences,
        featured_stays=featured_stays,
        homepage_testimonials=homepage_testimonials,
        featured_promotions=featured_promotions,)

def _sync_contact_newsletter_opt_in(form):
    """Record an explicit contact-form newsletter opt-in."""
    if not form.newsletter_opt_in.data:
        return "not_requested"

    email = form.email.data.strip().lower()
    subscriber = NewsletterSubscriber.query.filter_by(email=email).first()

    # Preserve all preferences for an existing active subscriber
    # who has already given marketing consent.
    if (
        subscriber
        and subscriber.subscribed
        and subscriber.marketing_consent
    ):
        subscriber.first_name = form.first_name.data.strip()
        subscriber.last_name = (
            form.last_name.data.strip()
            if form.last_name.data else None
        )
        if form.country.data:
            subscriber.country = form.country.data.strip()

        db.session.commit()

        if subscriber.verified:
            return "already_subscribed"

        # An existing, unverified subscriber still needs verification.
        if not subscriber.verification_token:
            subscriber.verification_token = uuid.uuid4().hex
            db.session.commit()

        from app.routes.public_newsletter import _send_verification_email

        sent = _send_verification_email(subscriber)
        return "verification_sent" if sent else "verification_failed"

    now = datetime.datetime.now(datetime.timezone.utc)

    if subscriber is None:
        subscriber = NewsletterSubscriber(
            email=email,
            source="Website Contact Form",
        )
        db.session.add(subscriber)

    subscriber.first_name = form.first_name.data.strip()
    subscriber.last_name = (
        form.last_name.data.strip()
        if form.last_name.data else None
    )
    subscriber.country = (
        form.country.data.strip()
        if form.country.data else None
    )

    subscriber.subscribed = True
    subscriber.marketing_consent = True
    subscriber.consent_date = now
    subscriber.unsubscribed_at = None

    # The contact checkbox must clearly disclose all four categories.
    # These defaults apply only to a fresh opt-in or re-subscription.
    subscriber.receive_promotions = True
    subscriber.receive_new_experiences = True
    subscriber.receive_blog_updates = True
    subscriber.receive_company_news = True

    subscriber.verified = False
    subscriber.verification_token = uuid.uuid4().hex

    db.session.commit()

    from app.routes.public_newsletter import _send_verification_email

    sent = _send_verification_email(subscriber)

    if not sent:
        current_app.logger.error(
            "Newsletter verification email failed for %s.", email)
        return "verification_failed"
    return "verification_sent"

# =============================================================================
# Contact
# =============================================================================
@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """Public contact page."""

    form = ContactForm()
    page_hero = PageHeroService.get_by_page_key("contact")

    # -------------------------------------------------------------------------
    # Site settings
    # -------------------------------------------------------------------------
    # Public contact details are managed from:
    # Admin → Site Settings → Public Contact Information
    #
    # This is the same SiteSetting record containing:
    #   - email
    #   - phone
    #   - whatsapp
    #   - address
    #   - city
    #   - country
    #   - show_email
    #   - show_phone
    #
    settings = SettingsService.get_settings()

    if form.validate_on_submit():
        try:
            contact = ContactService.create_contact(
                first_name=form.first_name.data.strip(),
                last_name=(
                    form.last_name.data.strip()
                    if form.last_name.data
                    else None
                ),
                email=form.email.data.strip().lower(),
                phone=(
                    form.phone.data.strip()
                    if form.phone.data
                    else None
                ),
                company=(
                    form.company.data.strip()
                    if form.company.data
                    else None
                ),
                country=(
                    form.country.data.strip()
                    if form.country.data
                    else None
                ),
                subject=form.subject.data.strip(),
                enquiry_type=form.enquiry_type.data,
                message=form.message.data.strip(),
                priority="Normal",
                follow_up_required=True,
                newsletter_opt_in=bool(form.newsletter_opt_in.data),
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
                source="Website",
            )

        except Exception:
            current_app.logger.exception(
                "Failed to save website contact enquiry."
            )
            db.session.rollback()

            flash(
                "We couldn't submit your message right now. Please try again.",
                "danger",
            )

            return render_template(
                "contact.html",
                form=form,
                page_hero=page_hero,
                settings=settings,
            )

        # ---------------------------------------------------------
        # Newsletter integration — AFTER saving the contact enquiry
        # ---------------------------------------------------------
        newsletter_status = "not_requested"

        if form.newsletter_opt_in.data:
            try:
                newsletter_status = _sync_contact_newsletter_opt_in(form)

            except Exception:
                db.session.rollback()

                current_app.logger.exception(
                    "Newsletter opt-in failed for contact ID %s.",
                    getattr(contact, "id", "unknown"),
                )

                newsletter_status = "failed"

        # ---------------------------------------------------------
        # Internal notification email
        # ---------------------------------------------------------
        try:
            internal_email_sent = email_service.send_contact_notification(
                contact
            )

            if not internal_email_sent:
                current_app.logger.error(
                    "Internal contact notification failed for contact ID %s.",
                    getattr(contact, "id", "unknown"),
                )

        except Exception:
            current_app.logger.exception(
                "Internal contact notification raised an exception for "
                "contact ID %s.",
                getattr(contact, "id", "unknown"),
            )

        # ---------------------------------------------------------
        # Customer acknowledgement email
        # — independent of internal email
        # ---------------------------------------------------------
        customer_name = (
            f"{form.first_name.data.strip()} "
            f"{form.last_name.data.strip() if form.last_name.data else ''}"
        ).strip()

        customer_email = form.email.data.strip().lower()
        subject = form.subject.data.strip()

        try:
            customer_email_sent = email_service.send_email(
                recipient=customer_email,
                subject="We've received your message | The Uncharted Route",
                body=(
                    f"Hello {customer_name},\n\n"
                    "Thank you for contacting The Uncharted Route.\n\n"
                    "We've received your message and our team will get "
                    "back to you as soon as possible.\n\n"
                    f"Subject: {subject}\n\n"
                    "Thank you for reaching out to us.\n\n"
                    "The Uncharted Route\n"
                    "Explore. Experience. Remember."
                ),
                html_body=f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport"
                              content="width=device-width, initial-scale=1.0">
                        <title>Message Received</title>
                    </head>

                    <body style="margin:0;padding:24px;background:#F7F1E5;
                                 color:#1C2822;font-family:Arial,sans-serif;">

                        <div style="max-width:600px;margin:auto;background:#fff;
                                    padding:32px;border-radius:8px;">

                            <h2 style="color:#12372A;">
                                Thank you for reaching out.
                            </h2>

                            <p>Hello {customer_name},</p>

                            <p>
                                We've received your message and our team
                                will get back to you as soon as possible.
                            </p>

                            <p>
                                <strong>Your subject:</strong> {subject}
                            </p>

                            <p>
                                Thank you for considering The Uncharted Route.
                            </p>

                            <p style="color:#12372A;font-weight:bold;">
                                The Uncharted Route
                            </p>

                            <p style="color:#66736B;">
                                Explore. Experience. Remember.
                            </p>

                        </div>

                    </body>
                    </html>
                """,
            )

            if not customer_email_sent:
                current_app.logger.error(
                    "Contact confirmation email was not sent for contact "
                    "ID %s.",
                    getattr(contact, "id", "unknown"),
                )

        except Exception:
            current_app.logger.exception(
                "Customer acknowledgement email failed for contact ID %s.",
                getattr(contact, "id", "unknown"),
            )

        # ---------------------------------------------------------
        # Success-page acknowledgements
        # ---------------------------------------------------------
        flash(
            "Your message has been submitted successfully. "
            "We'll get back to you as soon as possible.",
            "success",
        )

        if newsletter_status == "verification_sent":
            flash(
                "Your newsletter signup has been received. Please check "
                "your email and verify your address to activate it.",
                "info",
            )

        elif newsletter_status == "already_subscribed":
            flash(
                "You're already subscribed to our newsletter. "
                "Your existing preferences have been kept.",
                "info",
            )

        elif newsletter_status == "verification_failed":
            flash(
                "Your message was submitted, but we couldn't send the "
                "newsletter verification email. Please try signing up "
                "again from our newsletter page.",
                "warning",
            )

        elif newsletter_status == "failed":
            flash(
                "Your message was submitted, but we couldn't complete "
                "your newsletter signup. Please try our newsletter page.",
                "warning",
            )

        return redirect(url_for("main.contact_success"))

    # -------------------------------------------------------------------------
    # GET / validation failure
    # -------------------------------------------------------------------------
    return render_template(
        "contact.html",
        form=form,
        page_hero=page_hero,
        settings=settings,
    )

# =============================================================================
# Contact Success
# =============================================================================
@main_bp.route("/contact/success")
def contact_success():
    """
    Confirmation page shown after a successful
    contact submission.
    """

    return render_template(
        "contact_success.html"
    )

# =============================================================================
# Public Testimonials
# =============================================================================
def _public_testimonial_choices(form):
    """
    Populate public listing selectors with active listings only.
    Public visitors cannot select arbitrary database IDs.
    """
    experiences = (
        Experience.query
        .filter(Experience.active.is_(True))
        .order_by(Experience.title.asc())
        .all()
    )

    stays = (
        Stay.query
        .filter(Stay.active.is_(True))
        .order_by(Stay.property_name.asc())
        .all()
    )

    safari_query = SafariPackageOption.query

    # Support models that expose an active flag.
    if hasattr(SafariPackageOption, "active"):
        safari_query = safari_query.filter(
            SafariPackageOption.active.is_(True)
        )

    safari_packages = safari_query.order_by(
        SafariPackageOption.id.asc()
    ).all()

    form.experience_id.choices = [
        (0, "Choose an experience (optional)")
    ] + [
        (item.id, item.title)
        for item in experiences
    ]

    form.stay_id.choices = [
        (0, "Choose a stay (optional)")
    ] + [
        (item.id, item.property_name)
        for item in stays
    ]

    def safari_label(item):
        for attr in ("name", "title"):
            value = getattr(item, attr, None)
            if value:
                return value

        package = getattr(item, "package", None)
        if package:
            return (
                getattr(package, "name", None)
                or getattr(package, "title", None)
                or f"Safari package #{item.id}"
            )

        return f"Safari package #{item.id}"

    form.safari_package_option_id.choices = [
        (0, "Choose a safari package (optional)")
    ] + [
        (item.id, safari_label(item))
        for item in safari_packages
    ]

    # The public form does not grant access to the internal DAM.
    # Visitors cannot select arbitrary internal media assets.
    form.profile_photo_asset_id.choices = [
        (0, "No image selected")
    ]
    form.customer_photo_asset_id.choices = [
        (0, "No image selected")
    ]

    return experiences, stays, safari_packages

def _save_testimonial_customer_photo(file_storage):
    """
    Validate and save a customer's uploaded testimonial photo.
    Returns a static-relative path, or None if no photo was supplied.
    """
    if not file_storage or not file_storage.filename:
        return None

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    original_name = secure_filename(file_storage.filename)
    extension = os.path.splitext(original_name)[1].lower()

    if not original_name or extension not in allowed_extensions:
        raise ValueError(
            "Please upload a JPG, PNG, or WEBP image."
        )

    max_size = 5 * 1024 * 1024  # 5 MB
    file_storage.stream.seek(0, os.SEEK_END)
    file_size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    if file_size == 0:
        raise ValueError("The selected image is empty.")

    if file_size > max_size:
        raise ValueError("Your image must be 5 MB or smaller.")

    filename = f"{uuid.uuid4().hex}{extension}"
    relative_directory = os.path.join(
        "uploads",
        "testimonials",
    )

    absolute_directory = os.path.join(
        current_app.static_folder,
        relative_directory,
    )
    os.makedirs(absolute_directory, exist_ok=True)

    absolute_path = os.path.join(
        absolute_directory,
        filename,
    )

    file_storage.save(absolute_path)

    return os.path.join(
        relative_directory,
        filename,
    ).replace("\\", "/")

@main_bp.route("/testimonials")
def testimonials():
    """Display approved public testimonials."""
    page_hero = PageHeroService.get_by_page_key("testimonials")

    testimonials_list = (
        Testimonial.query
        .filter(
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        )
        .order_by(
            Testimonial.sort_order.asc(),
            Testimonial.created_at.desc(),
            Testimonial.id.desc(),
        )
        .all())

    return render_template(
        "testimonials/index.html",
        testimonials=testimonials_list,
        page_hero=page_hero,)


@main_bp.route("/testimonials/submit", methods=["GET", "POST"])
def submit_testimonial():
    """Accept testimonials for administrator moderation."""

    form = PublicTestimonialForm()
    _public_testimonial_choices(form)

    if form.validate_on_submit():
        experience_id = form.experience_id.data or None
        stay_id = form.stay_id.data or None
        safari_option_id = form.safari_package_option_id.data or None

        # A testimonial may be linked to at most one listing.
        selected_listing_ids = [
            value
            for value in (
                experience_id,
                stay_id,
                safari_option_id,
            )
            if value
        ]

        if len(selected_listing_ids) > 1:
            flash(
                "Please select only one experience, stay, or safari package.",
                "warning",
            )
            return render_template(
                "testimonials/submit.html",
                form=form,
            )

        # Revalidate selected listings against active database records.
        if experience_id and not Experience.query.filter_by(
            id=experience_id,
            active=True,
        ).first():
            form.experience_id.errors.append(
                "Please choose an available experience."
            )

        if stay_id and not Stay.query.filter_by(
            id=stay_id,
            active=True,
        ).first():
            form.stay_id.errors.append(
                "Please choose an available stay."
            )

        if safari_option_id:
            safari_query = SafariPackageOption.query.filter_by(
                id=safari_option_id
            )

            if hasattr(SafariPackageOption, "active"):
                safari_query = safari_query.filter_by(active=True)

            if not safari_query.first():
                form.safari_package_option_id.errors.append(
                    "Please choose an available safari package."
                )

        if form.errors:
            return render_template(
                "testimonials/submit.html",
                form=form,
            )

        customer_name = form.customer_name.data.strip()
        customer_email = form.customer_email.data.strip().lower()
        testimonial_text = form.testimonial.data.strip()
        title = (form.title.data or "").strip() or None

        # Optional photo uploaded by the customer.
        # This is a file path, not a Media Library asset ID.
        customer_photo_path = None

        try:
            customer_photo_path = _save_testimonial_customer_photo(
                request.files.get("customer_photo_file")
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "testimonials/submit.html",
                form=form,
            )

        try:
            testimonial = TestimonialService.create_testimonial(
                customer_name=customer_name,
                customer_email=customer_email,
                customer_country=(
                    form.customer_country.data.strip()
                    if form.customer_country.data
                    else None
                ),
                customer_city=(
                    form.customer_city.data.strip()
                    if form.customer_city.data
                    else None
                ),
                title=title,
                testimonial=testimonial_text,
                short_testimonial=(
                    testimonial_text[:297] + "..."
                    if len(testimonial_text) > 300
                    else testimonial_text
                ),
                rating=form.rating.data,
                experience_id=experience_id,
                stay_id=stay_id,
                safari_package_option_id=safari_option_id,

                # Public customers cannot select internal Media Library assets.
                profile_photo_asset_id=None,
                customer_photo_asset_id=None,
                video_asset_id=None,

                # The optional uploaded photo uses the legacy path field.
                customer_photo=customer_photo_path,

                # Public submissions require admin moderation.
                featured=False,
                homepage=False,
                active=False,
                verified=False,
                sort_order=0,
                source="Website",
            )

        except Exception:
            current_app.logger.exception(
                "Failed to save public testimonial."
            )
            flash(
                "We couldn't submit your testimonial right now. "
                "Please try again.",
                "danger",
            )
            return render_template(
                "testimonials/submit.html",
                form=form,
            )

        # Send emails only after the testimonial has been saved.
        # Email failures must not undo the database record.
        try:
            customer_email_sent = (
                email_service.send_testimonial_received_email(
                    testimonial,
                    customer_email,
                )
            )

            if not customer_email_sent:
                current_app.logger.error(
                    "Testimonial confirmation email failed for ID %s.",
                    testimonial.id,
                )

            admin_email_sent = (
                email_service.send_testimonial_admin_notification(
                    testimonial
                )
            )

            if not admin_email_sent:
                current_app.logger.error(
                    "Testimonial admin notification failed for ID %s.",
                    testimonial.id,
                )

        except Exception:
            current_app.logger.exception(
                "Email processing failed for testimonial ID %s.",
                testimonial.id,
            )

        flash(
            "Thank you for sharing your experience. Your testimonial "
            "has been received and will be reviewed before publication.",
            "success",
        )

        return redirect(url_for("main.testimonial_success"))

    return render_template(
        "testimonials/submit.html",
        form=form,
    )

@main_bp.route("/testimonials/success")
def testimonial_success():
    """Confirmation page after a testimonial submission."""
    return render_template("testimonials/success.html")

# =============================================================================
# About
# =============================================================================
@main_bp.route("/about")
def about():
    page = LegalHelpService.get_public_page("about")

    if not page:
        abort(404)

    return render_template(
        "about.html",
        page=page,)

# =============================================================================
# FAQ
# =============================================================================
@main_bp.route("/faq")
def faq():
    page = LegalHelpService.get_public_page("faq")

    if not page:
        abort(404)

    return render_template(
        "faq.html",
        page=page,
    )


# =============================================================================
# Privacy
# =============================================================================

@main_bp.route("/privacy")
def privacy():
    page = LegalHelpService.get_public_page("privacy")

    if not page:
        abort(404)

    return render_template(
        "privacy.html",
        page=page,
    )


# =============================================================================
# Terms
# =============================================================================
@main_bp.route("/terms")
def terms():
    page = LegalHelpService.get_public_page("terms")

    if not page:
        abort(404)

    return render_template(
        "terms.html",
        page=page,
    )
@main_bp.app_errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


@main_bp.app_errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@main_bp.app_errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500
