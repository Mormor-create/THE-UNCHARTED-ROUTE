"""
===============================================================================
The Uncharted Route
Administrative Routes
===============================================================================
Protected administrative routes for The Uncharted Route.
Responsibilities
----------------
• Administrator authentication
• Administrator-created staff accounts
• Administrator-created guide accounts
• Administrator password recovery
• Administrator password reset
• Administrator dashboard
• Administrator logout
• Administrative access control
• Administrative error handling

Business logic is delegated to services.
Forms handle validation.
Models handle persistence and model behavior.

The admin blueprint should remain thin:

    Route → Form/Service → Model

Security Boundary
-----------------
Only active administrators may access administrative routes.

Public registration is handled separately and can only create customer
accounts.

Administrative registration can create only:

    • Staff
    • Guide

Administrator accounts cannot be created through the admin registration
interface.
===============================================================================
"""

from flask import (
    flash,
    redirect,
    render_template,
    url_for, request,)
from flask_login import (
    current_user,
    login_user,
    logout_user, login_required, )
from app.decorators.admin import admin_required
from app.forms.admin_auth import (
    AdminForgotPasswordForm,
    AdminLoginForm,
    AdminResetPasswordForm,
    AdminUserCreateForm,)
from app.services.admin.admin_authentication_service import (
    authenticate_admin,
    can_access_admin,
    complete_admin_login,
    create_internal_user,
    generate_admin_password_reset_token,
    reset_admin_password,
    verify_admin_password_reset_token,)
from app.models import User
from app.forms.admin_profile import (
    AdminProfileForm,
    AdminPasswordForm,)
from app.forms.access_control import (
    AccessControlFilterForm,
    UserRoleForm,
    UserStatusForm,
    UserVerificationForm,)
from . import admin_bp
# =============================================================================
# Admin Login
# =============================================================================
@admin_bp.route("/login",methods=["GET", "POST"],)
def login():
    """
    Administrative login page.

    GET
        Display the administrator login form.

    POST
        Validate credentials and authenticate an administrator.

    Authenticated administrators are redirected to the dashboard.

    Authenticated non-administrators are not granted administrative access.
    """

    # -------------------------------------------------------------------------
    # Already authenticated administrators do not need to log in again.
    # -------------------------------------------------------------------------

    if current_user.is_authenticated and current_user.is_admin:
        if current_user.is_active:
            return redirect(url_for("admin.dashboard"))

        flash(
            "Your administrator account is inactive.",
            "error",
        )
        return redirect(url_for("main.home"))

    # An authenticated customer or other non-admin user
    # may still open the admin login form.
    # A successful admin login will replace the current
    # Flask-Login session with the administrator account.

    # -------------------------------------------------------------------------
    # Login form
    # -------------------------------------------------------------------------
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = authenticate_admin(
            identity=form.identity.data,
            password=form.password.data,)

        if user is None:

            flash(
                "Invalid administrator credentials.",
                "danger",
            )

            return render_template(
                "admin/auth/login.html",
                form=form,
            )

        # ---------------------------------------------------------------------
        # Record the successful administrator login.
        # ---------------------------------------------------------------------

        complete_admin_login(
            user
        )

        # ---------------------------------------------------------------------
        # Establish the Flask-Login session.
        # ---------------------------------------------------------------------

        login_user(
            user,
            remember=False,
        )

        flash(
            f"Welcome back, {user.first_name}.",
            "success",
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    return render_template(
        "admin/auth/login.html",
        form=form,
    )

# =============================================================================
# Administrator-Created User Registration
# =============================================================================
@admin_bp.route("/register",methods=["GET", "POST"],)
@admin_required
def register():
    """
    Create a staff or guide account.
    This route is strictly administrator-only.
    Supported roles
    ---------------
    • staff
    • guide

    Administrator accounts cannot be created through this route.
    """

    form = AdminUserCreateForm()
    if form.validate_on_submit():

        try:

            user = create_internal_user(
                acting_admin=current_user,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                role=form.role.data,
            )

        except PermissionError:

            flash(
                "You do not have permission to create internal users.",
                "danger",
            )

            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        except ValueError as error:

            flash(
                str(error),
                "danger",
            )

            return render_template(
                "admin/auth/register.html",
                form=form,
            )

        flash(
            f"{user.role.capitalize()} account for "
            f"{user.full_name} was created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin.register"
            )
        )

    return render_template(
        "admin/auth/register.html",
        form=form,
    )


