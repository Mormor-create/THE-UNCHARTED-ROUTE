"""
===============================================================================
The Uncharted Route
Administrator User Management Routes
===============================================================================
Administrator-only management of application users.
Routes
------
/admin/users/
/admin/users/<user_id>

Administrators can:
• View users
• Search and filter users
• Edit user profiles
• Change roles
• Activate / deactivate accounts
• Verify / unverify accounts
• Reset user passwords

Authentication and authorization are handled through admin_required.
===============================================================================
"""
from flask import (
    Blueprint,
    render_template,
    redirect,url_for,
    flash,request,)
from flask_login import current_user
from app.decorators.admin import admin_required
from app.forms.admin_user import (
    AdminUserProfileForm,
    AdminUserRoleForm,
    AdminUserStatusForm,
    AdminUserVerificationForm,
    AdminUserPasswordForm,)
from app.services import user_service
from app.forms.guide_invitation_forms import GuideInvitationForm
from app.services.guide_invitation_service import (
    GuideInvitationError,
    create_pending_guide,
    generate_guide_invitation_token,
)
from flask import current_app
from app.services import email_service
from extensions import db

# =============================================================================
# Blueprint
# =============================================================================
admin_user_bp = Blueprint(
    "admin_user",
    __name__,
    url_prefix="/admin/users",)

# =============================================================================
# Users Index
# =============================================================================
@admin_user_bp.route("/")
@admin_required
def index():
    """
    Display the administrator user-management page.
    """

    search = request.args.get(
        "search",
        "",
        type=str,
    ).strip()

    role = request.args.get(
        "role",
        "",
        type=str,
    ).strip().lower()

    active_value = request.args.get(
        "active",
        "",
        type=str,
    ).strip().lower()

    verified_value = request.args.get(
        "verified",
        "",
        type=str,
    ).strip().lower()

    # -------------------------------------------------------------------------
    # Convert filter values
    # -------------------------------------------------------------------------
    active = None
    if active_value == "active":
        active = True
    elif active_value == "inactive":
        active = False
    verified = None
    if verified_value == "verified":
        verified = True
    elif verified_value == "unverified":
        verified = False

    # -------------------------------------------------------------------------
    # Retrieve users
    # -------------------------------------------------------------------------
    users = user_service.get_users(
        search=search or None,
        role=role or None,
        active=active,
        verified=verified,)
    statistics = user_service.get_user_statistics()
    return render_template(
        "admin/users/users.html",
        users=users,
        statistics=statistics,
        search=search,
        role=role,
        active=active_value,
        verified=verified_value,)

