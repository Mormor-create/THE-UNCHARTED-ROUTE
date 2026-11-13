"""
Public newsletter signup and email verification routes.
"""

import uuid
import base64
from flask import Response
from itsdangerous import BadSignature, URLSafeSerializer
from datetime import datetime
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from extensions import db
from app.models import NewsletterSubscriber
from app.services.email_service import email_service

public_newsletter_bp = Blueprint(
    "public_newsletter",
    __name__,
    url_prefix="/newsletter",)

def _send_verification_email(subscriber):
    """Send a confirmation link before enabling marketing emails."""
    verification_url = url_for(
        "public_newsletter.verify",
        token=subscriber.verification_token,
        _external=True,
    )

    name = subscriber.first_name or "there"

    body = (
        f"Hello {name},\n\n"
        "Thank you for subscribing to The Uncharted Route.\n\n"
        "Please confirm your email address using this link:\n"
        f"{verification_url}\n\n"
        "You will not receive marketing emails until you verify your address.\n\n"
        "The Uncharted Route\n"
        "Explore. Experience. Remember."
    )

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <body style="margin:0;padding:24px;background:#F7F1E5;
                 color:#1C2822;font-family:Arial,sans-serif;">
        <div style="max-width:600px;margin:auto;background:#FFFFFF;
                    padding:32px;border-radius:12px;">
            <h2 style="color:#12372A;">Confirm your subscription</h2>
            <p>Hello {name},</p>
            <p>
                Thank you for subscribing to The Uncharted Route.
                Please confirm your email address to activate your
                newsletter subscription.
            </p>
            <p>
                <a href="{verification_url}"
                   style="display:inline-block;padding:12px 20px;
                          background:#D89B24;color:#12372A;
                          text-decoration:none;border-radius:6px;
                          font-weight:bold;">
                    Confirm my email
                </a>
            </p>
            <p style="color:#66736B;font-size:13px;">
                If you did not request this subscription, you can ignore
                this email.
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
    """

    return email_service.send_email(
        recipient=subscriber.email,
        subject="Confirm your newsletter subscription | The Uncharted Route",
        body=body,
        html_body=html_body,)

@public_newsletter_bp.route("/", methods=["GET", "POST"])
def signup():
    """Display the public newsletter signup page."""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        first_name = (request.form.get("first_name") or "").strip()
        last_name = (request.form.get("last_name") or "").strip()
        country = (request.form.get("country") or "").strip()

        consent = request.form.get("marketing_consent") == "y"

        if not email or "@" not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template("newsletter/signup.html")

        if not consent:
            flash(
                "Please confirm your consent to receive the selected "
                "newsletter categories.",
                "warning",
            )
            return render_template("newsletter/signup.html")

        subscriber = NewsletterSubscriber.query.filter_by(
            email=email
        ).first()

        preferences = {
            "receive_promotions": request.form.get("receive_promotions") == "y",
            "receive_new_experiences": (
                request.form.get("receive_new_experiences") == "y"
            ),
            "receive_blog_updates": (
                request.form.get("receive_blog_updates") == "y"
            ),
            "receive_company_news": (
                request.form.get("receive_company_news") == "y"
            ),
        }

        if not any(preferences.values()):
            flash(
                "Please select at least one newsletter category.",
                "warning",
            )
            return render_template("newsletter/signup.html")

        now = datetime.utcnow()

        if subscriber is None:
            subscriber = NewsletterSubscriber(
                email=email,
                first_name=first_name or None,
                last_name=last_name or None,
                country=country or None,
                source="Website Newsletter",
            )
            db.session.add(subscriber)

        subscriber.first_name = first_name or subscriber.first_name
        subscriber.last_name = last_name or subscriber.last_name
        subscriber.country = country or subscriber.country

        subscriber.subscribed = True
        subscriber.marketing_consent = True
        subscriber.consent_date = now
        subscriber.unsubscribed_at = None

        for field, value in preferences.items():
            setattr(subscriber, field, value)

        # Require confirmation for a new subscription or a re-subscription.
        if not subscriber.verified or not subscriber.verification_token:
            subscriber.verified = False
            subscriber.verification_token = uuid.uuid4().hex

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to save public newsletter subscription."
            )
            flash(
                "We couldn't process your subscription right now. "
                "Please try again.",
                "danger",
            )
            return render_template("newsletter/signup.html")

        if not subscriber.verified:
            try:
                sent = _send_verification_email(subscriber)
                if not sent:
                    current_app.logger.error(
                        "Newsletter verification email failed for %s.",
                        subscriber.email,
                    )
            except Exception:
                current_app.logger.exception(
                    "Newsletter verification email failed for %s.",
                    subscriber.email,
                )

            flash(
                "Please check your inbox for a verification email. "
                "Your subscription will activate after you confirm.",
                "success",)
        else:
            flash("Your newsletter preferences have been updated.","success",)

        return redirect(url_for("public_newsletter.signup"))
    return render_template("newsletter/signup.html")

@public_newsletter_bp.route("/verify/<token>")
def verify(token):
    """Verify a subscriber's email address."""
    subscriber = NewsletterSubscriber.query.filter_by(
        verification_token=token,
        subscribed=True,
        marketing_consent=True,).first()

    if subscriber is None:
        flash(
            "That verification link is invalid or has already been used.",
            "warning",)
        return redirect(url_for("public_newsletter.signup"))

    subscriber.verified = True
    subscriber.verification_token = None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to verify newsletter subscriber.")
        flash("We couldn't verify your subscription right now. Please try again.","danger",)
        return redirect(url_for("public_newsletter.signup"))

    flash("Your email has been verified. Thank you for subscribing!","success",)
    return redirect(url_for("public_newsletter.signup"))

