"""
===============================================================================
The Uncharted Route
Newsletter Service
===============================================================================
Business logic for newsletter subscriptions.
This service manages:

• Newsletter subscriptions
• Subscriber creation
• Duplicate subscription handling
• Double opt-in verification
• Unsubscription
• Re-subscription
• Marketing preferences
• Interest segmentation
• Consent tracking
• Engagement tracking
• Subscriber lookup
• Subscriber statistics

The service works with:
    NewsletterSubscriber
    Newsletter

The service does not handle email delivery itself.
Email delivery should be handled by a separate email service.
"""

from datetime import datetime, timezone
import secrets
from extensions import db
from app.models import NewsletterSubscriber, Newsletter

# =============================================================================
# Newsletter Service
# =============================================================================
class NewsletterService:
    """
    Service layer for newsletter management.
    """

    # =========================================================================
    # Subscription
    # =========================================================================
    @staticmethod
    def subscribe(
        email,
        first_name=None,
        last_name=None,
        country=None,
        source="Website",
        marketing_consent=False,
        interests=None
    ):
        """
        Subscribe a user to the newsletter.
        If the email already exists:
        • Reactivate an unsubscribed subscriber.
        • Update subscriber information.
        • Preserve existing engagement history.
        Returns:
            NewsletterSubscriber
        """

        if not email:
            raise ValueError("Email address is required.")
        email = email.strip().lower()
        subscriber = NewsletterSubscriber.query.filter_by(
            email=email
        ).first()

        # ---------------------------------------------------------------------
        # Existing Subscriber
        # ---------------------------------------------------------------------
        if subscriber:
            subscriber.subscribed = True
            subscriber.unsubscribed_at = None
            subscriber.unsubscribe_reason = None
            if first_name:
                subscriber.first_name = first_name
            if last_name:
                subscriber.last_name = last_name
            if country:
                subscriber.country = country
            if source:
                subscriber.source = source

            # -------------------------------------------------------------
            # Marketing Consent
            # -------------------------------------------------------------
            if marketing_consent:
                subscriber.marketing_consent = True
                subscriber.consent_date = datetime.now(timezone.utc)

            # -------------------------------------------------------------
            # Interests
            # -------------------------------------------------------------
            if interests:
                NewsletterService.update_interests(
                    subscriber,
                    interests)
            db.session.commit()
            return subscriber

        # ---------------------------------------------------------------------
        # Verification Token
        # ---------------------------------------------------------------------
        verification_token = secrets.token_urlsafe(32)

        # ---------------------------------------------------------------------
        # Create Subscriber
        # ---------------------------------------------------------------------
        subscriber = NewsletterSubscriber(
            email=email,
            first_name=first_name,
            last_name=last_name,
            country=country,
            subscribed=True,
            verified=False,
            verification_token=verification_token,
            source=source or "Website",
            marketing_consent=marketing_consent,
            consent_date=(
                datetime.now(timezone.utc)
                if marketing_consent
                else None))

        # ---------------------------------------------------------------------
        # Interests
        # ---------------------------------------------------------------------
        if interests:
            NewsletterService.update_interests(
                subscriber,
                interests)
        db.session.add(subscriber)
        db.session.commit()
        return subscriber

    # =========================================================================
    # Verification
    # =========================================================================
    @staticmethod
    def verify_subscription(token):
        """
        Verify a newsletter subscription using a verification token.
        Returns:
            NewsletterSubscriber
        Raises:
            ValueError if the token is invalid.
        """

        if not token:
            raise ValueError("Verification token is required.")

        subscriber = NewsletterSubscriber.query.filter_by(
            verification_token=token
        ).first()

        if not subscriber:
            raise ValueError("Invalid verification token.")
        subscriber.verified = True
        subscriber.verification_token = None
        db.session.commit()
        return subscriber

    # =========================================================================
    # Resend Verification Token
    # =========================================================================
    @staticmethod
    def generate_verification_token(subscriber):
        """
        Generate a new verification token for a subscriber.
        """

        if not subscriber:
            raise ValueError("Subscriber is required.")
        token = secrets.token_urlsafe(32)
        subscriber.verification_token = token
        db.session.commit()
        return token

    # =========================================================================
    # Unsubscribe
    # =========================================================================
    @staticmethod
    def unsubscribe(
        email,
        reason=None):
        """
        Unsubscribe a newsletter subscriber.
        Returns:
            NewsletterSubscriber
        Raises:
            ValueError if subscriber does not exist.
        """

        if not email:
            raise ValueError("Email address is required.")
        email = email.strip().lower()
        subscriber = NewsletterSubscriber.query.filter_by(
            email=email).first()
        if not subscriber:
            raise ValueError("Subscriber not found.")
        subscriber.subscribed = False
        subscriber.unsubscribed_at = datetime.now(timezone.utc)
        subscriber.unsubscribe_reason = reason
        db.session.commit()
        return subscriber

    # =========================================================================
    # Resubscribe
    # =========================================================================
    @staticmethod
    def resubscribe(email):
        """
        Reactivate an existing newsletter subscription.
        """
        if not email:
            raise ValueError("Email address is required.")
        email = email.strip().lower()
        subscriber = NewsletterSubscriber.query.filter_by(
            email=email
        ).first()
        if not subscriber:
            raise ValueError("Subscriber not found.")
        subscriber.subscribed = True
        subscriber.unsubscribed_at = None
        subscriber.unsubscribe_reason = None
        db.session.commit()
        return subscriber

    # =========================================================================
    # Preferences
    # =========================================================================
    @staticmethod
    def update_preferences(
        subscriber,
        receive_promotions=None,
        receive_new_experiences=None,
        receive_blog_updates=None,
        receive_company_news=None):
        """
        Update newsletter communication preferences.
        """
        if not subscriber:
            raise ValueError("Subscriber is required.")
        if receive_promotions is not None:
            subscriber.receive_promotions = receive_promotions
        if receive_new_experiences is not None:
            subscriber.receive_new_experiences = (
                receive_new_experiences)
        if receive_blog_updates is not None:
            subscriber.receive_blog_updates = (
                receive_blog_updates)
        if receive_company_news is not None:
            subscriber.receive_company_news = (
                receive_company_news)
        db.session.commit()
        return subscriber

    # =========================================================================
    # Interest Segmentation
    # =========================================================================
    @staticmethod
    def update_interests(
        subscriber,
        interests
    ):
        """
        Update subscriber interest segments.

        Accepted interests include:

            adventure
            wildlife
            luxury
            coastal
            corporate
            family
        """

        if not subscriber:
            raise ValueError("Subscriber is required.")
        if not interests:
            return subscriber
        if isinstance(interests, str):
            interests = [
                interest.strip().lower()
                for interest in interests.split(",")]

        supported_interests = {
            "adventure",
            "wildlife",
            "luxury",
            "coastal",
            "corporate",
            "family"}

        # ---------------------------------------------------------------------
        # Reset all interests
        # ---------------------------------------------------------------------
        for interest in supported_interests:
            setattr(
                subscriber,
                interest,
                False)

        # ---------------------------------------------------------------------
        # Apply Selected Interests
        # ---------------------------------------------------------------------
        for interest in interests:
            normalized = interest.strip().lower()
            if normalized in supported_interests:
                setattr(
                    subscriber,
                    normalized,
                    True)
        return subscriber

    # =========================================================================
    # Consent
    # =========================================================================
    @staticmethod
    def update_consent(
        subscriber,
        consent=True):
        """
        Update marketing consent.
        """
        if not subscriber:
            raise ValueError("Subscriber is required.")
        subscriber.marketing_consent = consent
        if consent:
            subscriber.consent_date = datetime.now(timezone.utc)
        else:
            subscriber.consent_date = None
        db.session.commit()
        return subscriber

    # =========================================================================
    # Subscriber Lookup
    # =========================================================================

    @staticmethod
    def get_by_email(email):
        """
        Find a subscriber by email address.
        """

        if not email:
            return None

        return NewsletterSubscriber.query.filter_by(
            email=email.strip().lower()
        ).first()

    # =========================================================================
    # Subscriber Lookup By ID
    # =========================================================================
    @staticmethod
    def get_by_id(subscriber_id):
        """
        Find a subscriber by ID.
        """
        return NewsletterSubscriber.query.get(subscriber_id)

    # =========================================================================
    # Active Subscribers
    # =========================================================================
    @staticmethod
    def get_active_subscribers():
        """
        Return verified and subscribed newsletter subscribers
        who have granted marketing consent.
        """

        return NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed.is_(True),
            NewsletterSubscriber.verified.is_(True),
            NewsletterSubscriber.marketing_consent.is_(True)
        ).all()

    # =========================================================================
    # Preference-Based Subscribers
    # =========================================================================
    @staticmethod
    def get_subscribers_for_promotions():
        """
        Return subscribers who opted into promotions.
        """
        return NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed.is_(True),
            NewsletterSubscriber.verified.is_(True),
            NewsletterSubscriber.marketing_consent.is_(True),
            NewsletterSubscriber.receive_promotions.is_(True)).all()

    # -------------------------------------------------------------------------
    @staticmethod
    def get_subscribers_for_new_experiences():
        """
        Return subscribers interested in new experiences.
        """
        return NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed.is_(True),
            NewsletterSubscriber.verified.is_(True),
            NewsletterSubscriber.marketing_consent.is_(True),
            NewsletterSubscriber.receive_new_experiences.is_(True)).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_subscribers_for_blog_updates():
        """
        Return subscribers interested in blog updates.
        """
        return NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed.is_(True),
            NewsletterSubscriber.verified.is_(True),
            NewsletterSubscriber.marketing_consent.is_(True),
            NewsletterSubscriber.receive_blog_updates.is_(True)
        ).all()

    # -------------------------------------------------------------------------
    @staticmethod
    def get_subscribers_for_company_news():
        """
        Return subscribers interested in company news.
        """

        return NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed.is_(True),
            NewsletterSubscriber.verified.is_(True),
            NewsletterSubscriber.marketing_consent.is_(True),
            NewsletterSubscriber.receive_company_news.is_(True)
        ).all()

    # =========================================================================
    # Interest Segments
    # =========================================================================
    @staticmethod
    def get_by_interest(interest):
        """
        Return active subscribers belonging to an interest segment.
        """
        supported_interests = {
            "adventure",
            "wildlife",
            "luxury",
            "coastal",
            "corporate",
            "family"}

        interest = interest.strip().lower()
        if interest not in supported_interests:
            raise ValueError(f"Unsupported interest segment: {interest}")
        column = getattr(NewsletterSubscriber,interest)
        return NewsletterSubscriber.query.filter(
            NewsletterSubscriber.subscribed.is_(True),
            NewsletterSubscriber.verified.is_(True),
            NewsletterSubscriber.marketing_consent.is_(True),
            column.is_(True)).all()

    # =========================================================================
    # Engagement Tracking
    # =========================================================================
    @staticmethod
    def record_email_sent(subscriber):
        """
        Record that an email was sent to a subscriber.
        """
        if not subscriber:
            raise ValueError("Subscriber is required.")
        subscriber.last_email_sent = (
            datetime.now(timezone.utc))
        subscriber.total_emails_sent += 1
        db.session.commit()
        return subscriber

    # ------------------------------------------------------------------------
    @staticmethod
    def record_email_opened(subscriber):
        """
        Record an email open.
        """

        if not subscriber:
            raise ValueError("Subscriber is required.")

        subscriber.last_opened = (
            datetime.now(timezone.utc)
        )

        subscriber.total_opens += 1

        db.session.commit()

        return subscriber

    # -------------------------------------------------------------------------
    @staticmethod
    def record_email_clicked(subscriber):
        """
        Record an email link click.
        """
        if not subscriber:
            raise ValueError("Subscriber is required.")

        subscriber.last_clicked = (
            datetime.now(timezone.utc))
        subscriber.total_clicks += 1
        db.session.commit()
        return subscriber

    # =========================================================================
    # Subscriber Statistics
    # =========================================================================
    @staticmethod
    def get_statistics():
        """
        Return newsletter subscriber statistics.
        """
        total = NewsletterSubscriber.query.count()

        subscribed = NewsletterSubscriber.query.filter_by(
            subscribed=True
        ).count()

        verified = NewsletterSubscriber.query.filter_by(
            verified=True
        ).count()

        consented = NewsletterSubscriber.query.filter_by(
            marketing_consent=True
        ).count()
        unsubscribed = NewsletterSubscriber.query.filter_by(
            subscribed=False
        ).count()
        return {
            "total": total,
            "subscribed": subscribed,
            "verified": verified,
            "marketing_consented": consented,
            "unsubscribed": unsubscribed}

    # =========================================================================
    # Newsletter Compatibility Model
    # =========================================================================
    @staticmethod
    def create_legacy_newsletter(
        email,
        source="Website"):
        """
        Create a record in the simpler Newsletter model.
        This method exists because the project currently contains
        both NewsletterSubscriber and Newsletter models.

        NewsletterSubscriber should be preferred for the full
        subscription system.
        """
        if not email:
            raise ValueError("Email address is required.")
        email = email.strip().lower()
        newsletter = Newsletter.query.filter_by(
            email=email
        ).first()
        if newsletter:
            newsletter.is_subscribed = True
            newsletter.source = source
            db.session.commit()
            return newsletter
        newsletter = Newsletter(
            email=email,
            is_subscribed=True,
            is_verified=False,
            source=source)
        db.session.add(newsletter)
        db.session.commit()
        return newsletter

    # =========================================================================
    # Legacy Newsletter Lookup
    # =========================================================================
    @staticmethod
    def get_legacy_newsletter(email):
        """
        Find a record from the simpler Newsletter model.
        """
        if not email:
            return None
        return Newsletter.query.filter_by(
            email=email.strip().lower()
        ).first()

    # =========================================================================
    # Legacy Unsubscribe
    # =========================================================================
    @staticmethod
    def unsubscribe_legacy(email):
        """
        Unsubscribe a record from the simpler Newsletter model.
        """
        newsletter = NewsletterService.get_legacy_newsletter(email)
        if not newsletter:
            raise ValueError("Newsletter subscriber not found.")
        newsletter.is_subscribed = False
        db.session.commit()
        return newsletter

# =============================================================================
# Convenience Functions
# =============================================================================
def subscribe_to_newsletter(
    email,
    first_name=None,
    last_name=None,
    country=None,
    source="Website",
    marketing_consent=False,
    interests=None
):
    """
    Convenience wrapper around NewsletterService.subscribe().
    """

    return NewsletterService.subscribe(
        email=email,
        first_name=first_name,
        last_name=last_name,
        country=country,
        source=source,
        marketing_consent=marketing_consent,
        interests=interests)

def verify_newsletter_subscription(token):
    """
    Convenience wrapper for subscription verification.
    """
    return NewsletterService.verify_subscription(token)

def unsubscribe_from_newsletter(
    email,
    reason=None):
    """
    Convenience wrapper for newsletter unsubscribe.
    """
    return NewsletterService.unsubscribe(
        email,reason=reason)

def get_newsletter_subscriber(email):
    """
    Convenience wrapper for subscriber lookup.
    """
    return NewsletterService.get_by_email(email)