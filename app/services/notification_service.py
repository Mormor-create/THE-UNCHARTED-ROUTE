"""
===============================================================================
The Uncharted Route
Notification Service
===============================================================================

Centralized notification service for The Uncharted Route.

This service manages application notifications and coordinates delivery
through supported channels.

Supported notification channels:

• In-App
• Email
• Both

Typical notifications include:

• New booking
• Booking confirmation
• Booking cancellation
• Payment received
• Payment failed
• Contact enquiry
• New review
• Review approval
• Account verification
• Password reset
• System notifications

The service is intentionally kept separate from email_service.py.

email_service.py
    Responsible for delivering email.

notification_service.py
    Responsible for creating and coordinating notifications.
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Notification Service
# =============================================================================

class NotificationService:
    """
    Centralized application notification service.
    """

    # =========================================================================
    # Notification Creation
    # =========================================================================

    def create_notification(
        self,
        user_id,
        title: str,
        message: str,
        notification_type: str = "General",
        channel: str = "In-App",
        action_url: str = None,
        reference_type: str = None,
        reference_id: int = None,
        priority: str = "Normal",
        commit: bool = True,
    ):
        """
        Create an application notification.

        Parameters
        ----------
        user_id:
            ID of the user receiving the notification.

        title:
            Notification title.

        message:
            Notification message.

        notification_type:
            Type of notification.

        channel:
            In-App, Email, or Both.

        action_url:
            Optional URL the notification should open.

        reference_type:
            Optional related object type.

        reference_id:
            Optional related object ID.

        priority:
            Low, Normal, High, or Urgent.

        commit:
            Whether the database transaction should be committed.

        Returns
        -------
        Notification object or None
        """

        if not user_id:
            return None

        if not title:
            raise ValueError(
                "Notification title is required."
            )

        if not message:
            raise ValueError(
                "Notification message is required."
            )

        # Import lazily to avoid circular imports.
        from app.models.notification import Notification

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            channel=channel,
            action_url=action_url,
            reference_type=reference_type,
            reference_id=reference_id,
            priority=priority,
        )

        db.session.add(notification)

        if commit:
            db.session.commit()

        return notification

    # =========================================================================
    # Mark as Read
    # =========================================================================

    def mark_as_read(
        self,
        notification_id: int,
        user_id: int = None,
        commit: bool = True,
    ) -> bool:
        """
        Mark a notification as read.
        """

        from app.models.notification import Notification

        notification = Notification.query.get(
            notification_id
        )

        if not notification:
            return False

        if (
            user_id is not None
            and notification.user_id != user_id
        ):
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return True

    # =========================================================================
    # Mark as Unread
    # =========================================================================

    def mark_as_unread(
        self,
        notification_id: int,
        user_id: int = None,
        commit: bool = True,
    ) -> bool:
        """
        Mark a notification as unread.
        """

        from app.models.notification import Notification

        notification = Notification.query.get(
            notification_id
        )

        if not notification:
            return False

        if (
            user_id is not None
            and notification.user_id != user_id
        ):
            return False

        notification.is_read = False
        notification.read_at = None

        if commit:
            db.session.commit()

        return True

    # =========================================================================
    # Mark All as Read
    # =========================================================================

    def mark_all_as_read(
        self,
        user_id: int,
        commit: bool = True,
    ) -> int:
        """
        Mark all notifications belonging to a user as read.

        Returns the number of notifications updated.
        """

        from app.models.notification import Notification

        notifications = Notification.query.filter_by(
            user_id=user_id,
            is_read=False,
        ).all()

        now = datetime.utcnow()

        for notification in notifications:
            notification.is_read = True
            notification.read_at = now

        if commit:
            db.session.commit()

        return len(notifications)

    # =========================================================================
    # Delete Notification
    # =========================================================================

    def delete_notification(
        self,
        notification_id: int,
        user_id: int = None,
        commit: bool = True,
    ) -> bool:
        """
        Delete a notification.
        """

        from app.models.notification import Notification

        notification = Notification.query.get(
            notification_id
        )

        if not notification:
            return False

        if (
            user_id is not None
            and notification.user_id != user_id
        ):
            return False

        db.session.delete(notification)

        if commit:
            db.session.commit()

        return True

    # =========================================================================
    # Booking Notifications
    # =========================================================================

    def notify_booking_created(
        self,
        user_id: int,
        booking_id: int,
        booking_reference: str = None,
    ):
        """
        Notify a user that a booking has been created.
        """

        reference = (
            booking_reference
            or str(booking_id)
        )

        return self.create_notification(
            user_id=user_id,
            title="Booking Received",
            message=(
                f"Your booking "
                f"{reference} has been received."
            ),
            notification_type="Booking",
            channel="Both",
            action_url=f"/booking/{booking_id}",
            reference_type="Booking",
            reference_id=booking_id,
        )

    # =========================================================================
    # Booking Confirmation
    # =========================================================================

    def notify_booking_confirmed(
        self,
        user_id: int,
        booking_id: int,
        booking_reference: str = None,
    ):
        """
        Notify a user that a booking has been confirmed.
        """

        reference = (
            booking_reference
            or str(booking_id)
        )

        return self.create_notification(
            user_id=user_id,
            title="Booking Confirmed",
            message=(
                f"Your booking "
                f"{reference} has been confirmed."
            ),
            notification_type="Booking Confirmation",
            channel="Both",
            action_url=f"/booking/{booking_id}",
            reference_type="Booking",
            reference_id=booking_id,
            priority="High",
        )

    # =========================================================================
    # Booking Cancellation
    # =========================================================================

    def notify_booking_cancelled(
        self,
        user_id: int,
        booking_id: int,
        booking_reference: str = None,
    ):
        """
        Notify a user that a booking has been cancelled.
        """

        reference = (
            booking_reference
            or str(booking_id)
        )

        return self.create_notification(
            user_id=user_id,
            title="Booking Cancelled",
            message=(
                f"Your booking "
                f"{reference} has been cancelled."
            ),
            notification_type="Booking Cancellation",
            channel="Both",
            action_url=f"/booking/{booking_id}",
            reference_type="Booking",
            reference_id=booking_id,
            priority="High",
        )

    # =========================================================================
    # Payment Notifications
    # =========================================================================

    def notify_payment_received(
        self,
        user_id: int,
        booking_id: int,
        amount,
        currency: str = "KES",
    ):
        """
        Notify a user that payment has been received.
        """

        return self.create_notification(
            user_id=user_id,
            title="Payment Received",
            message=(
                f"Your payment of "
                f"{currency} {amount:,.2f} "
                f"has been received."
            ),
            notification_type="Payment",
            channel="Both",
            action_url=f"/booking/{booking_id}",
            reference_type="Booking",
            reference_id=booking_id,
        )

    # =========================================================================
    # Payment Failure
    # =========================================================================

    def notify_payment_failed(
        self,
        user_id: int,
        booking_id: int,
    ):
        """
        Notify a user that a payment failed.
        """

        return self.create_notification(
            user_id=user_id,
            title="Payment Failed",
            message=(
                "Your payment could not be completed. "
                "Please try again or contact our team."
            ),
            notification_type="Payment",
            channel="Both",
            action_url=f"/booking/{booking_id}",
            reference_type="Booking",
            reference_id=booking_id,
            priority="High",
        )

    # =========================================================================
    # Review Notifications
    # =========================================================================

    def notify_review_received(
        self,
        user_id: int,
        review_id: int,
        experience_name: str = None,
    ):
        """
        Notify an internal user that a new review was submitted.
        """

        experience_text = (
            experience_name
            or "an experiences"
        )

        return self.create_notification(
            user_id=user_id,
            title="New Experience Review",
            message=(
                f"A new review has been submitted "
                f"for {experience_text}."
            ),
            notification_type="Review",
            channel="In-App",
            action_url=f"/admin/reviews/{review_id}",
            reference_type="ExperienceReview",
            reference_id=review_id,
        )

    # =========================================================================
    # Review Approval
    # =========================================================================

    def notify_review_approved(
        self,
        user_id: int,
        review_id: int,
    ):
        """
        Notify a reviewer that their review was approved.
        """

        return self.create_notification(
            user_id=user_id,
            title="Review Published",
            message=(
                "Your experiences review has been "
                "approved and published."
            ),
            notification_type="Review",
            channel="Both",
            action_url=f"/reviews/{review_id}",
            reference_type="ExperienceReview",
            reference_id=review_id,
        )

    # =========================================================================
    # Contact Enquiry
    # =========================================================================

    def notify_contact_enquiry(
        self,
        user_id: int,
        contact_id: int,
        subject: str = None,
    ):
        """
        Notify an internal user of a new contact enquiry.
        """

        subject = (
            subject
            or "New Website Enquiry"
        )

        return self.create_notification(
            user_id=user_id,
            title="New Contact Enquiry",
            message=(
                f"A new enquiry has been received: "
                f"{subject}"
            ),
            notification_type="Contact",
            channel="In-App",
            action_url=f"/admin/contacts/{contact_id}",
            reference_type="Contact",
            reference_id=contact_id,
            priority="High",
        )

    # =========================================================================
    # Account Verification
    # =========================================================================

    def notify_account_verified(
        self,
        user_id: int,
    ):
        """
        Notify a user that their account has been verified.
        """

        return self.create_notification(
            user_id=user_id,
            title="Account Verified",
            message=(
                "Your account has been successfully verified."
            ),
            notification_type="Account",
            channel="In-App",
            action_url="/account",
            reference_type="User",
            reference_id=user_id,
        )

    # =========================================================================
    # System Notification
    # =========================================================================

    def notify_user(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "General",
        action_url: str = None,
        priority: str = "Normal",
    ):
        """
        Create a general user notification.
        """

        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            channel="In-App",
            action_url=action_url,
            priority=priority,
        )

    # =========================================================================
    # Bulk Notifications
    # =========================================================================

    def notify_users(
        self,
        user_ids,
        title: str,
        message: str,
        notification_type: str = "General",
        action_url: str = None,
        priority: str = "Normal",
    ) -> int:
        """
        Create the same notification for multiple users.

        Returns the number of notifications created.
        """

        count = 0

        for user_id in user_ids:
            notification = self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                channel="In-App",
                action_url=action_url,
                priority=priority,
                commit=False,
            )

            if notification:
                count += 1

        db.session.commit()

        return count


# =============================================================================
# Service Instance
# =============================================================================

notification_service = NotificationService()


# =============================================================================
# Convenience Functions
# =============================================================================

def create_notification(
    user_id,
    title,
    message,
    notification_type="General",
    channel="In-App",
    action_url=None,
    reference_type=None,
    reference_id=None,
    priority="Normal",
    commit=True,
):
    """
    Convenience wrapper for notification creation.
    """

    return notification_service.create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        channel=channel,
        action_url=action_url,
        reference_type=reference_type,
        reference_id=reference_id,
        priority=priority,
        commit=commit,
    )


def mark_as_read(
    notification_id,
    user_id=None,
):
    """
    Convenience wrapper for marking a notification as read.
    """

    return notification_service.mark_as_read(
        notification_id,
        user_id,
    )


def mark_all_as_read(
    user_id,
):
    """
    Convenience wrapper for marking all notifications as read.
    """

    return notification_service.mark_all_as_read(
        user_id,
    )


def notify_booking_created(
    user_id,
    booking_id,
    booking_reference=None,
):
    return notification_service.notify_booking_created(
        user_id,
        booking_id,
        booking_reference,
    )


def notify_booking_confirmed(
    user_id,
    booking_id,
    booking_reference=None,
):
    return notification_service.notify_booking_confirmed(
        user_id,
        booking_id,
        booking_reference,
    )

def notify_booking_cancelled(
    user_id,
    booking_id,
    booking_reference=None,
):
    return notification_service.notify_booking_cancelled(
        user_id,
        booking_id,
        booking_reference,)

def notify_payment_received(
    user_id,
    booking_id,
    amount,
    currency="KES",
):
    return notification_service.notify_payment_received(
        user_id,
        booking_id,
        amount,
        currency,
    )


def notify_payment_failed(
    user_id,
    booking_id,
):
    return notification_service.notify_payment_failed(
        user_id,
        booking_id,
    )

def notify_user(
    user_id,
    title,
    message,
    notification_type="General",
    action_url=None,
    priority="Normal",
):
    return notification_service.notify_user(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
        priority=priority,
    )