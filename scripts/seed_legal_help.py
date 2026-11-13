"""
===============================================================================
The Uncharted Route
Seed Legal & Help CMS
===============================================================================

Seeds:

- FAQ
- Privacy Policy
- Terms & Conditions

FAQ:
- Existing 7 questions
- 3 additional questions

Usage:

    flask shell

or, if this script is wired into your normal scripts workflow:

    python scripts/seed_legal_help.py --dry-run
    python scripts/seed_legal_help.py --apply

The script is idempotent and will not duplicate existing records.
===============================================================================
"""
from __future__ import annotations

import argparse
import os
import sys

# =============================================================================
# Project root
# =============================================================================
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =============================================================================
# Flask application
# =============================================================================
from app import create_app
from extensions import db
from app.models.legal_help_page import LegalHelpPage
from app.models.legal_help_section import LegalHelpSection
from app.models.legal_help_item import LegalHelpItem

# =============================================================================
# DATA
# =============================================================================

PAGES = [

    # =========================================================================
    # FAQ
    # =========================================================================

    {
        "slug": "faq",
        "page_type": "faq",
        "eyebrow": "Help & Information",
        "title": "Frequently Asked Questions",
        "intro": (
            "Everything you need to know about planning, booking, "
            "and experiencing your journey with us."
        ),
        "meta_title": "Frequently Asked Questions",
        "meta_description": (
            "Find answers to common questions about experiences, bookings, "
            "travel, payments, cancellations, and travelling with "
            "{{ config.COMPANY_NAME }}."
        ),
        "sections": [

            {
                "section_key": "hero",
                "section_type": "hero",
                "sort_order": 10,
                "eyebrow": "Help & Information",
                "title": "Frequently Asked Questions",
                "body": (
                    "Everything you need to know about planning, booking, "
                    "and experiencing your journey with "
                    "{{ config.COMPANY_NAME }}."
                ),
            },

            {
                "section_key": "faq",
                "section_type": "faq",
                "sort_order": 20,
                "title": "Frequently Asked Questions",
                "items": [

                    {
                        "item_type": "faq",
                        "sort_order": 10,
                        "title": "How do I book an experience?",
                        "body": (
                            "You can begin by exploring our experiences and "
                            "selecting the journey that interests you. From "
                            "there, you can contact us to discuss availability, "
                            "dates, group size, preferences, and any custom "
                            "requirements."
                        ),
                    },

                    {
                        "item_type": "faq",
                        "sort_order": 20,
                        "title": "Can you create a custom journey?",
                        "body": (
                            "Absolutely. Many of our journeys can be tailored "
                            "around your interests, schedule, group size, "
                            "accommodation preferences, and desired level "
                            "of comfort."
                        ),
                    },

                    {
                        "item_type": "faq",
                        "sort_order": 30,
                        "title": "What does the price of an experience include?",
                        "body": (
                            "Inclusions vary by experience. Each experience "
                            "page provides information about what is included "
                            "and what may be arranged as an optional add-on."
                        ),
                    },

                    {
                        "item_type": "faq",
                        "sort_order": 40,
                        "title": "How do payments work?",
                        "body": (
                            "Payment arrangements depend on the experience "
                            "and booking. Your booking confirmation will "
                            "provide the applicable payment instructions, "
                            "deadlines, and conditions."
                        ),
                    },

                    {
                        "item_type": "faq",
                        "sort_order": 50,
                        "title": "What is your cancellation policy?",
                        "body": (
                            "Cancellation terms may vary depending on the "
                            "experience, suppliers involved, accommodation, "
                            "transport, and timing. Please review the "
                            "cancellation conditions provided with your "
                            "booking before confirming."
                        ),
                    },

                    {
                        "item_type": "faq",
                        "sort_order": 60,
                        "title": "Are your experiences suitable for everyone?",
                        "body": (
                            "Experiences differ in duration, accessibility, "
                            "physical requirements, and difficulty. Please "
                            "review the individual experience information "
                            "and let us know about any relevant requirements "
                            "before booking."
                        ),
                    },

                    {
                        "item_type": "faq",
                        "sort_order": 70,
                        "title": (
                            "I have another question. How can I contact you?"
                        ),
                        "body": (
                            "We'd be happy to help. Send us an enquiry "
                            "through our contact page and tell us what "
                            "you're planning."
                        ),
                        "link_label": "Contact Us",
                        "link_url": "/contact",
                    },

                    # =========================================================
                    # NEW FAQ 1
                    # =========================================================

                    {
                        "item_type": "faq",
                        "sort_order": 80,
                        "title": "How far in advance should I enquire?",
                        "body": (
                            "There is no single rule because every journey is "
                            "different. We recommend contacting us as early "
                            "as possible for journeys involving accommodation, "
                            "special arrangements, peak travel periods, or "
                            "larger groups. Last-minute enquiries may also "
                            "be possible depending on availability."
                        ),
                    },

                    # =========================================================
                    # NEW FAQ 2
                    # =========================================================

                    {
                        "item_type": "faq",
                        "sort_order": 90,
                        "title": "Can you help with accommodation?",
                        "body": (
                            "Yes. Where accommodation forms part of your "
                            "journey, we can help identify suitable stays "
                            "based on your destination, preferences, group "
                            "size, style of travel, and budget. Accommodation "
                            "is confirmed separately according to property "
                            "availability."
                        ),
                    },

                    # =========================================================
                    # NEW FAQ 3
                    # =========================================================

                    {
                        "item_type": "faq",
                        "sort_order": 100,
                        "title": "What should I tell you when making an enquiry?",
                        "body": (
                            "It helps to tell us your preferred destination "
                            "or experience, approximate travel dates, number "
                            "of travellers, interests, accommodation "
                            "preferences, and anything important to your "
                            "journey. If you are still deciding, that is "
                            "completely fine — we can help you shape the route."
                        ),
                    },

                ],
            },

            {
                "section_key": "final_cta",
                "section_type": "cta",
                "sort_order": 30,
                "eyebrow": "Still Planning?",
                "title": "Let's talk about your journey.",
                "body": (
                    "If you can't find the answer you're looking for, "
                    "our team can help you plan the details."
                ),
                "primary_cta_label": "Get in Touch",
                "primary_cta_url": "/contact",
            },
        ],
    },


    # =========================================================================
    # PRIVACY
    # =========================================================================

    {
        "slug": "privacy",
        "page_type": "privacy",
        "eyebrow": "Legal",
        "title": "Privacy Policy",
        "intro": (
            "How we handle information provided through our website and services."
        ),
        "meta_title": "Privacy Policy",
        "meta_description": (
            "Read the Privacy Policy for {{ config.COMPANY_NAME }} and learn "
            "how information is collected, used, stored, and protected."
        ),
        "sections": [

            {
                "section_key": "hero",
                "section_type": "hero",
                "sort_order": 10,
                "eyebrow": "Legal",
                "title": "Privacy Policy",
                "body": (
                    "How {{ config.COMPANY_NAME }} handles information "
                    "provided through our website and services."
                ),
            },

            {
                "section_key": "privacy_content",
                "section_type": "legal",
                "sort_order": 20,
                "title": "Privacy Policy",
                "items": [

                    {
                        "item_type": "legal",
                        "sort_order": 10,
                        "title": "Introduction",
                        "body": (
                            "{{ config.COMPANY_NAME }} respects your privacy "
                            "and is committed to handling personal information "
                            "responsibly. This Privacy Policy explains how "
                            "information may be collected and used when you "
                            "interact with our website, make an enquiry, or "
                            "use our services."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 20,
                        "title": "Information We Collect",
                        "body": (
                            "Depending on how you interact with us, we may "
                            "collect information such as your name, contact "
                            "details, country, company information, enquiry "
                            "details, booking information, and other "
                            "information that you voluntarily provide."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 30,
                        "title": "How We Use Information",
                        "body": (
                            "Information may be used to respond to enquiries, "
                            "arrange requested services, communicate with you, "
                            "improve our website and services, maintain "
                            "business records, and meet applicable legal or "
                            "operational requirements."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 40,
                        "title": "Communications",
                        "body": (
                            "Where you choose to receive communications from "
                            "us, we may use the information you provide to "
                            "send relevant updates, information, or marketing "
                            "communications. You may opt out of marketing "
                            "communications where applicable."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 50,
                        "title": "Information Sharing",
                        "body": (
                            "We may need to share relevant information with "
                            "trusted service providers, suppliers, partners, "
                            "or authorities where necessary to provide "
                            "requested services, operate our business, or "
                            "comply with applicable law."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 60,
                        "title": "Data Security",
                        "body": (
                            "We take reasonable measures to protect information "
                            "against unauthorized access, misuse, loss, or "
                            "disclosure. However, no online system can be "
                            "guaranteed to be completely secure."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 70,
                        "title": "Your Rights",
                        "body": (
                            "Depending on applicable law, you may have rights "
                            "relating to the personal information we hold "
                            "about you, including rights to access, correction, "
                            "objection, restriction, or deletion."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 80,
                        "title": "Contact",
                        "body": (
                            "If you have questions about this Privacy Policy "
                            "or how your information is handled, please "
                            "contact us."
                        ),
                        "link_label": "Contact Us",
                        "link_url": "/contact",
                    },

                ],
            },
        ],
    },


    # =========================================================================
    # TERMS
    # =========================================================================

    {
        "slug": "terms",
        "page_type": "terms",
        "eyebrow": "Legal",
        "title": "Terms & Conditions",
        "intro": (
            "The terms governing your use of our website and engagement with us."
        ),
        "meta_title": "Terms & Conditions",
        "meta_description": (
            "Read the Terms and Conditions governing use of the "
            "{{ config.COMPANY_NAME }} website and services."
        ),
        "sections": [

            {
                "section_key": "hero",
                "section_type": "hero",
                "sort_order": 10,
                "eyebrow": "Legal",
                "title": "Terms & Conditions",
                "body": (
                    "The terms governing your use of our website and "
                    "engagement with {{ config.COMPANY_NAME }}."
                ),
            },

            {
                "section_key": "terms_content",
                "section_type": "legal",
                "sort_order": 20,
                "title": "Terms & Conditions",
                "items": [

                    {
                        "item_type": "legal",
                        "sort_order": 10,
                        "title": "About These Terms",
                        "body": (
                            "These Terms & Conditions govern your use of the "
                            "{{ config.COMPANY_NAME }} website and your "
                            "interaction with our travel and experience "
                            "services."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 20,
                        "title": "Website Use",
                        "body": (
                            "You agree to use this website lawfully and "
                            "responsibly. You must not misuse the website, "
                            "interfere with its operation, attempt "
                            "unauthorized access, or use the website for "
                            "unlawful purposes."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 30,
                        "title": "Experiences & Availability",
                        "body": (
                            "Experiences displayed on the website may be "
                            "subject to availability, seasonal conditions, "
                            "supplier availability, weather, conservation "
                            "requirements, and operational considerations."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 40,
                        "title": "Pricing",
                        "body": (
                            "Prices displayed on the website may change. "
                            "The applicable price, inclusions, exclusions, "
                            "taxes, fees, and payment requirements will be "
                            "confirmed as part of the booking process."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 50,
                        "title": "Bookings & Payments",
                        "body": (
                            "A booking is subject to availability and "
                            "confirmation. Payment requirements and deadlines "
                            "may vary depending on the experience and "
                            "services involved."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 60,
                        "title": "Cancellations & Changes",
                        "body": (
                            "Cancellation, amendment, refund, and rescheduling "
                            "conditions may vary by experience and supplier. "
                            "The conditions applicable to your booking will "
                            "be communicated during the booking process."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 70,
                        "title": "Travel Responsibilities",
                        "body": (
                            "Travellers are responsible for providing accurate "
                            "information, following reasonable instructions, "
                            "carrying appropriate documentation, and meeting "
                            "any applicable entry, health, insurance, or other "
                            "travel requirements."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 80,
                        "title": "Third-Party Services",
                        "body": (
                            "Some journeys may involve accommodation providers, "
                            "transport operators, guides, attractions, "
                            "conservation organizations, or other third "
                            "parties. Their own terms and conditions may "
                            "also apply."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 90,
                        "title": "Changes to These Terms",
                        "body": (
                            "We may update these Terms & Conditions from "
                            "time to time. Updated terms will be published "
                            "on this website where appropriate."
                        ),
                    },

                    {
                        "item_type": "legal",
                        "sort_order": 100,
                        "title": "Contact",
                        "body": (
                            "If you have questions regarding these terms "
                            "or a booking, please contact our team."
                        ),
                        "link_label": "Contact Us",
                        "link_url": "/contact",
                    },

                ],
            },
        ],
    },

]


# =============================================================================
# HELPERS
# =============================================================================

def create_or_update_page(page_data, apply=False):
    slug = page_data["slug"]

    page = LegalHelpPage.query.filter_by(
        slug=slug
    ).first()

    if page:
        action = "UPDATE"
    else:
        action = "CREATE"

    print(
        f"{action}: page '{slug}' "
        f"({page_data['title']})"
    )

    if not apply:
        return

    if not page:
        page = LegalHelpPage(
            slug=slug,
        )
        db.session.add(page)

    page.page_type = page_data["page_type"]
    page.eyebrow = page_data.get("eyebrow")
    page.title = page_data["title"]
    page.intro = page_data.get("intro")
    page.meta_title = page_data.get("meta_title")
    page.meta_description = page_data.get(
        "meta_description"
    )
    page.active = True

    db.session.flush()

    for section_data in page_data.get("sections", []):

        section = LegalHelpSection.query.filter_by(
            page_id=page.id,
            section_key=section_data["section_key"],
        ).first()

        if section:
            section_action = "UPDATE"
        else:
            section_action = "CREATE"

        print(
            f"  {section_action}: section "
            f"'{section_data['section_key']}'"
        )

        if not apply:
            continue

        if not section:
            section = LegalHelpSection(
                page_id=page.id,
                section_key=section_data["section_key"],
            )
            db.session.add(section)

        section.section_type = section_data[
            "section_type"
        ]
        section.eyebrow = section_data.get("eyebrow")
        section.title = section_data.get("title")
        section.body = section_data.get("body")
        section.secondary_body = section_data.get(
            "secondary_body"
        )
        section.primary_cta_label = section_data.get(
            "primary_cta_label"
        )
        section.primary_cta_url = section_data.get(
            "primary_cta_url"
        )
        section.secondary_cta_label = section_data.get(
            "secondary_cta_label"
        )
        section.secondary_cta_url = section_data.get(
            "secondary_cta_url"
        )
        section.sort_order = section_data.get(
            "sort_order",
            0,
        )
        section.active = True

        db.session.flush()

        for item_data in section_data.get(
            "items",
            [],
        ):

            item = LegalHelpItem.query.filter_by(
                section_id=section.id,
                sort_order=item_data["sort_order"],
            ).first()

            if item:
                item_action = "UPDATE"
            else:
                item_action = "CREATE"

            print(
                f"    {item_action}: "
                f"'{item_data['title']}'"
            )

            if not apply:
                continue

            if not item:
                item = LegalHelpItem(
                    section_id=section.id,
                    sort_order=item_data[
                        "sort_order"
                    ],
                )
                db.session.add(item)

            item.item_type = item_data[
                "item_type"
            ]
            item.eyebrow = item_data.get(
                "eyebrow"
            )
            item.title = item_data[
                "title"
            ]
            item.body = item_data.get(
                "body"
            )
            item.link_label = item_data.get(
                "link_label"
            )
            item.link_url = item_data.get(
                "link_url"
            )
            item.active = True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Seed Legal & Help CMS content."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to the database.",
    )

    args = parser.parse_args()

    app = create_app()

    with app.app_context():

        print()
        print("=" * 79)
        print("THE UNCHARTED ROUTE")
        print("Legal & Help CMS Seed")
        print("=" * 79)
        print()

        if args.apply:
            print("MODE: APPLY")
        else:
            print("MODE: DRY RUN")
            print(
                "No database changes will be committed."
            )

        print()

        for page_data in PAGES:
            create_or_update_page(
                page_data,
                apply=args.apply,
            )

        if args.apply:
            db.session.commit()

            print()
            print("=" * 79)
            print("SEED COMPLETE")
            print("=" * 79)
        else:
            print()
            print("=" * 79)
            print("DRY RUN COMPLETE")
            print("Run with --apply to write the content.")
            print("=" * 79)


if __name__ == "__main__":
    main()