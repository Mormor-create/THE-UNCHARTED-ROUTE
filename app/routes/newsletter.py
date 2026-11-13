"""
===============================================================================
The Uncharted Route
Admin Newsletter CMS Routes
===============================================================================
Manage newsletter subscribers and compose newsletter emails.
URL prefix:
    /admin/newsletter
"""
from datetime import datetime
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from sqlalchemy import func, or_
from app.decorators.admin import admin_required
from app.forms.newsletter import (
    NewsletterComposeForm,
    NewsletterSubscriberFilterForm,
    NewsletterSubscriberForm,)
from app.models import NewsletterSubscriber
from app.services.email_service import EmailService
from extensions import db

# =============================================================================
# Blueprint
# =============================================================================
newsletter_bp = Blueprint(
    "admin_newsletter",
    __name__,
    url_prefix="/admin/newsletter",)

# =============================================================================
# Helpers
# =============================================================================
def _get_subscriber_or_404(subscriber_id):
    """Return a subscriber or raise a 404 response."""
    subscriber = db.session.get(
        NewsletterSubscriber,
        subscriber_id,)
    if subscriber is None:
        abort(404)
    return subscriber

def _subscriber_query():
    """Return the base subscriber query."""
    return NewsletterSubscriber.query

# =============================================================================
# Newsletter Dashboard
# =============================================================================
@newsletter_bp.route("/", methods=["GET"])
@admin_required
def index():
    """Display newsletter statistics and recent subscribers."""
    total_subscribers = NewsletterSubscriber.query.count()
    subscribed_count = NewsletterSubscriber.query.filter_by(
        subscribed=True,).count()

    verified_count = NewsletterSubscriber.query.filter_by(
        verified=True,).count()

    eligible_count = NewsletterSubscriber.query.filter_by(
        subscribed=True,
        verified=True,).count()

    recent_subscribers = (
        NewsletterSubscriber.query
        .order_by(NewsletterSubscriber.id.desc())
        .limit(10)
        .all())
    return render_template(
        "admin/newsletter/index.html",
        total_subscribers=total_subscribers,
        subscribed_count=subscribed_count,
        verified_count=verified_count,
        eligible_count=eligible_count,
        recent_subscribers=recent_subscribers,)

# =============================================================================
# Subscriber List
# =============================================================================
@newsletter_bp.route("/subscribers/", methods=["GET"])
@admin_required
def subscribers():
    """Display and filter newsletter subscribers."""

    form = NewsletterSubscriberFilterForm(
        request.args,
        meta={"csrf": False},
    )

    query = _subscriber_query()

    search_term = request.args.get(
        "search",
        "",
        type=str,
    ).strip()

    status = request.args.get(
        "status",
        "",
        type=str,
    ).strip()

    if search_term:
        query = query.filter(
            NewsletterSubscriber.email.ilike(
                f"%{search_term}%"
            )
        )

    if status == "subscribed":
        query = query.filter(
            NewsletterSubscriber.subscribed.is_(True)
        )
    elif status == "unsubscribed":
        query = query.filter(
            NewsletterSubscriber.subscribed.is_(False)
        )
    elif status == "verified":
        query = query.filter(
            NewsletterSubscriber.verified.is_(True)
        )
    elif status == "unverified":
        query = query.filter(
            NewsletterSubscriber.verified.is_(False)
        )

    page = max(
        request.args.get("page", 1, type=int),
        1,
    )

    pagination = (
        query
        .order_by(NewsletterSubscriber.id.desc())
        .paginate(
            page=page,
            per_page=20,
            error_out=False,))

    return render_template(
        "admin/newsletter/subscribers.html",
        form=form,
        subscribers=pagination.items,
        pagination=pagination,
        search_term=search_term,
        selected_status=status,)

# =============================================================================
# Subscriber Detail
# =============================================================================
@newsletter_bp.route("/subscribers/<int:subscriber_id>/",methods=["GET"],)
@admin_required
def subscriber_detail(subscriber_id):
    """Display a subscriber's details."""

    subscriber = _get_subscriber_or_404(subscriber_id)

    return render_template(
        "admin/newsletter/subscriber_detail.html",
        subscriber=subscriber,)

# =============================================================================
# Create Subscriber
# =============================================================================
@newsletter_bp.route("/subscribers/create", methods=["GET", "POST"])
@admin_required
def create_subscriber():
    """Add a subscriber through the admin CMS."""
    form = NewsletterSubscriberForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        existing = NewsletterSubscriber.query.filter(
            func.lower(NewsletterSubscriber.email) == email
        ).first()

        if existing:
            flash(
                "A subscriber with that email address already exists.",
                "warning",)
            return render_template(
                "admin/newsletter/subscriber_form.html",
                form=form,
                subscriber=None,
                page_title="Add Subscriber",)

        marketing_consent = bool(form.marketing_consent.data)

        subscriber = NewsletterSubscriber(
            email=email,
            first_name=(
                form.first_name.data.strip()
                if form.first_name.data
                else None),
            last_name=(
                form.last_name.data.strip()
                if form.last_name.data
                else None
            ),
            country=(
                form.country.data.strip()
                if form.country.data
                else None
            ),
            subscribed=bool(form.subscribed.data),
            verified=bool(form.verified.data),
            marketing_consent=marketing_consent,
            consent_date=datetime.utcnow() if marketing_consent else None,
        )

        db.session.add(subscriber)
        db.session.commit()

        flash(
            "Newsletter subscriber created successfully.",
            "success",)

        return redirect(
            url_for(
                "admin_newsletter.subscriber_detail",
                subscriber_id=subscriber.id,))

    return render_template(
        "admin/newsletter/subscriber_form.html",
        form=form,
        subscriber=None,
        page_title="Add Subscriber",)

