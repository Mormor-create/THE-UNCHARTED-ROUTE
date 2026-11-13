"""
===============================================================================
The Uncharted Route
Authentication Routes
===============================================================================
Handles:
• Login
• Registration
• Logout
• Forgot password
• Password reset
HTTP/request handling lives here.
Authentication business logic lives in:
    app.services.auth_service
"""
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,)
from app.forms.auth import (
    ForgotPasswordForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,)
from app.models import User
from app.services import guide_service
from app.services.auth_service import (
    authenticate_user,
    create_user,
    generate_password_reset_token,
    record_login,
    reset_password,
    verify_password_reset_token,)
from extensions import db
import logging
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

# =============================================================================
# Blueprint
# =============================================================================
auth_bp = Blueprint("auth",__name__,url_prefix="/auth",)
# =============================================================================
# Safe Redirect Helpers
# =============================================================================
def is_safe_url(target):
    """
    Determine whether a redirect target belongs to this application.
    """
    if not target:
        return False
    from urllib.parse import urljoin, urlparse
    host_url = urlparse(request.host_url)

    redirect_url = urlparse(
        urljoin(request.host_url,target,))

    return (
        redirect_url.scheme in {
            "http",
            "https",}
        and redirect_url.netloc == host_url.netloc)

def get_safe_redirect_target():
    """
    Return a safe post-login redirect target.
    Returns None when no safe redirect target was supplied.
    """
    target = request.args.get("next")
    if target and is_safe_url(target):
        return target
    return None

def get_role_redirect(user):
    """Choose the correct destination for the user's existing role."""
    role = getattr(user, "normalized_role", None) or ""

    if role == "admin":
        return url_for("admin.dashboard")

    if role == "guide":
        guide = guide_service.get_guide_by_user(user)

        if (
            guide is not None
            and guide.user_id == user.id
            and guide.staff_type == "Guide"
            and guide.status == "Active"
        ):
            return url_for("guide_portal.dashboard")

        flash(
            "Your guide account is active, but its guide profile "
            "is missing or inactive. Please contact an administrator.",
            "error",
        )
        return url_for("main.home")

    # Customers and other roles default to the public website.
    return url_for("main.home")

def get_post_login_redirect(user):
    """
    Redirect authenticated users to the correct portal for their role.
    """

    role = getattr(user, "normalized_role", None) or ""

    if role == "admin":
        return url_for("admin.dashboard")

    if role == "guide":
        guide = guide_service.get_guide_by_user(user)

        if (
            guide is not None
            and guide.user_id == user.id
            and guide.staff_type == "Guide"
            and guide.status == "Active"
        ):
            return url_for("guide_portal.dashboard")
        flash(
            "Your guide account does not have a valid active guide profile. "
            "Please contact an administrator.",
            "error",
        )
        return url_for("main.home")
    return url_for("main.home")

# =============================================================================
# Login
# =============================================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(get_post_login_redirect(current_user))

    form = LoginForm()

    if form.validate_on_submit():
        identity = form.identity.data.strip()

        user = authenticate_user(
            identity=identity,
            password=form.password.data,
        )

        if user is None:
            flash("Invalid username/email or password.", "error")
            return render_template("auth/login.html", form=form), 401

        if not user.is_active:
            flash(
                "Your account is inactive. Please contact an administrator.",
                "error",
            )
            return render_template("auth/login.html", form=form), 403

        login_user(user, remember=False)
        record_login(user)

        # Admins and guides go to their own portals.
        # Customers retain support for safe "next" redirects.
        role = getattr(user, "normalized_role", None) or ""

        if role not in {"admin", "guide"}:
            target = get_safe_redirect_target()

            if target:
                return redirect(target)

        return redirect(get_post_login_redirect(user))

    return render_template("auth/login.html", form=form)
# =============================================================================
# Registration
# =============================================================================
@auth_bp.route("/register",methods=["GET", "POST"],)
def register():
    """
    Register a new standard customer account.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        # -----------------------------------------------------------------
        # Username uniqueness
        # -----------------------------------------------------------------
        existing_username = User.query.filter(User.username.ilike(username)).first()
        if existing_username:
            form.username.errors.append("That username is already in use.")
            return render_template("auth/register.html",form=form,)

        # -----------------------------------------------------------------
        # Email uniqueness
        # -----------------------------------------------------------------
        existing_email = User.query.filter(User.email.ilike(email)).first()
        if existing_email:
            form.email.errors.append("That email address is already registered.")
            return render_template("auth/register.html",form=form,)

        # -----------------------------------------------------------------
        # Create account through service layer
        # -----------------------------------------------------------------
        user = create_user(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=username,
            email=email,
            password=form.password.data,)
        login_user(user,remember=False,)

        flash("Your account has been created successfully.","success",)
        return redirect(url_for("main.home"))
    return render_template("auth/register.html",form=form,)

# =============================================================================
# Logout
# =============================================================================
@auth_bp.route("/logout",methods=["POST"],)
@login_required
def logout():
    """
    Log the current user out.
    """
    logout_user()
    flash("You have been signed out successfully.","success",)
    return redirect(
        url_for("main.home"))

# =============================================================================
# Forgot Password
# =============================================================================
@auth_bp.route("/forgot-password",methods=["GET", "POST"],)
def forgot_password():
    """
    Request a password reset.
    The response intentionally does not reveal whether
    an email exists in the database.
    Email delivery is temporarily represented by
    printing the reset URL during development.
    """
    if current_user.is_authenticated:
        return redirect(
            url_for("main.home"))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter(User.email.ilike(email)).first()
        if user and user.is_active:
            token = generate_password_reset_token(user)

            reset_url = url_for(
                "auth.reset_password_route",
                token=token,
                _external=True,
            )

            email_service = EmailService()

            email_sent = email_service.send_password_reset_email(
                user=user,
                reset_url=reset_url,
            )

            if not email_sent:
                logger.error(
                    "Password reset email delivery failed for user ID %s.",
                    user.id,
                )
        flash(
            "If an account exists for that email address, "
            "a password reset link has been sent.",
            "info",)
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/forgot_password.html",form=form,)

# =============================================================================
# Reset Password
# =============================================================================
@auth_bp.route("/reset-password/<token>",methods=["GET", "POST"],)
def reset_password_route(token):
    """
    Reset a user's password using a signed token.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = verify_password_reset_token(token)
    if user is None or not user.is_active:
        flash("That password reset link is invalid or has expired.","error",)
        return redirect(url_for("auth.forgot_password"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        reset_password(
            user=user,password=form.password.data,)

        flash("Your password has been reset successfully. ""You can now sign in.","success",)
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html",form=form,)