# =============================================================================
# Administrator Forgot Password
# =============================================================================
@admin_bp.route("/forgot-password",methods=["GET", "POST"],)
def forgot_password():
    """
    Administrator password-recovery request.

    The response deliberately does not reveal whether an email address
    belongs to an administrator.

    The actual delivery of the generated reset link should be handled by
    the application's email service.
    """

    if current_user.is_authenticated:

        if current_user.is_admin:
            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        return redirect(
            url_for(
                "main.home"
            )
        )

    form = AdminForgotPasswordForm()

    if form.validate_on_submit():

        email = (
            form.email.data.strip().lower()
        )

        user = User.query.filter(
            User.email.ilike(email)
        ).first()

        # ---------------------------------------------------------------------
        # Only active administrators receive an administrative reset token.
        # ---------------------------------------------------------------------

        if (
            user is not None
            and can_access_admin(user)
        ):

            token = generate_admin_password_reset_token(
                user
            )

            # -----------------------------------------------------------------
            # The token is intentionally not displayed or returned here.
            #
            # The email service should use this token to construct:
            #
            # /admin/reset-password/<token>
            #
            # We keep email delivery outside this route so that authentication
            # remains independent from the application's mail implementation.
            # -----------------------------------------------------------------

            reset_url = url_for(
                "admin.reset_password",
                token=token,
                _external=True,
            )

            # -----------------------------------------------------------------
            # The variable is intentionally prepared for the future mail
            # service. Do not expose it in the HTTP response.
            # -----------------------------------------------------------------

            _ = reset_url

        # ---------------------------------------------------------------------
        # Always return the same message.
        # This prevents account enumeration through the password-recovery
        # endpoint.
        # ---------------------------------------------------------------------

        flash(
            "If an administrator account exists for that email address, "
            "a password-reset link has been sent.",
            "success",)
        return redirect(
            url_for("admin.forgot_password"))
    return render_template("admin/auth/forgot_password.html",form=form,)