# =============================================================================
# User Detail / Management
# =============================================================================
@admin_user_bp.route("/<int:user_id>", methods=["GET", "POST"])
@admin_required
def user_detail(user_id):
    """
    Display and manage an individual user.
    """
    user = user_service.get_user_by_id(user_id)
    if not user:
        flash("The requested user could not be found.","danger",)
        return redirect(url_for("admin_user.index"))

    # =========================================================================
    # Forms
    # =========================================================================
    profile_form = AdminUserProfileForm(obj=user)
    role_form = AdminUserRoleForm(prefix="role",obj=user,)
    status_form = AdminUserStatusForm(prefix="status",)
    verification_form = AdminUserVerificationForm(prefix="verification",)
    password_form = AdminUserPasswordForm(prefix="password",)

    # Set checkbox values manually.
    status_form.is_active.data = user.is_active
    verification_form.is_verified.data = user.is_verified

    # =========================================================================
    # Profile Update
    # =========================================================================
    if (
        request.method == "POST"
        and "save_profile" in request.form):
        profile_form = AdminUserProfileForm(obj=user)
        if profile_form.validate_on_submit():
            try:
                user_service.update_user(
                    user=user,
                    first_name=profile_form.first_name.data,
                    last_name=profile_form.last_name.data,
                    username=profile_form.username.data,
                    email=profile_form.email.data,
                    phone=profile_form.phone.data,
                    bio=profile_form.bio.data,)

                flash("User profile updated successfully.","success",)
                return redirect(
                    url_for(
                        "admin_user.user_detail",
                        user_id=user.id,))

            except ValueError as exc:
                flash(str(exc),"danger",)

    # =========================================================================
    # Role Update
    # =========================================================================

    elif (
        request.method == "POST" and "update_role" in request.form):
        role_form = AdminUserRoleForm(prefix="role")
        if role_form.validate_on_submit():
            new_role = role_form.role.data
            # Prevent an administrator from removing their own
            # administrator privileges.
            if (
                user.id == current_user.id
                and new_role != "admin"):
                flash(
                    "You cannot remove your own administrator role.",
                    "danger",)

            else:
                try:
                    user_service.set_user_role(user,new_role,)
                    flash("User role updated successfully.","success",)
                    return redirect(
                        url_for("admin_user.user_detail",user_id=user.id,))
                except ValueError as exc:
                    flash(str(exc),"danger",)

    # =========================================================================
    # Account Status Update
    # =========================================================================
    elif request.method == "POST"and "update_status" in request.form:
        status_form = AdminUserStatusForm(prefix="status")
        if status_form.validate_on_submit():
            new_status = bool(status_form.is_active.data)
            # Prevent an administrator from deactivating
            # their own account.
            if user.id == current_user.id and not new_status:
                flash("You cannot deactivate your own administrator account.","danger",)

            else:
                try:
                    if new_status:
                        user_service.activate_user(user)
                    else:
                        user_service.deactivate_user(user)
                    flash("User account status updated successfully.","success",)
                    return redirect(
                        url_for("admin_user.user_detail",user_id=user.id,))
                except ValueError as exc:
                    flash(str(exc),"danger",)
    # =========================================================================
    # Verification Update
    # =========================================================================
    elif (
        request.method == "POST"
        and "update_verification" in request.form):
        verification_form = AdminUserVerificationForm(prefix="verification")
        if verification_form.validate_on_submit():
            try:
                if verification_form.is_verified.data:
                    user_service.verify_user(user)
                else:
                    user_service.unverify_user(user)
                flash(
                    "User verification status updated successfully.","success",)
                return redirect(
                    url_for("admin_user.user_detail",user_id=user.id,))
            except ValueError as exc:
                flash(str(exc),"danger",)
    # =========================================================================
    # Password Reset
    # =========================================================================
    elif request.method == "POST"and "reset_password" in request.form:
        password_form = AdminUserPasswordForm(prefix="password")
        if password_form.validate_on_submit():
            try:
                user_service.set_user_password(user,password_form.new_password.data,)
                flash("User password reset successfully.","success",)
                return redirect(
                    url_for(
                        "admin_user.user_detail",
                        user_id=user.id,))
            except ValueError as exc:
                flash(str(exc),"danger",)

    # =========================================================================
    # Render
    # =========================================================================
    return render_template(
        "admin/users/user_detail.html",
        user=user,
        profile_form=profile_form,
        role_form=role_form,
        status_form=status_form,
        verification_form=verification_form,
        password_form=password_form,)

# =============================================================================
# Create Guide Account
# =============================================================================
@admin_user_bp.route("/create-guide", methods=["GET", "POST"])
@admin_required
def create_guide():
    """Create a guide account and email its activation invitation."""

    form = GuideInvitationForm()

    if form.validate_on_submit():
        try:
            # Create the pending User account and linked Staff profile.
            user = create_pending_guide(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                employee_number=form.employee_number.data,
                department=form.department.data,
                job_title=form.job_title.data,
                employment_type=form.employment_type.data,
            )

            # Generate the secure invitation link.
            token = generate_guide_invitation_token(user)

            invitation_url = url_for(
                "admin_guide.accept_guide_invitation",
                token=token,
                _external=True,
            )

            # Send the invitation. Never send a password.
            try:
                email_sent = email_service.send_guide_invitation_email(
                    user,
                    invitation_url,
                )
            except Exception:
                current_app.logger.exception(
                    "Guide invitation email failed for user_id=%s",
                    user.id,
                )
                email_sent = False

            if email_sent:
                flash(
                    f"Guide account created and invitation sent to "
                    f"{user.email}. The guide must accept the invitation "
                    f"before signing in.",
                    "success",
                )
            else:
                flash(
                    f"The guide account for {user.email} was created, "
                    "but the invitation email could not be sent. "
                    "You can resend the invitation from the guide catalogue.",
                    "warning",
                )

            return redirect(url_for("admin_user.index"))

        except GuideInvitationError as exc:
            db.session.rollback()
            flash(str(exc), "danger")

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to create guide account."
            )
            flash(
                "The guide account could not be created. Please try again.",
                "danger",
            )

    return render_template(
        "admin/users/create_guide.html",
        form=form,
    )