# =============================================================================
# Newsletter Unsubscribe
# =============================================================================
@public_newsletter_bp.route("/unsubscribe/<token>", methods=["GET", "POST"])
def unsubscribe(token):
    """Unsubscribe a recipient from marketing newsletters."""

    serializer = URLSafeSerializer(
        current_app.secret_key,
        salt="tur-newsletter-unsubscribe-v1",)

    try:
        payload = serializer.loads(token)
    except BadSignature:
        flash(
            "This unsubscribe link is invalid. Please contact us for help.",
            "warning",)
        return redirect(url_for("public_newsletter.signup"))

    subscriber_id = payload.get("subscriber_id")

    if not subscriber_id:
        flash("This unsubscribe link is invalid.", "warning")
        return redirect(url_for("public_newsletter.signup"))

    subscriber = db.session.get(NewsletterSubscriber, subscriber_id)

    if subscriber is None:
        flash(
            "We couldn't find the subscription associated with this link.",
            "warning",
        )
        return redirect(url_for("public_newsletter.signup"))

    if not subscriber.subscribed and not subscriber.marketing_consent:
        flash(
            "This email address is already unsubscribed.",
            "info",
        )
        return redirect(url_for("public_newsletter.signup"))

    subscriber.subscribed = False
    subscriber.marketing_consent = False
    subscriber.unsubscribed_at = datetime.utcnow()
    subscriber.unsubscribe_reason = "Unsubscribed using email link"
    subscriber.verification_token = None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to unsubscribe newsletter subscriber ID %s.",
            subscriber.id,
        )
        flash(
            "We couldn't process your request right now. Please try again.",
            "danger",
        )
        return redirect(url_for("public_newsletter.signup"))

    flash(
        "You have been unsubscribed from The Uncharted Route marketing emails.",
        "success",
    )
    return redirect(url_for("public_newsletter.signup"))


# =============================================================================
# Newsletter Open Tracking
# =============================================================================
@public_newsletter_bp.route("/track/open/<token>")
def track_open(token):
    """Record a newsletter tracking-pixel request."""

    pixel = base64.b64decode(
        "R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="
    )

    serializer = URLSafeSerializer(
        current_app.secret_key,
        salt="tur-newsletter-tracking-v1",
    )

    try:
        payload = serializer.loads(token)
        subscriber_id = payload.get("subscriber_id")

        if subscriber_id:
            subscriber = db.session.get(
                NewsletterSubscriber,
                subscriber_id,
            )

            if subscriber is not None:
                subscriber.total_opens = (subscriber.total_opens or 0) + 1
                subscriber.last_opened = datetime.utcnow()
                db.session.commit()

    except BadSignature:
        pass
    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Newsletter open tracking failed."
        )

    return Response(
        pixel,
        mimetype="image/gif",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",},)

# =============================================================================
# Newsletter Click Tracking
# =============================================================================
@public_newsletter_bp.route("/track/click/<token>")
def track_click(token):
    """Record a newsletter link click and redirect to its destination."""

    serializer = URLSafeSerializer(
        current_app.secret_key,
        salt="tur-newsletter-tracking-v1",)

    try:
        payload = serializer.loads(token)
    except BadSignature:
        flash("This newsletter link is invalid or has expired.", "warning")
        return redirect(url_for("public_newsletter.signup"))

    destination = payload.get("url")
    subscriber_id = payload.get("subscriber_id")

    if not destination:
        return redirect(url_for("public_newsletter.signup"))

    from urllib.parse import urlparse

    parsed = urlparse(destination)

    # Never permit the tracking endpoint to redirect to unsafe schemes.
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        current_app.logger.warning(
            "Blocked invalid newsletter tracking destination."
        )
        return redirect(url_for("public_newsletter.signup"))

    try:
        if subscriber_id:
            subscriber = db.session.get(
                NewsletterSubscriber,
                subscriber_id,)

            if subscriber is not None:
                subscriber.total_clicks = (
                    subscriber.total_clicks or 0) + 1
                subscriber.last_clicked = datetime.utcnow()
                db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Newsletter click tracking failed.")

    return redirect(destination)