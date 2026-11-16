
"""Create missing site settings table.

Revision ID: 4e4a9ac52cc9
Revises: 7b6204ebc853
"""

from alembic import op
import sqlalchemy as sa


revision = "4e4a9ac52cc9"
down_revision = "7b6204ebc853"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # Preserve an existing table if one is already present.
    if sa.inspect(bind).has_table("site_settings"):
        return

    op.create_table(
        "site_settings",

        sa.Column("id", sa.Integer(), primary_key=True),

        # Website identity
        sa.Column("site_name", sa.String(150), nullable=False),
        sa.Column("tagline", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("logo", sa.String(255)),
        sa.Column("favicon", sa.String(255)),

        # Contact information
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(100)),
        sa.Column("whatsapp", sa.String(100)),
        sa.Column("address", sa.Text()),
        sa.Column("city", sa.String(100)),
        sa.Column("country", sa.String(100)),

        # Business information
        sa.Column("business_name", sa.String(255)),
        sa.Column("registration_number", sa.String(150)),
        sa.Column("tax_number", sa.String(150)),
        sa.Column("business_email", sa.String(255)),
        sa.Column("business_phone", sa.String(100)),

        # Social media
        sa.Column("facebook_url", sa.String(500)),
        sa.Column("instagram_url", sa.String(500)),
        sa.Column("twitter_url", sa.String(500)),
        sa.Column("youtube_url", sa.String(500)),
        sa.Column("linkedin_url", sa.String(500)),
        sa.Column("tiktok_url", sa.String(500)),

        # Homepage
        sa.Column("homepage_title", sa.String(255)),
        sa.Column("homepage_subtitle", sa.String(500)),
        sa.Column("homepage_description", sa.Text()),
        sa.Column("homepage_hero_image", sa.String(255)),
        sa.Column("homepage_hero_video", sa.String(500)),

        # SEO
        sa.Column("meta_title", sa.String(255)),
        sa.Column("meta_description", sa.Text()),
        sa.Column("meta_keywords", sa.Text()),
        sa.Column("canonical_url", sa.String(500)),

        # Analytics
        sa.Column("google_analytics_id", sa.String(100)),
        sa.Column("google_tag_manager_id", sa.String(100)),
        sa.Column("facebook_pixel_id", sa.String(100)),

        # Booking configuration
        sa.Column(
            "booking_email",
            sa.String(255),
        ),
        sa.Column(
            "booking_phone",
            sa.String(100),
        ),
        sa.Column(
            "booking_enabled",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "online_payment_enabled",
            sa.Boolean(),
            nullable=False,
        ),

        # Newsletter
        sa.Column(
            "newsletter_enabled",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column("newsletter_email", sa.String(255)),

        # Website status
        sa.Column(
            "maintenance_mode",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column("maintenance_message", sa.Text()),

        # Display preferences
        sa.Column(
            "show_phone",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "show_email",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "show_social_links",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "show_booking_button",
            sa.Boolean(),
            nullable=False,
        ),

        # Footer
        sa.Column("footer_text", sa.Text()),
        sa.Column("copyright_text", sa.String(500)),

        # Audit
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
    )


def downgrade():
    # Intentionally non-destructive.
    # The table may have existed before this migration on legacy databases.
    # Do not risk deleting existing site configuration.
    pass