# =============================================================================
# Administrator Reset Password
# =============================================================================
@admin_bp.route("/reset-password/<token>",methods=["GET", "POST"],)
def reset_password(token):
    """
    Reset an administrator password using a signed token.

    Only tokens belonging to active administrator accounts are accepted.
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        return redirect(
            url_for(
                "main.home"
            )
        )

    user = verify_admin_password_reset_token(
        token
    )

    if user is None:

        flash(
            "That password-reset link is invalid or has expired.",
            "danger",
        )

        return redirect(
            url_for(
                "admin.forgot_password"
            )
        )

    form = AdminResetPasswordForm()

    if form.validate_on_submit():

        updated_user = reset_admin_password(
            user=user,
            password=form.password.data,
        )

        if updated_user is None:

            flash(
                "Unable to reset the administrator password.",
                "danger",
            )

            return render_template(
                "admin/auth/reset_password.html",
                form=form,
            )

        flash(
            "Your administrator password has been reset successfully. "
            "You may now sign in.",
            "success",
        )

        return redirect(
            url_for(
                "admin.login"
            )
        )

    return render_template(
        "admin/auth/reset_password.html",
        form=form,
    )
# =============================================================================
# Admin Dashboard
# =============================================================================
from flask import render_template
from flask_login import current_user
from sqlalchemy import func
from extensions import db
from app.models import (
    Experience,
    Destination,
    Booking,
    Contact,
    BlogPost,
    BlogCategory,
    Testimonial,
    User,)
from app.models import Staff
from app.models import (
    SafariInquiry,
    StayInquiry,
    ExperienceInquiry,)
from app.models import NewsletterSubscriber, Newsletter

# =============================================================================
# Dashboard
# =============================================================================
@admin_bp.route("/")
@admin_required
def dashboard():
    """
    Main administrative dashboard.
    Provides a high-level overview of the systems managed through
    the administration area.
    Includes:
    • Experiences
    • Destinations
    • Bookings
    • Enquiries
    • Blog posts
    • Blog categories
    • Testimonials
    • Users
    • Staff
    • Guides
    • Active / inactive content
    • Featured content
    • Homepage content
    • Booking status overview
    • Testimonial rating overview
    """
    # =========================================================================
    # Experiences
    # =========================================================================
    experience_count = (
        db.session.query(func.count(Experience.id))
        .scalar()or 0)

    active_experience_count = 0
    inactive_experience_count = 0
    featured_experience_count = 0

    if hasattr(Experience, "active"):
        active_experience_count = (
            db.session.query(func.count(Experience.id))
            .filter(Experience.active.is_(True))
            .scalar()
            or 0
        )

        inactive_experience_count = (
            db.session.query(func.count(Experience.id))
            .filter(Experience.active.is_(False))
            .scalar()
            or 0)

    if hasattr(Experience, "featured"):
        featured_experience_count = (
            db.session.query(func.count(Experience.id))
            .filter(Experience.featured.is_(True))
            .scalar()
            or 0)

    # =========================================================================
    # Destinations
    # =========================================================================
    destination_count = (
        db.session.query(func.count(Destination.id))
        .scalar()
        or 0)

    active_destination_count = 0
    inactive_destination_count = 0
    featured_destination_count = 0

    if hasattr(Destination, "active"):
        active_destination_count = (
            db.session.query(func.count(Destination.id))
            .filter(Destination.active.is_(True))
            .scalar()
            or 0
        )

        inactive_destination_count = (
            db.session.query(func.count(Destination.id))
            .filter(Destination.active.is_(False))
            .scalar()
            or 0
        )

    if hasattr(Destination, "featured"):
        featured_destination_count = (
            db.session.query(func.count(Destination.id))
            .filter(Destination.featured.is_(True))
            .scalar()
            or 0
        )


    # =========================================================================
    # Bookings
    # =========================================================================
    booking_count = (
        db.session.query(func.count(Booking.id))
        .scalar()
        or 0)

    # -------------------------------------------------------------------------
    # Booking status counts
    # -------------------------------------------------------------------------
    pending_booking_count = 0
    confirmed_booking_count = 0
    completed_booking_count = 0
    cancelled_booking_count = 0
    if hasattr(Booking, "status"):
        pending_booking_count = (
            db.session.query(func.count(Booking.id))
            .filter(
                func.lower(Booking.status) == "pending"
            ).scalar()or 0)

        confirmed_booking_count = (
            db.session.query(func.count(Booking.id))
            .filter(
                func.lower(Booking.status) == "confirmed"
            ).scalar()or 0)

        completed_booking_count = (
            db.session.query(func.count(Booking.id))
            .filter(
                func.lower(Booking.status) == "completed").scalar()or 0)

        cancelled_booking_count = (
            db.session.query(func.count(Booking.id))
            .filter(
                func.lower(Booking.status) == "cancelled")
            .scalar()
            or 0)

    # =========================================================================
    # Enquiries / Contacts
    # =========================================================================
    enquiry_count = (
        db.session.query(func.count(Contact.id))
        .scalar()
        or 0)

    unread_enquiry_count = 0
    open_enquiry_count = 0
    resolved_enquiry_count = 0
    archived_enquiry_count = 0

    if hasattr(Contact, "is_read"):

        unread_enquiry_count = (
            db.session.query(func.count(Contact.id))
            .filter(
                Contact.is_read.is_(False)
            )
            .scalar()
            or 0
        )

    if hasattr(Contact, "status"):

        open_enquiry_count = (
            db.session.query(func.count(Contact.id))
            .filter(
                func.lower(Contact.status) == "open"
            )
            .scalar()
            or 0
        )

        resolved_enquiry_count = (
            db.session.query(func.count(Contact.id))
            .filter(
                func.lower(Contact.status) == "resolved"
            )
            .scalar()
            or 0)

        archived_enquiry_count = (
            db.session.query(func.count(Contact.id))
            .filter(
                func.lower(Contact.status) == "archived"
            )
            .scalar()
            or 0)
    # =========================================================================
    # Enquiries / Contacts
    # =========================================================================
    enquiry_count = (
        db.session.query(func.count(Contact.id))
        .scalar()
        or 0)

    unread_enquiry_count = (
        db.session.query(func.count(Contact.id))
        .filter(Contact.is_read.is_(False))
        .scalar()
        or 0)

    # These statuses represent enquiries that are still open.
    open_enquiry_count = (
        db.session.query(func.count(Contact.id))
        .filter(
            Contact.status.in_([
                "New",
                "Assigned",
                "In Progress",
                "Waiting for Customer",
            ]),
            Contact.is_archived.is_(False),
        )
        .scalar()
        or 0
    )

    resolved_enquiry_count = (
        db.session.query(func.count(Contact.id))
        .filter(
            func.lower(Contact.status) == "resolved",
            Contact.is_archived.is_(False),
        ).scalar()or 0)

    archived_enquiry_count = (
        db.session.query(func.count(Contact.id))
        .filter(Contact.is_archived.is_(True)).scalar()or 0)

    # =============================================================================
    # Service Enquiries — Safari, Stay, and Experience
    # =============================================================================
    service_inquiry_models = {
        "safari": SafariInquiry,
        "stay": StayInquiry,
        "experience": ExperienceInquiry,}

    service_inquiry_stats = {
        "total": 0,
        "active": 0,
        "archived": 0,
        "new": 0,
        "safari": 0,
        "stay": 0,
        "experience": 0,
        "safari_active": 0,
        "stay_active": 0,
        "experience_active": 0,
        "safari_archived": 0,
        "stay_archived": 0,
        "experience_archived": 0,
        "safari_new": 0,
        "stay_new": 0,
        "experience_new": 0,}

    for service_type, model in service_inquiry_models.items():
        archived_column = getattr(model, "is_archived", None)
        status_column = getattr(model, "status", None)

        # All submitted enquiries for this service.
        total = db.session.query(
            func.count(model.id)).scalar() or 0

        service_inquiry_stats[service_type] = total
        service_inquiry_stats["total"] += total

        # Archived enquiries.
        if archived_column is not None:
            archived = (
                    db.session.query(func.count(model.id))
                    .filter(archived_column.is_(True))
                    .scalar()or 0)

            active = (
                    db.session.query(func.count(model.id))
                    .filter(archived_column.is_(False))
                    .scalar()or 0
            )
        else:
            # Defensive fallback if a model lacks the archive field.
            archived = 0
            active = total

        service_inquiry_stats[f"{service_type}_archived"] = archived
        service_inquiry_stats[f"{service_type}_active"] = active

        service_inquiry_stats["archived"] += archived
        service_inquiry_stats["active"] += active

        # New enquiries: case-insensitive for Safari's lowercase statuses
        # and Stay/Experience's title-case statuses.
        if status_column is not None:
            new_count = (
                db.session.query(func.count(model.id))
                .filter(func.lower(status_column) == "new"))

            if archived_column is not None:
                new_count = new_count.filter(
                    archived_column.is_(False))

            new_count = new_count.scalar() or 0

            service_inquiry_stats[f"{service_type}_new"] = new_count
            service_inquiry_stats["new"] += new_count

    # =============================================================================
    # Newsletter Statistics
    # =============================================================================

    # Rich newsletter model:
    # newsletter_subscribers
    newsletter_subscriber_stats = {
        "total": 0,
        "subscribed": 0,
        "unsubscribed": 0,
        "verified": 0,
        "unverified": 0,
        "marketing_consent": 0,
        "eligible_for_marketing": 0,
    }

    newsletter_subscriber_stats["total"] = (
            db.session.query(func.count(NewsletterSubscriber.id)).scalar() or 0)

    newsletter_subscriber_stats["subscribed"] = (
            db.session.query(func.count(NewsletterSubscriber.id))
            .filter(NewsletterSubscriber.subscribed.is_(True))
            .scalar()
            or 0)

    newsletter_subscriber_stats["unsubscribed"] = (
            db.session.query(func.count(NewsletterSubscriber.id))
            .filter(NewsletterSubscriber.subscribed.is_(False))
            .scalar()
            or 0)

    newsletter_subscriber_stats["verified"] = (
            db.session.query(func.count(NewsletterSubscriber.id))
            .filter(NewsletterSubscriber.verified.is_(True))
            .scalar()
            or 0)

    newsletter_subscriber_stats["unverified"] = (
            db.session.query(func.count(NewsletterSubscriber.id))
            .filter(NewsletterSubscriber.verified.is_(False))
            .scalar()
            or 0)

    newsletter_subscriber_stats["marketing_consent"] = (
            db.session.query(func.count(NewsletterSubscriber.id))
            .filter(NewsletterSubscriber.marketing_consent.is_(True))
            .scalar()
            or 0)

    newsletter_subscriber_stats["eligible_for_marketing"] = (
            db.session.query(func.count(NewsletterSubscriber.id))
            .filter(
                NewsletterSubscriber.subscribed.is_(True),
                NewsletterSubscriber.verified.is_(True),
                NewsletterSubscriber.marketing_consent.is_(True),
            ).scalar()or 0)

    # Simple newsletter model:
    # newsletters
    newsletter_stats = {"total": (db.session.query(func.count(Newsletter.id)).scalar() or 0), "subscribed": (
            db.session.query(func.count(Newsletter.id))
            .filter(Newsletter.is_subscribed.is_(True))
            .scalar()
            or 0
    ), "unsubscribed": (
            db.session.query(func.count(Newsletter.id))
            .filter(Newsletter.is_subscribed.is_(False))
            .scalar()
            or 0
    ), "verified": (
            db.session.query(func.count(Newsletter.id))
            .filter(Newsletter.is_verified.is_(True))
            .scalar()
            or 0
    ), "unverified": (
            db.session.query(func.count(Newsletter.id))
            .filter(Newsletter.is_verified.is_(False))
            .scalar()
            or 0
    )}

    # =========================================================================
    # Blog / Journal
    # =========================================================================
    blog_post_count = (
        db.session.query(func.count(BlogPost.id))
        .scalar()or 0)

    blog_category_count = (
        db.session.query(func.count(BlogCategory.id)).scalar()or 0)
    draft_blog_count = 0
    review_blog_count = 0
    scheduled_blog_count = 0
    published_blog_count = 0
    archived_blog_count = 0
    featured_blog_count = 0
    pinned_blog_count = 0

    if hasattr(BlogPost, "status"):
        draft_blog_count = (
            db.session.query(func.count(BlogPost.id))
            .filter(
                func.lower(BlogPost.status) == "draft"
            ).scalar()or 0)

        review_blog_count = (
            db.session.query(func.count(BlogPost.id))
            .filter(
                func.lower(BlogPost.status) == "review"
            ).scalar()or 0)

        scheduled_blog_count = (
            db.session.query(func.count(BlogPost.id))
            .filter(
                func.lower(BlogPost.status) == "scheduled"
            )
            .scalar()
            or 0
        )

        published_blog_count = (
            db.session.query(func.count(BlogPost.id))
            .filter(
                func.lower(BlogPost.status) == "published"
            )
            .scalar()
            or 0
        )

        archived_blog_count = (
            db.session.query(func.count(BlogPost.id))
            .filter(
                func.lower(BlogPost.status) == "archived"
            )
            .scalar()
            or 0
        )

    if hasattr(BlogPost, "featured"):

        featured_blog_count = (
            db.session.query(func.count(BlogPost.id))
            .filter(
                BlogPost.featured.is_(True)
            )
            .scalar()
            or 0
        )

    if hasattr(BlogPost, "pinned"):

        pinned_blog_count = (
            db.session.query(func.count(BlogPost.id))
            .filter(
                BlogPost.pinned.is_(True)
            )
            .scalar()
            or 0
        )


    # =========================================================================
    # Testimonials
    # =========================================================================

    testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .scalar()
        or 0
    )

    active_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.active.is_(True)
        )
        .scalar()
        or 0
    )

    inactive_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.active.is_(False)
        )
        .scalar()
        or 0
    )

    featured_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.featured.is_(True)
        )
        .scalar()
        or 0
    )

    homepage_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.homepage.is_(True)
        )
        .scalar()
        or 0
    )

    verified_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.verified.is_(True)
        )
        .scalar()
        or 0
    )

    unverified_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.verified.is_(False)
        )
        .scalar()
        or 0)

    # -------------------------------------------------------------------------
    # Testimonial ratings
    # -------------------------------------------------------------------------
    testimonial_rating_query = (
        db.session.query(
            func.avg(Testimonial.rating)
        )
        .filter(
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        )
        .scalar()
    )

    average_testimonial_rating = (
        round(float(testimonial_rating_query), 1)
        if testimonial_rating_query is not None
        else 0
    )

    five_star_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.rating == 5,
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        )
        .scalar()
        or 0
    )

    four_star_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.rating == 4,
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        )
        .scalar()
        or 0
    )

    three_star_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.rating == 3,
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        )
        .scalar()
        or 0
    )

    two_star_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.rating == 2,
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        )
        .scalar()
        or 0
    )

    one_star_testimonial_count = (
        db.session.query(func.count(Testimonial.id))
        .filter(
            Testimonial.rating == 1,
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        )
        .scalar()
        or 0)

    # =========================================================================
    # Users
    # =========================================================================
    user_count = (
        db.session.query(func.count(User.id))
        .scalar()
        or 0)

    active_user_count = 0
    inactive_user_count = 0
    admin_user_count = 0
    guide_user_count = 0
    staff_user_count = 0

    if hasattr(User, "is_active"):

        active_user_count = (
            db.session.query(func.count(User.id))
            .filter(
                User.is_active.is_(True)
            )
            .scalar()
            or 0
        )

        inactive_user_count = (
            db.session.query(func.count(User.id))
            .filter(
                User.is_active.is_(False)
            )
            .scalar()
            or 0
        )

    if hasattr(User, "role"):

        admin_user_count = (
            db.session.query(func.count(User.id))
            .filter(
                func.lower(User.role) == "admin"
            ).scalar()or 0)

        guide_user_count = (
            db.session.query(func.count(User.id))
            .filter(
                func.lower(User.role) == "guide"
            ).scalar()or 0)

        staff_user_count = (
            db.session.query(func.count(User.id))
            .filter(
                func.lower(User.role) == "staff"
            )
            .scalar()
            or 0)

    # =========================================================================
    # Staff
    # =========================================================================
    staff_count = (
            db.session.query(func.count(Staff.id))
            .scalar()
            or 0)

    active_staff_count = (
            db.session.query(func.count(Staff.id))
            .filter(
                Staff.status == "Active"
            )
            .scalar()
            or 0)

    inactive_staff_count = (
            db.session.query(func.count(Staff.id))
            .filter(
                Staff.status != "Active"
            )
            .scalar()
            or 0)

    # =========================================================================
    # Guides
    # =========================================================================
    guide_count = guide_user_count


    # =========================================================================
    # Recent Content
    # =========================================================================
    recent_testimonials = (
        Testimonial.query
        .order_by(
            Testimonial.created_at.desc()
        )
        .limit(5)
        .all()
    )

    recent_blog_posts = (
        BlogPost.query
        .order_by(
            BlogPost.created_at.desc()
        ).limit(5).all())

    recent_enquiries = (
        Contact.query
        .order_by(
            Contact.created_at.desc()
        ).limit(5).all())

    recent_bookings = (
        Booking.query
        .order_by(
            Booking.created_at.desc()
        ).limit(5).all())

    # =========================================================================
    # Dashboard Summary
    # =========================================================================
    dashboard_stats = {
        "experiences": experience_count,
        "destinations": destination_count,
        "booking": booking_count,
        "enquiries": enquiry_count,
        "blog_posts": blog_post_count,
        "testimonials": testimonial_count,
        "users": user_count,
        "staff": staff_count,
        "guides": guide_count,}

    # =========================================================================
    # Render Dashboard
    # =========================================================================
    return render_template(
        "admin/dashboard.html",

        # ---------------------------------------------------------------------
        # Current user
        # ---------------------------------------------------------------------
        current_user=current_user,

        # ---------------------------------------------------------------------
        # Primary counts
        # ---------------------------------------------------------------------
        experience_count=experience_count,
        destination_count=destination_count,
        booking_count=booking_count,
        enquiry_count=enquiry_count,
        blog_post_count=blog_post_count,
        testimonial_count=testimonial_count,

        # ---------------------------------------------------------------------
        # Experience statistics
        # ---------------------------------------------------------------------
        active_experience_count=active_experience_count,
        inactive_experience_count=inactive_experience_count,
        featured_experience_count=featured_experience_count,

        # ---------------------------------------------------------------------
        # Destination statistics
        # ---------------------------------------------------------------------
        active_destination_count=active_destination_count,
        inactive_destination_count=inactive_destination_count,
        featured_destination_count=featured_destination_count,

        # ---------------------------------------------------------------------
        # Booking statistics
        # ---------------------------------------------------------------------
        pending_booking_count=pending_booking_count,
        confirmed_booking_count=confirmed_booking_count,
        completed_booking_count=completed_booking_count,
        cancelled_booking_count=cancelled_booking_count,

        # ---------------------------------------------------------------------
        # Enquiry statistics
        # ---------------------------------------------------------------------
        unread_enquiry_count=unread_enquiry_count,
        open_enquiry_count=open_enquiry_count,
        resolved_enquiry_count=resolved_enquiry_count,
        archived_enquiry_count=archived_enquiry_count,

        # ---------------------------------------------------------------------
        # Service Enquiry Statistics
        # ---------------------------------------------------------------------
        service_inquiry_stats=service_inquiry_stats,
        service_inquiry_count=service_inquiry_stats["total"],
        active_service_inquiry_count=service_inquiry_stats["active"],
        archived_service_inquiry_count=service_inquiry_stats["archived"],
        new_service_inquiry_count=service_inquiry_stats["new"],
        safari_inquiry_count=service_inquiry_stats["safari"],
        stay_inquiry_count=service_inquiry_stats["stay"],
        experience_inquiry_count=service_inquiry_stats["experience"],

        # Newsletter statistics
        newsletter_subscriber_stats=newsletter_subscriber_stats,
        newsletter_stats=newsletter_stats,

        # Convenient individual values for dashboard cards
        newsletter_subscriber_count=newsletter_subscriber_stats["total"],
        active_newsletter_subscriber_count=newsletter_subscriber_stats["subscribed"],
        verified_newsletter_subscriber_count=newsletter_subscriber_stats["verified"],
        unsubscribed_newsletter_subscriber_count=newsletter_subscriber_stats["unsubscribed"],
        marketing_consent_count=newsletter_subscriber_stats["marketing_consent"],
        eligible_for_marketing_count=newsletter_subscriber_stats["eligible_for_marketing"],

        newsletter_count=newsletter_stats["total"],
        active_newsletter_count=newsletter_stats["subscribed"],
        verified_newsletter_count=newsletter_stats["verified"],
        unsubscribed_newsletter_count=newsletter_stats["unsubscribed"],

        # ---------------------------------------------------------------------
        # Blog statistics
        # ---------------------------------------------------------------------

        blog_category_count=blog_category_count,
        draft_blog_count=draft_blog_count,
        review_blog_count=review_blog_count,
        scheduled_blog_count=scheduled_blog_count,
        published_blog_count=published_blog_count,
        archived_blog_count=archived_blog_count,
        featured_blog_count=featured_blog_count,
        pinned_blog_count=pinned_blog_count,

        # ---------------------------------------------------------------------
        # Testimonial statistics
        # ---------------------------------------------------------------------
        active_testimonial_count=active_testimonial_count,
        inactive_testimonial_count=inactive_testimonial_count,
        featured_testimonial_count=featured_testimonial_count,
        homepage_testimonial_count=homepage_testimonial_count,
        verified_testimonial_count=verified_testimonial_count,
        unverified_testimonial_count=unverified_testimonial_count,
        average_testimonial_rating=average_testimonial_rating,
        five_star_testimonial_count=five_star_testimonial_count,
        four_star_testimonial_count=four_star_testimonial_count,
        three_star_testimonial_count=three_star_testimonial_count,
        two_star_testimonial_count=two_star_testimonial_count,
        one_star_testimonial_count=one_star_testimonial_count,

        # ---------------------------------------------------------------------
        # User statistics
        # ---------------------------------------------------------------------
        user_count=user_count,
        active_user_count=active_user_count,
        inactive_user_count=inactive_user_count,
        admin_user_count=admin_user_count,
        guide_user_count=guide_user_count,
        staff_user_count=staff_user_count,

        # ---------------------------------------------------------------------
        # Staff statistics
        # ---------------------------------------------------------------------
        staff_count=staff_count,
        active_staff_count=active_staff_count,
        inactive_staff_count=inactive_staff_count,
        guide_count=guide_count,

        # ---------------------------------------------------------------------
        # Recent records
        # ---------------------------------------------------------------------
        recent_testimonials=recent_testimonials,
        recent_blog_posts=recent_blog_posts,
        recent_enquiries=recent_enquiries,
        recent_bookings=recent_bookings,

        # ---------------------------------------------------------------------
        # Combined dashboard object
        # ---------------------------------------------------------------------
        dashboard_stats=dashboard_stats,
    )

# =============================================================================
# Logout
# =============================================================================
@admin_bp.route("/logout")
@login_required
def logout():
    """
    Log the current administrator out of the platform.
    """

    logout_user()

    flash(
        "You have been signed out.",
        "success",
    )

    return redirect(
        url_for(
            "admin.login"
        )
    )

# =============================================================================
# ADMINISTRATOR PROFILE
# =============================================================================
@admin_bp.route("/profile", methods=["GET", "POST"])
@admin_required
def profile():
    """
    Manage the currently authenticated administrator's profile.

    Supports:
        - Personal information
        - Username
        - Email
        - Phone
        - Bio
        - Password change
    """

    profile_form = AdminProfileForm(obj=current_user)
    password_form = AdminPasswordForm()

    # -------------------------------------------------------------------------
    # PROFILE UPDATE
    # -------------------------------------------------------------------------
    if request.method == "POST" and "save_profile" in request.form:
        profile_form = AdminProfileForm(obj=current_user)
        password_form = AdminPasswordForm()

        if profile_form.validate_on_submit():
            current_user.first_name = profile_form.first_name.data.strip()
            current_user.last_name = profile_form.last_name.data.strip()
            current_user.username = profile_form.username.data.strip()
            current_user.email = profile_form.email.data.strip().lower()

            if profile_form.phone.data:
                current_user.phone = profile_form.phone.data.strip()
            else:
                current_user.phone = None

            current_user.bio = profile_form.bio.data.strip() if profile_form.bio.data else None

            db.session.commit()

            flash("Your profile has been updated successfully.", "success")

            return redirect(url_for("admin.profile"))

    # -------------------------------------------------------------------------
    # PASSWORD UPDATE
    # -------------------------------------------------------------------------
    if request.method == "POST" and "change_password" in request.form:
        profile_form = AdminProfileForm(obj=current_user)
        password_form = AdminPasswordForm()

        if password_form.validate_on_submit():
            current_user.set_password(password_form.new_password.data)

            db.session.commit()

            flash("Your password has been changed successfully.", "success")

            return redirect(url_for("admin.profile"))

    return render_template(
        "admin/profile.html",
        profile_form=profile_form,
        password_form=password_form,
    )

# =============================================================================
# ACCESS CONTROL
# =============================================================================
@admin_bp.route("/access-control", methods=["GET"])
@admin_required
def access_control():
    """
    Administrator access-control dashboard.

    Allows administrators to:
        - Search users
        - Filter by role
        - Filter by active/inactive status
        - Filter by verification status
        - Manage individual users
    """

    filter_form = AccessControlFilterForm(request.args, meta={"csrf": False})

    query = User.query

    # -------------------------------------------------------------------------
    # SEARCH
    # -------------------------------------------------------------------------
    search = request.args.get("search", "").strip()

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern),
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
            )
        )

    # -------------------------------------------------------------------------
    # ROLE FILTER
    # -------------------------------------------------------------------------
    role = request.args.get("role", "").strip()

    if role:
        query = query.filter(User.role == role)

    # -------------------------------------------------------------------------
    # ACTIVE STATUS FILTER
    # -------------------------------------------------------------------------
    active = request.args.get("active", "").strip()

    if active == "active":
        query = query.filter(User.is_active.is_(True))

    elif active == "inactive":
        query = query.filter(User.is_active.is_(False))

    # -------------------------------------------------------------------------
    # VERIFICATION FILTER
    # -------------------------------------------------------------------------
    verified = request.args.get("verified", "").strip()

    if verified == "verified":
        query = query.filter(User.is_verified.is_(True))

    elif verified == "unverified":
        query = query.filter(User.is_verified.is_(False))

    # -------------------------------------------------------------------------
    # ORDERING
    # -------------------------------------------------------------------------
    query = query.order_by(
        User.first_name.asc(),
        User.last_name.asc(),
    )

    users = query.all()

    return render_template(
        "admin/access_control.html",
        users=users,
        filter_form=filter_form,
    )

# =============================================================================
# Admin Error Pages
# =============================================================================
@admin_bp.app_errorhandler(403)
def forbidden(error):
    """
    Administrative forbidden response.
    """
    return render_template("admin/errors/403.html"), 403

@admin_bp.app_errorhandler(404)
def not_found(error):
    """
    Administrative not-found response.
    """
    return render_template("admin/errors/404.html"), 404

@admin_bp.app_errorhandler(500)
def server_error(error):
    """
    Administrative server-error response.
    """
    return render_template("admin/errors/500.html"), 500

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "admin_bp",
]
