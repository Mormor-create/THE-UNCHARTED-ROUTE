"""
===============================================================================
The Uncharted Route
Cancellation Policy Service
===============================================================================

Business logic for reusable cancellation and refund policies.

Handles:

• Creating cancellation policies
• Retrieving policies
• Updating policies
• Activating/deactivating policies
• Managing the default policy
• Calculating refund eligibility
• Listing policies
• Policy statistics
• Deleting policies
"""

from extensions import db
from app.models import CancellationPolicy


# =============================================================================
# Cancellation Policy Service
# =============================================================================

class CancellationPolicyService:
    """
    Service layer for managing cancellation and refund policies.
    """

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_policy(
        name,
        full_policy,
        slug=None,
        short_description=None,
        full_refund_days=30,
        partial_refund_days=14,
        partial_refund_percentage=50,
        no_refund_days=7,
        date_changes_allowed=True,
        name_changes_allowed=True,
        transferable_booking=False,
        notes=None,
        active=True,
        default_policy=False
    ):
        """
        Create and persist a new cancellation policy.
        """

        if default_policy:
            CancellationPolicyService.clear_default_policy()

        policy = CancellationPolicy(
            name=name,
            slug=slug,
            short_description=short_description,
            full_policy=full_policy,
            full_refund_days=full_refund_days,
            partial_refund_days=partial_refund_days,
            partial_refund_percentage=partial_refund_percentage,
            no_refund_days=no_refund_days,
            date_changes_allowed=date_changes_allowed,
            name_changes_allowed=name_changes_allowed,
            transferable_booking=transferable_booking,
            notes=notes,
            active=active,
            default_policy=default_policy
        )

        db.session.add(policy)
        db.session.commit()

        return policy

    # =========================================================================
    # Retrieve
    # =========================================================================

    @staticmethod
    def get_by_id(policy_id):
        """
        Return a cancellation policy by ID.
        """

        return db.session.get(
            CancellationPolicy,
            policy_id
        )

    # =========================================================================
    # Retrieve by Name
    # =========================================================================

    @staticmethod
    def get_by_name(name):
        """
        Return a cancellation policy by name.
        """

        return (
            CancellationPolicy.query
            .filter(
                CancellationPolicy.name == name
            )
            .first()
        )

    # =========================================================================
    # Retrieve by Slug
    # =========================================================================

    @staticmethod
    def get_by_slug(slug):
        """
        Return a cancellation policy by slug.
        """

        return (
            CancellationPolicy.query
            .filter(
                CancellationPolicy.slug == slug
            )
            .first()
        )

    # =========================================================================
    # Get All
    # =========================================================================

    @staticmethod
    def get_all(
        active_only=False,
        include_default_first=True
    ):
        """
        Return cancellation policies.
        """

        query = CancellationPolicy.query

        if active_only:
            query = query.filter(
                CancellationPolicy.active.is_(True)
            )

        if include_default_first:
            return (
                query
                .order_by(
                    CancellationPolicy.default_policy.desc(),
                    CancellationPolicy.name.asc()
                )
                .all()
            )

        return (
            query
            .order_by(
                CancellationPolicy.name.asc()
            )
            .all()
        )

    # =========================================================================
    # Get Active Policies
    # =========================================================================

    @staticmethod
    def get_active():
        """
        Return all active cancellation policies.
        """

        return (
            CancellationPolicy.query
            .filter(
                CancellationPolicy.active.is_(True)
            )
            .order_by(
                CancellationPolicy.default_policy.desc(),
                CancellationPolicy.name.asc()
            )
            .all()
        )

    # =========================================================================
    # Default Policy
    # =========================================================================

    @staticmethod
    def get_default():
        """
        Return the current default cancellation policy.
        """

        return (
            CancellationPolicy.query
            .filter(
                CancellationPolicy.default_policy.is_(True),
                CancellationPolicy.active.is_(True)
            )
            .first()
        )

    # =========================================================================
    # Clear Default
    # =========================================================================

    @staticmethod
    def clear_default_policy():
        """
        Remove the default flag from all policies.

        Used before assigning a new default policy.
        """

        (
            CancellationPolicy.query
            .filter(
                CancellationPolicy.default_policy.is_(True)
            )
            .update(
                {
                    CancellationPolicy.default_policy: False
                },
                synchronize_session=False
            )
        )

        db.session.flush()

    # =========================================================================
    # Set Default
    # =========================================================================

    @staticmethod
    def set_default(policy_id):
        """
        Make a policy the default policy.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return None

        if not policy.active:
            raise ValueError(
                "An inactive policy cannot be the default policy."
            )

        CancellationPolicyService.clear_default_policy()

        policy.default_policy = True

        db.session.commit()

        return policy

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_policy(policy_id, **updates):
        """
        Update editable cancellation policy fields.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return None

        allowed_fields = {
            "name",
            "slug",
            "short_description",
            "full_policy",
            "full_refund_days",
            "partial_refund_days",
            "partial_refund_percentage",
            "no_refund_days",
            "date_changes_allowed",
            "name_changes_allowed",
            "transferable_booking",
            "notes",
            "active"
        }

        for field, value in updates.items():

            if field in allowed_fields:
                setattr(policy, field, value)

        db.session.commit()

        return policy

    # =========================================================================
    # Activate
    # =========================================================================

    @staticmethod
    def activate(policy_id):
        """
        Activate a cancellation policy.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return None

        policy.active = True

        db.session.commit()

        return policy

    # =========================================================================
    # Deactivate
    # =========================================================================

    @staticmethod
    def deactivate(policy_id):
        """
        Deactivate a cancellation policy.

        A default policy cannot remain default after being
        deactivated.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return None

        policy.active = False

        if policy.default_policy:
            policy.default_policy = False

        db.session.commit()

        return policy

    # =========================================================================
    # Refund Calculation
    # =========================================================================

    @staticmethod
    def calculate_refund_percentage(
        policy_id,
        days_before_trip
    ):
        """
        Determine the refund percentage based on the policy
        and the number of days before the trip.

        Returns:

        100 - Full refund
        partial_refund_percentage - Partial refund
        0 - No refund
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return None

        if days_before_trip >= policy.full_refund_days:
            return 100

        if days_before_trip >= policy.partial_refund_days:
            return policy.partial_refund_percentage

        if days_before_trip <= policy.no_refund_days:
            return 0

        return 0

    # =========================================================================
    # Refund Information
    # =========================================================================

    @staticmethod
    def get_refund_information(
        policy_id,
        days_before_trip
    ):
        """
        Return detailed refund information for a cancellation.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return None

        refund_percentage = (
            CancellationPolicyService.calculate_refund_percentage(
                policy_id,
                days_before_trip
            )
        )

        if refund_percentage == 100:
            refund_type = "Full Refund"

        elif refund_percentage > 0:
            refund_type = "Partial Refund"

        else:
            refund_type = "No Refund"

        return {
            "policy": policy,
            "days_before_trip": days_before_trip,
            "refund_percentage": refund_percentage,
            "refund_type": refund_type,
            "date_changes_allowed": policy.date_changes_allowed,
            "name_changes_allowed": policy.name_changes_allowed,
            "transferable_booking": policy.transferable_booking
        }

    # =========================================================================
    # Booking Changes
    # =========================================================================

    @staticmethod
    def can_change_date(policy_id):
        """
        Determine whether booking date changes are allowed.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return False

        return policy.date_changes_allowed

    @staticmethod
    def can_change_name(policy_id):
        """
        Determine whether guest name changes are allowed.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return False

        return policy.name_changes_allowed

    @staticmethod
    def can_transfer_booking(policy_id):
        """
        Determine whether a booking can be transferred.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return False

        return policy.transferable_booking

    # =========================================================================
    # Experience Count
    # =========================================================================

    @staticmethod
    def get_experience_count(policy_id):
        """
        Return the number of experiences using this policy.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return 0

        return policy.experience_count

    # =========================================================================
    # Stay Count
    # =========================================================================

    @staticmethod
    def get_stay_count(policy_id):
        """
        Return the number of stays using this policy.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return 0

        return policy.stay_count

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete(policy_id):
        """
        Delete a cancellation policy.

        Policies currently attached to experiences or stays
        cannot be deleted.
        """

        policy = CancellationPolicyService.get_by_id(policy_id)

        if not policy:
            return False

        if policy.experience_count > 0:
            raise ValueError(
                "Cannot delete a cancellation policy that is "
                "currently assigned to experiences."
            )

        if policy.stay_count > 0:
            raise ValueError(
                "Cannot delete a cancellation policy that is "
                "currently assigned to stays."
            )

        db.session.delete(policy)
        db.session.commit()

        return True

    # =========================================================================
    # Statistics
    # =========================================================================

    @staticmethod
    def get_statistics():
        """
        Return cancellation policy statistics.
        """

        total = CancellationPolicy.query.count()

        active = CancellationPolicy.query.filter(
            CancellationPolicy.active.is_(True)
        ).count()

        inactive = CancellationPolicy.query.filter(
            CancellationPolicy.active.is_(False)
        ).count()

        default = CancellationPolicy.query.filter(
            CancellationPolicy.default_policy.is_(True)
        ).count()

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "default": default
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_cancellation_policy(**kwargs):
    return CancellationPolicyService.create_policy(**kwargs)


def get_cancellation_policy(policy_id):
    return CancellationPolicyService.get_by_id(policy_id)


def get_default_cancellation_policy():
    return CancellationPolicyService.get_default()


def update_cancellation_policy(policy_id, **updates):
    return CancellationPolicyService.update_policy(
        policy_id,
        **updates
    )


def set_default_cancellation_policy(policy_id):
    return CancellationPolicyService.set_default(policy_id)


def calculate_refund_percentage(
    policy_id,
    days_before_trip
):
    return CancellationPolicyService.calculate_refund_percentage(
        policy_id,
        days_before_trip
    )