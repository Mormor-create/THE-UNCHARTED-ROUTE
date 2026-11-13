"""Secure invitation workflow for The Uncharted Route guides."""
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired
from flask import current_app
from sqlalchemy import or_
from extensions import db
from app.models import User, Staff

GUIDE_INVITATION_SALT = "tur-guide-invitation-v1"
DEFAULT_INVITATION_MAX_AGE = 60 * 60 * 24 * 2  # 48 hours

class GuideInvitationError(ValueError):
    """Raised when a guide invitation cannot be processed."""

def _serializer():
    secret = current_app.config.get("SECRET_KEY")
    if not secret:
        raise RuntimeError("Flask SECRET_KEY is not configured.")
    return URLSafeTimedSerializer(secret)

def generate_guide_invitation_token(user):
    """Generate a time-stamped, signed invitation token."""
    if user is None or not user.id:
        raise GuideInvitationError("A saved user account is required.")

    return _serializer().dumps(
        {"user_id": user.id},
        salt=GUIDE_INVITATION_SALT,)

def verify_guide_invitation_token(token):
    """Return the eligible pending guide, or None if invalid or expired."""
    if not token:
        return None

    max_age = current_app.config.get(
        "GUIDE_INVITATION_MAX_AGE",
        DEFAULT_INVITATION_MAX_AGE,)

    try:
        payload = _serializer().loads(
            token,
            salt=GUIDE_INVITATION_SALT,
            max_age=max_age,
        )
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return None

    if not isinstance(payload, dict):
        return None

    user_id = payload.get("user_id")
    if not isinstance(user_id, int):
        return None

    user = db.session.get(User, user_id)

    if (
        user is None
        or user.normalized_role != "guide"
        or user.is_active
        or user.is_verified
    ):
        return None

    if user.staff_profile is None:
        return None

    if user.staff_profile.staff_type != "Guide":
        return None

    return user

def create_pending_guide(
    *,
    first_name,
    last_name,
    email,
    phone=None,
    employee_number=None,
    department="Guiding",
    job_title="Guide",
    employment_type="Freelance",
):
    """Create an inactive guide account and inactive Staff profile.

    This function commits the pending account before email delivery so that
    a failed email can be retried using the resend invitation route.
    """
    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    email = (email or "").strip().lower()
    phone = (phone or "").strip() or None
    employee_number = (employee_number or "").strip() or None

    if not first_name or not last_name or not email:
        raise GuideInvitationError(
            "First name, last name, and email are required."
        )

    duplicate = User.query.filter(
        or_(
            User.email.ilike(email),
        )
    ).first()

    if duplicate:
        raise GuideInvitationError(
            "An account already exists with that email address."
        )

    if employee_number and Staff.query.filter(
        Staff.employee_number.ilike(employee_number)
    ).first():
        raise GuideInvitationError(
            "That employee number is already in use."
        )

    # User.username is required and unique. Start with the email prefix,
    # then add a numeric suffix if another user already uses it.
    base_username = email.split("@", 1)[0].strip().lower()
    base_username = "".join(
        char for char in base_username
        if char.isalnum() or char in "._-"
    )[:70] or "guide"

    username = base_username
    suffix = 1

    while User.query.filter(
        User.username.ilike(username)
    ).first():
        suffix_text = str(suffix)
        username = f"{base_username[:80 - len(suffix_text)]}{suffix_text}"
        suffix += 1

    # password_hash is non-nullable. Store a random, unshared password
    # hash until the guide chooses their own password.
    import secrets

    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        phone=phone,
        role="guide",
        is_active=False,
        is_verified=False,
    )
    user.set_password(secrets.token_urlsafe(48))

    try:
        db.session.add(user)
        db.session.flush()

        staff = Staff(
            user_id=user.id,
            employee_number=employee_number,
            staff_type="Guide",
            department=(department or "").strip() or "Guiding",
            job_title=(job_title or "").strip() or "Guide",
            employment_type=employment_type or "Freelance",
            status="Inactive",
        )
        db.session.add(staff)
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise

def accept_guide_invitation(token, password):
    """Set the guide's password and activate the account exactly once."""
    user = verify_guide_invitation_token(token)

    if user is None:
        raise GuideInvitationError(
            "This invitation is invalid, expired, or has already been used. "
            "Please request a new invitation from the administrator."
        )

    if not password or len(password) < 12:
        raise GuideInvitationError(
            "Choose a password with at least 12 characters."
        )

    staff = user.staff_profile
    if staff is None or staff.staff_type != "Guide":
        raise GuideInvitationError(
            "The guide profile could not be found. Contact an administrator."
        )
    try:
        user.set_password(password)
        user.is_verified = True
        user.is_active = True
        user.updated_at = datetime.utcnow()
        staff.status = "Active"
        staff.updated_at = datetime.utcnow()
        db.session.commit()
        return user
    except Exception:
        db.session.rollback()
        raise