# =============================================================================
# Edit Subscriber
# =============================================================================
@newsletter_bp.route("/subscribers/<int:subscriber_id>/edit",methods=["GET", "POST"],)
@admin_required
def edit_subscriber(subscriber_id):
    """Edit an existing subscriber."""
    subscriber = _get_subscriber_or_404(subscriber_id)
    form = NewsletterSubscriberForm(obj=subscriber)

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        duplicate = NewsletterSubscriber.query.filter(
            func.lower(NewsletterSubscriber.email) == email,
            NewsletterSubscriber.id != subscriber.id,
        ).first()

        if duplicate:
            flash(
                "Another subscriber already uses that email address.",
                "warning",
            )
            return render_template(
                "admin/newsletter/subscriber_form.html",
                form=form,
                subscriber=subscriber,
                page_title="Edit Subscriber",
            )

        was_consented = bool(subscriber.marketing_consent)
        marketing_consent = bool(form.marketing_consent.data)

        subscriber.email = email
        subscriber.first_name = (
            form.first_name.data.strip()
            if form.first_name.data
            else None
        )
        subscriber.last_name = (
            form.last_name.data.strip()
            if form.last_name.data
            else None
        )
        subscriber.country = (
            form.country.data.strip()
            if form.country.data
            else None
        )

        subscriber.subscribed = bool(form.subscribed.data)
        subscriber.verified = bool(form.verified.data)
        subscriber.marketing_consent = marketing_consent

        if marketing_consent and not was_consented:
            # Record when consent is newly recorded.
            subscriber.consent_date = datetime.utcnow()
        elif not marketing_consent:
            subscriber.consent_date = None

        db.session.commit()

        flash(
            "Subscriber updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_newsletter.subscriber_detail",
                subscriber_id=subscriber.id,))

    return render_template(
        "admin/newsletter/subscriber_form.html",
        form=form,
        subscriber=subscriber,
        page_title="Edit Subscriber",)

# =============================================================================
# Subscription Status Actions
# =============================================================================
@newsletter_bp.route("/subscribers/<int:subscriber_id>/unsubscribe",methods=["POST"],)
@admin_required
def unsubscribe_subscriber(subscriber_id):
    """Mark a subscriber as unsubscribed."""
    subscriber = _get_subscriber_or_404(subscriber_id)
    subscriber.subscribed = False
    db.session.commit()
    flash("Subscriber has been unsubscribed.","success",)

    return redirect(
        url_for(
            "admin_newsletter.subscriber_detail",
            subscriber_id=subscriber.id,))

@newsletter_bp.route("/subscribers/<int:subscriber_id>/resubscribe",methods=["POST"],)
@admin_required
def resubscribe_subscriber(subscriber_id):
    """Restore subscription status for an existing subscriber."""
    subscriber = _get_subscriber_or_404(subscriber_id)
    subscriber.subscribed = True
    db.session.commit()
    flash("Subscriber has been marked as subscribed.","success",)

    return redirect(
        url_for(
            "admin_newsletter.subscriber_detail",
            subscriber_id=subscriber.id,))


# =============================================================================
# Newsletter Composer
# =============================================================================
@newsletter_bp.route("/compose", methods=["GET", "POST"])
@admin_required
def compose():
    """Compose and send a newsletter to eligible subscribers."""
    form = NewsletterComposeForm()

    # Refresh the current session's view of subscriber records.
    db.session.expire_all()

    eligible_query = NewsletterSubscriber.query.filter_by(
        subscribed=True,
        verified=True,
        marketing_consent=True,
    )

    eligible_count = eligible_query.count()

    if form.validate_on_submit():
        if not form.confirm_send.data:
            flash(
                "Please confirm before sending the newsletter.",
                "warning",
            )
            return render_template(
                "admin/newsletter/compose.html",
                form=form,
                eligible_count=eligible_count,
            )

        if eligible_count == 0:
            flash(
                "There are no verified, subscribed recipients with "
                "recorded marketing consent.",
                "warning",
            )
            return render_template(
                "admin/newsletter/compose.html",
                form=form,
                eligible_count=eligible_count,
            )

        recipients = eligible_query.order_by(
            NewsletterSubscriber.id.asc()
        ).all()

        email_service = EmailService()
        sent_count = 0
        failed_count = 0

        subject = form.subject.data.strip()
        body = form.body.data.strip()
        html_body = (
            form.html_body.data.strip()
            if form.html_body.data
            else None
        )

        for subscriber in recipients:
            try:
                sent = email_service.send_newsletter(
                    subscriber=subscriber,
                    subject=subject,
                    body=body,
                    html_body=html_body,
                )

                if sent:
                    sent_count += 1
                else:
                    failed_count += 1

            except Exception:
                from flask import current_app

                current_app.logger.exception(
                    "Newsletter delivery failed for subscriber ID %s",
                    subscriber.id,
                )
                failed_count += 1

        if sent_count:
            flash(
                f"Newsletter sent successfully to {sent_count} "
                f"subscriber(s).",
                "success",
            )

        if failed_count:
            flash(
                f"{failed_count} newsletter delivery attempt(s) failed. "
                "Check the application logs for details.",
                "warning",
            )

        return redirect(url_for("admin_newsletter.index"))

    return render_template(
        "admin/newsletter/compose.html",
        form=form,
        eligible_count=eligible_count,)