"""
===============================================================================
The Uncharted Route
User Model
===============================================================================
Represents authenticated users of the platform.
Supported roles:
- Customer
- Guide
- Staff
- Administrator
Integrated with Flask-Login.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,)
from extensions import db
# =============================================================================
# User Model
# =============================================================================
class User(UserMixin, db.Model):
    """
    Application user.
    """
    __tablename__ = "users"
    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True,)

    # =========================================================================
    # Account Information
    # =========================================================================
    first_name = db.Column(db.String(100),nullable=False,)
    last_name = db.Column(db.String(100),nullable=False,)
    username = db.Column(db.String(80),unique=True,nullable=False,index=True,)
    email = db.Column(db.String(255),unique=True,nullable=False,index=True,)
    password_hash = db.Column(db.String(255),nullable=False,)

    # =========================================================================
    # Profile
    # =========================================================================
    phone = db.Column(db.String(30),)
    profile_image = db.Column(db.String(255),default="default-avatar.png",)
    bio = db.Column(db.Text,)
    # =========================================================================
    # Role & Account Status
    # =========================================================================
    role = db.Column(db.String(30),default="customer",nullable=False,)
    is_active = db.Column(db.Boolean, default=True,nullable=False,)
    is_verified = db.Column(db.Boolean,default=False,nullable=False,)
    # =========================================================================
    # Audit Fields
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False,)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False,)
    last_login = db.Column(db.DateTime,)
    # =========================================================================
    # Staff Profile
    # =========================================================================
    staff_profile = db.relationship("Staff",back_populates="user",uselist=False,)
    # =========================================================================
    # Password Helpers
    # =========================================================================
    def set_password(self, password: str) -> None:
        """
        Hash and store a password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Verify a password.
        """
        return check_password_hash(self.password_hash,password,)

    # =========================================================================
    # General Properties
    # =========================================================================

    @property
    def full_name(self) -> str:
        """
        Return the user's full name.
        """

        return (
            f"{self.first_name} "
            f"{self.last_name}"
        )

    @property
    def normalized_role(self) -> str:
        """
        Return the user's normalized role.
        """

        return (
            self.role.strip().lower()
            if self.role
            else ""
        )
    # =========================================================================
    # Role Properties
    # =========================================================================
    @property
    def is_customer(self) -> bool:
        """
        Determine whether the user is a customer.
        """
        return self.normalized_role == "customer"

    @property
    def is_guide(self) -> bool:
        """
        Determine whether the user is a guide.
        """
        return self.normalized_role == "guide"

    @property
    def is_admin(self) -> bool:
        """
        Determine whether the user is an administrator.
        """
        return self.normalized_role == "admin"

    @property
    def is_staff(self) -> bool:
        """
        Determine whether the user has staff-level access.

        Administrators are included.
        """
        return self.normalized_role in {
            "admin",
            "staff",}

    @property
    def is_internal_user(self) -> bool:
        """
        Determine whether the user is an internal platform user.
        """
        return self.normalized_role in {
            "admin",
            "staff",
            "guide",}
    # =========================================================================
    # Permission Helpers
    # =========================================================================

    def has_permission(self, permission: str) -> bool:
        """
        Determine whether this user has a specific permission.
        """
        from app.services.permission_service import has_permission
        return has_permission(self,permission,)

    def has_any_permission(self, *permissions) -> bool:
        """
        Determine whether this user has at least one supplied permission.
        """
        from app.services.permission_service import has_any_permission
        return has_any_permission(self,*permissions,)

    def has_all_permissions(self, *permissions) -> bool:
        """
        Determine whether this user has all supplied permissions.
        """
        from app.services.permission_service import has_all_permissions
        return has_all_permissions(self,*permissions,)

    def get_permissions(self):
        """
        Return all permissions granted to this user.
        """
        from app.services.permission_service import get_user_permissions
        return get_user_permissions(self)

    # =========================================================================
    # String Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<User "
            f"{self.username}>"
        )