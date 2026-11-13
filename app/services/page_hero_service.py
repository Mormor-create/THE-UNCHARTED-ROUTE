"""
The Uncharted Route
Page Hero Service
"""
from sqlalchemy import or_
from extensions import db
from app.models.page_hero import PageHero
from app.models.media_asset import MediaAsset

class PageHeroService:
    """Business logic for PageHero CMS records."""

    @staticmethod
    def get_all(search=None, active=None):
        query = PageHero.query

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    PageHero.page_key.ilike(search_term),
                    PageHero.page_name.ilike(search_term),
                    PageHero.heading.ilike(search_term),
                )
            )

        if active is not None:
            query = query.filter(PageHero.active == active)

        return query.order_by(
            PageHero.display_order.asc(),
            PageHero.page_name.asc(),
        ).all()

    @staticmethod
    def get_by_id(hero_id):
        return db.session.get(PageHero, hero_id)

    @staticmethod
    def get_by_page_key(page_key):
        if not page_key:
            return None

        return PageHero.query.filter_by(
            page_key=page_key.strip().lower()
        ).first()

    @staticmethod
    def page_key_exists(page_key, exclude_id=None):
        if not page_key:
            return False

        query = PageHero.query.filter(
            PageHero.page_key == page_key.strip().lower()
        )

        if exclude_id is not None:
            query = query.filter(PageHero.id != exclude_id)

        return query.first() is not None

    @staticmethod
    def _clean(value):
        if value is None:
            return None

        value = value.strip()
        return value or None

    @staticmethod
    def _media_id(value):
        """Return a valid active image asset ID, or None."""
        if value in (None, "", 0, "0"):
            return None

        try:
            media_id = int(value)
        except (TypeError, ValueError):
            raise ValueError("Please select a valid Media Library image.")

        media = db.session.get(MediaAsset, media_id)

        if (
            media is None
            or not media.active
            or media.media_type != "image"
        ):
            raise ValueError(
                "The selected image is unavailable. "
                "Please choose another image from the Media Library."
            )

        return media.id

    @staticmethod
    def _form_values(form):
        """Prepare and validate values shared by create and update."""
        page_key = (form.page_key.data or "").strip().lower()

        return {
            "page_key": page_key,
            "page_name": (form.page_name.data or "").strip(),
            "eyebrow": PageHeroService._clean(form.eyebrow.data),
            "heading": (form.heading.data or "").strip(),
            "subheading": PageHeroService._clean(form.subheading.data),
            "desktop_media_id": PageHeroService._media_id(
                form.desktop_media_id.data
            ),
            "mobile_media_id": PageHeroService._media_id(
                form.mobile_media_id.data
            ),
            "overlay_style": form.overlay_style.data,
            "image_position": form.image_position.data,
            "primary_cta_text": PageHeroService._clean(
                form.primary_cta_text.data
            ),
            "primary_cta_url": PageHeroService._clean(
                form.primary_cta_url.data
            ),
            "secondary_cta_text": PageHeroService._clean(
                form.secondary_cta_text.data
            ),
            "secondary_cta_url": PageHeroService._clean(
                form.secondary_cta_url.data
            ),
            "active": bool(form.active.data),
            "display_order": (
                form.display_order.data
                if form.display_order.data is not None
                else 0
            ),
            "notes": PageHeroService._clean(form.notes.data),
        }

    @staticmethod
    def create(form):
        values = PageHeroService._form_values(form)

        if PageHeroService.page_key_exists(values["page_key"]):
            raise ValueError(
                f"A page hero already exists for '{values['page_key']}'."
            )

        hero = PageHero(**values)
        db.session.add(hero)
        db.session.commit()

        return hero

    @staticmethod
    def update(hero, form):
        values = PageHeroService._form_values(form)

        if PageHeroService.page_key_exists(
            values["page_key"],
            exclude_id=hero.id,
        ):
            raise ValueError(
                f"A page hero already exists for '{values['page_key']}'."
            )

        for field, value in values.items():
            setattr(hero, field, value)

        db.session.commit()
        return hero

    @staticmethod
    def delete(hero):
        """Delete the PageHero record without deleting its media assets."""
        db.session.delete(hero)
        db.session.commit()

    @staticmethod
    def toggle_active(hero):
        hero.active = not hero.active
        db.session.commit()
        return hero
