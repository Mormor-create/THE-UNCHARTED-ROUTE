"""Add legal and help CMS

Revision ID: 068608e7ce3a
Revises: e9c5b13abbde
Create Date: 2026-11-10 14:38:23.296565

"""

from alembic import op
import sqlalchemy as sa


# =============================================================================
# Revision identifiers, used by Alembic.
# =============================================================================

revision = "068608e7ce3a"
down_revision = "e9c5b13abbde"
branch_labels = None
depends_on = None


# =============================================================================
# Upgrade
# =============================================================================

def upgrade():
    """
    Create the current Legal & Help CMS architecture.

    Current architecture:

        faqs
            Dedicated FAQ content.

        legal_help_pages
            Top-level managed pages such as:
                - about
                - faq
                - privacy
                - terms

        legal_help_sections
            Structured content sections belonging to a page.

        legal_help_items
            Individual cards, FAQ entries, legal sections, etc.
            belonging to a LegalHelpSection.

    The previous Legal CMS architecture using:

        legal_pages
        legal_page_sections

    is intentionally NOT created.
    """

    # -------------------------------------------------------------------------
    # FAQs
    # -------------------------------------------------------------------------

    op.create_table(
        "faqs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "question",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "answer",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("faqs", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_faqs_active"),
            ["active"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_faqs_category"),
            ["category"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_faqs_sort_order"),
            ["sort_order"],
            unique=False,
        )

    # -------------------------------------------------------------------------
    # Legal & Help Pages
    # -------------------------------------------------------------------------

    op.create_table(
        "legal_help_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "slug",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "page_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "eyebrow",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "intro",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "meta_title",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "meta_description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("legal_help_pages", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_legal_help_pages_active"),
            ["active"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_legal_help_pages_page_type"),
            ["page_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_legal_help_pages_slug"),
            ["slug"],
            unique=True,
        )

    # -------------------------------------------------------------------------
    # Legal & Help Sections
    # -------------------------------------------------------------------------

    op.create_table(
        "legal_help_sections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "page_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "section_key",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "section_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "eyebrow",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "body",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "secondary_body",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "primary_cta_label",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "primary_cta_url",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "secondary_cta_label",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "secondary_cta_url",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(
            ["page_id"],
            ["legal_help_pages.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("legal_help_sections", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_legal_help_sections_active"),
            ["active"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_legal_help_sections_page_id"),
            ["page_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_legal_help_sections_section_key"),
            ["section_key"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_legal_help_sections_sort_order"),
            ["sort_order"],
            unique=False,
        )

    # -------------------------------------------------------------------------
    # Legal & Help Items
    # -------------------------------------------------------------------------

    op.create_table(
        "legal_help_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "section_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "item_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "eyebrow",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "body",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "link_label",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "link_url",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(
            ["section_id"],
            ["legal_help_sections.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("legal_help_items", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_legal_help_items_active"),
            ["active"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_legal_help_items_section_id"),
            ["section_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_legal_help_items_sort_order"),
            ["sort_order"],
            unique=False,
        )


# =============================================================================
# Downgrade
# =============================================================================

def downgrade():
    """
    Remove the current Legal & Help CMS architecture.

    This intentionally removes only the tables created by this migration.
    It does not modify staff scheduling, bookings, or any unrelated tables.
    """

    # -------------------------------------------------------------------------
    # Legal & Help Items
    # -------------------------------------------------------------------------

    with op.batch_alter_table(
        "legal_help_items",
        schema=None,
    ) as batch_op:
        batch_op.drop_index(
            batch_op.f("ix_legal_help_items_sort_order")
        )
        batch_op.drop_index(
            batch_op.f("ix_legal_help_items_section_id")
        )
        batch_op.drop_index(
            batch_op.f("ix_legal_help_items_active")
        )

    op.drop_table("legal_help_items")

    # -------------------------------------------------------------------------
    # Legal & Help Sections
    # -------------------------------------------------------------------------

    with op.batch_alter_table(
        "legal_help_sections",
        schema=None,
    ) as batch_op:
        batch_op.drop_index(
            batch_op.f("ix_legal_help_sections_sort_order")
        )
        batch_op.drop_index(
            batch_op.f("ix_legal_help_sections_section_key")
        )
        batch_op.drop_index(
            batch_op.f("ix_legal_help_sections_page_id")
        )
        batch_op.drop_index(
            batch_op.f("ix_legal_help_sections_active")
        )

    op.drop_table("legal_help_sections")

    # -------------------------------------------------------------------------
    # Legal & Help Pages
    # -------------------------------------------------------------------------

    with op.batch_alter_table(
        "legal_help_pages",
        schema=None,
    ) as batch_op:
        batch_op.drop_index(
            batch_op.f("ix_legal_help_pages_slug")
        )
        batch_op.drop_index(
            batch_op.f("ix_legal_help_pages_page_type")
        )
        batch_op.drop_index(
            batch_op.f("ix_legal_help_pages_active")
        )

    op.drop_table("legal_help_pages")

    # -------------------------------------------------------------------------
    # FAQs
    # -------------------------------------------------------------------------

    with op.batch_alter_table(
        "faqs",
        schema=None,
    ) as batch_op:
        batch_op.drop_index(
            batch_op.f("ix_faqs_sort_order")
        )
        batch_op.drop_index(
            batch_op.f("ix_faqs_category")
        )
        batch_op.drop_index(
            batch_op.f("ix_faqs_active")
        )

    op.drop_table("faqs")