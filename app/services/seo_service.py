"""
===============================================================================
The Uncharted Route
SEO Service
===============================================================================

Centralized SEO utilities for The Uncharted Route.

The SEO service provides reusable functionality for:

• SEO metadata generation
• Meta title generation
• Meta description generation
• Keyword handling
• Slug generation
• Canonical URL generation
• Open Graph metadata
• Twitter Card metadata
• Structured data helpers
• SEO validation
• Indexing controls
• Sitemap information

The service is designed to work across:

• Experiences
• Destinations
• Blog Posts
• Wildlife
• Categories
• Landing Pages
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional


# =============================================================================
# SEO Error
# =============================================================================

class SEOError(Exception):
    """
    Raised when an SEO operation cannot be completed.
    """

    pass


# =============================================================================
# SEO Service
# =============================================================================

class SEOService:
    """
    Centralized SEO management service.
    """

    # =========================================================================
    # Recommended SEO Limits
    # =========================================================================

    TITLE_MIN_LENGTH = 30
    TITLE_MAX_LENGTH = 60

    DESCRIPTION_MIN_LENGTH = 70
    DESCRIPTION_MAX_LENGTH = 160

    SLUG_MAX_LENGTH = 120

    # =========================================================================
    # Initialization
    # =========================================================================

    def __init__(
        self,
        site_name: str = "The Uncharted Route",
        default_description: str = (
            "Discover unforgettable journeys, wildlife experiences, "
            "coastal escapes, cultural adventures, and tailor-made "
            "travel experiences across Kenya and beyond."
        ),
        default_image: Optional[str] = None,
    ):
        self.site_name = site_name
        self.default_description = default_description
        self.default_image = default_image

    # =========================================================================
    # Text Helpers
    # =========================================================================

    @staticmethod
    def clean_text(
        value: Optional[str],
    ) -> str:
        """
        Normalize text for SEO usage.
        """

        if not value:
            return ""

        value = unicodedata.normalize(
            "NFKC",
            str(value),
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    @staticmethod
    def truncate(
        value: str,
        max_length: int,
    ) -> str:
        """
        Safely truncate text without cutting words where possible.
        """

        value = SEOService.clean_text(
            value
        )

        if len(value) <= max_length:
            return value

        truncated = value[:max_length].rsplit(
            " ",
            1,
        )[0]

        return truncated.rstrip(
            ".,;:!?-"
        ) + "..."

    # =========================================================================
    # Slugs
    # =========================================================================

    @staticmethod
    def generate_slug(
        value: str,
        max_length: int = SLUG_MAX_LENGTH,
    ) -> str:
        """
        Generate a URL-friendly slug.
        """

        if not value:
            raise SEOError(
                "Cannot generate a slug from empty text."
            )

        value = unicodedata.normalize(
            "NFKD",
            str(value),
        )

        value = value.encode(
            "ascii",
            "ignore",
        ).decode(
            "ascii"
        )

        value = value.lower()

        value = re.sub(
            r"[^a-z0-9]+",
            "-",
            value,
        )

        value = value.strip(
            "-"
        )

        value = value[:max_length]

        value = value.rstrip(
            "-"
        )

        if not value:
            raise SEOError(
                "Unable to generate a valid slug."
            )

        return value

    # =========================================================================
    # Title Generation
    # =========================================================================

    def generate_title(
        self,
        title: str,
        section: Optional[str] = None,
        include_site_name: bool = True,
    ) -> str:
        """
        Generate a page SEO title.
        """

        title = self.clean_text(
            title
        )

        if not title:
            title = self.site_name

        if section:
            section = self.clean_text(
                section
            )

            if section:
                title = (
                    f"{title} | {section}"
                )

        if include_site_name:
            if self.site_name.lower() not in title.lower():

                title = (
                    f"{title} | "
                    f"{self.site_name}"
                )

        return self.truncate(
            title,
            self.TITLE_MAX_LENGTH,
        )

    # =========================================================================
    # Description Generation
    # =========================================================================

    def generate_description(
        self,
        description: Optional[str] = None,
        fallback: Optional[str] = None,
    ) -> str:
        """
        Generate an SEO-friendly meta description.
        """

        description = self.clean_text(
            description
        )

        if not description:
            description = self.clean_text(
                fallback
            )

        if not description:
            description = self.default_description

        return self.truncate(
            description,
            self.DESCRIPTION_MAX_LENGTH,
        )

    # =========================================================================
    # Keyword Helpers
    # =========================================================================

    @staticmethod
    def normalize_keywords(
        keywords: Optional[Iterable[str] | str],
    ) -> List[str]:
        """
        Normalize SEO keywords and remove duplicates.
        """

        if not keywords:
            return []

        if isinstance(
            keywords,
            str,
        ):
            keywords = re.split(
                r"[,;|]",
                keywords,
            )

        normalized = []

        for keyword in keywords:

            keyword = SEOService.clean_text(
                keyword
            )

            if not keyword:
                continue

            keyword = keyword.lower()

            if keyword not in normalized:
                normalized.append(
                    keyword
                )

        return normalized

    @staticmethod
    def keywords_to_string(
        keywords: Optional[Iterable[str] | str],
    ) -> str:
        """
        Convert keywords to a comma-separated string.
        """

        return ", ".join(
            SEOService.normalize_keywords(
                keywords
            )
        )

    # =========================================================================
    # Canonical URLs
    # =========================================================================

    @staticmethod
    def build_canonical_url(
        base_url: str,
        path: str = "",
    ) -> str:
        """
        Build a normalized canonical URL.
        """

        base_url = str(
            base_url or ""
        ).rstrip(
            "/"
        )

        path = str(
            path or ""
        ).lstrip(
            "/"
        )

        if not path:
            return base_url

        return (
            f"{base_url}/{path}"
        )

    # =========================================================================
    # Indexing
    # =========================================================================

    @staticmethod
    def should_index(
        item: Any = None,
        default: bool = True,
    ) -> bool:
        """
        Determine whether a page/content object should be indexed.
        """

        if item is None:
            return default

        active = getattr(
            item,
            "active",
            None,
        )

        if active is False:
            return False

        status = getattr(
            item,
            "status",
            None,
        )

        if status is not None:
            if str(status).lower() != "published":
                return False

        return default

    @staticmethod
    def should_follow(
        item: Any = None,
        default: bool = True,
    ) -> bool:
        """
        Determine whether search engines should follow page links.
        """

        if item is None:
            return default

        return SEOService.should_index(
            item,
            default=default,
        )

    # =========================================================================
    # Open Graph
    # =========================================================================

    def generate_open_graph(
        self,
        title: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        image: Optional[str] = None,
        content_type: str = "website",
    ) -> Dict[str, Any]:
        """
        Generate Open Graph metadata.
        """

        return {
            "og:title": self.generate_title(
                title,
                include_site_name=True,
            ),
            "og:description": self.generate_description(
                description
            ),
            "og:url": url,
            "og:image": image or self.default_image,
            "og:type": content_type,
            "og:site_name": self.site_name,
        }

    # =========================================================================
    # Twitter Cards
    # =========================================================================

    def generate_twitter_card(
        self,
        title: str,
        description: Optional[str] = None,
        image: Optional[str] = None,
        card_type: str = "summary_large_image",
    ) -> Dict[str, Any]:
        """
        Generate Twitter/X card metadata.
        """

        return {
            "twitter:card": card_type,
            "twitter:title": self.generate_title(
                title,
                include_site_name=True,
            ),
            "twitter:description": self.generate_description(
                description
            ),
            "twitter:image": image or self.default_image,
        }

    # =========================================================================
    # General Metadata
    # =========================================================================

    def generate_metadata(
        self,
        title: str,
        description: Optional[str] = None,
        keywords: Optional[Iterable[str] | str] = None,
        canonical_url: Optional[str] = None,
        image: Optional[str] = None,
        content_type: str = "website",
        noindex: bool = False,
        nofollow: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate complete reusable SEO metadata.
        """

        normalized_title = self.generate_title(
            title
        )

        normalized_description = self.generate_description(
            description
        )

        normalized_keywords = self.normalize_keywords(
            keywords
        )

        metadata = {
            "title": normalized_title,
            "description": normalized_description,
            "keywords": normalized_keywords,
            "keywords_string": ", ".join(
                normalized_keywords
            ),
            "canonical_url": canonical_url,
            "robots": self.generate_robots(
                noindex=noindex,
                nofollow=nofollow,
            ),
            "open_graph": self.generate_open_graph(
                title=normalized_title,
                description=normalized_description,
                url=canonical_url,
                image=image,
                content_type=content_type,
            ),
            "twitter": self.generate_twitter_card(
                title=normalized_title,
                description=normalized_description,
                image=image,
            ),
        }

        return metadata

    # =========================================================================
    # Robots
    # =========================================================================

    @staticmethod
    def generate_robots(
        noindex: bool = False,
        nofollow: bool = False,
    ) -> str:
        """
        Generate a robots meta directive.
        """

        directives = []

        directives.append(
            "noindex"
            if noindex
            else "index"
        )

        directives.append(
            "nofollow"
            if nofollow
            else "follow"
        )

        return ", ".join(
            directives
        )

    # =========================================================================
    # Structured Data
    # =========================================================================

    def generate_article_schema(
        self,
        title: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        image: Optional[str] = None,
        author: Optional[str] = None,
        published_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate Article structured data.
        """

        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.clean_text(
                title
            ),
            "description": self.generate_description(
                description
            ),
        }

        if url:
            schema["url"] = url

        if image:
            schema["image"] = image

        if author:
            schema["author"] = {
                "@type": "Person",
                "name": author,
            }

        if published_at:
            schema["datePublished"] = published_at

        if updated_at:
            schema["dateModified"] = updated_at

        return schema

    def generate_breadcrumb_schema(
        self,
        breadcrumbs: Iterable[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Generate BreadcrumbList structured data.

        Each breadcrumb should contain:

        {
            "name": "Home",
            "url": "/"
        }
        """

        items = []

        for position, breadcrumb in enumerate(
            breadcrumbs,
            start=1,
        ):

            items.append(
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": breadcrumb.get(
                        "name",
                        "",
                    ),
                    "item": breadcrumb.get(
                        "url",
                        "",
                    ),
                }
            )

        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items,
        }

    def generate_organization_schema(
        self,
        name: Optional[str] = None,
        url: Optional[str] = None,
        logo: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate Organization structured data.
        """

        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": name or self.site_name,
        }

        if url:
            schema["url"] = url

        if logo:
            schema["logo"] = logo

        if description:
            schema["description"] = (
                self.clean_text(
                    description
                )
            )

        return schema

    def generate_tourism_business_schema(
        self,
        name: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        image: Optional[str] = None,
        telephone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate tourism business structured data.
        """

        schema = {
            "@context": "https://schema.org",
            "@type": "TravelAgency",
            "name": name or self.site_name,
        }

        if url:
            schema["url"] = url

        if description:
            schema["description"] = (
                self.clean_text(
                    description
                )
            )

        if image:
            schema["image"] = image

        if telephone:
            schema["telephone"] = telephone

        return schema

    # =========================================================================
    # Model-Based Metadata
    # =========================================================================

    def metadata_from_model(
        self,
        item: Any,
        content_type: str = "website",
        base_url: Optional[str] = None,
        path_prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate SEO metadata directly from a model instance.

        Supports the project's existing models such as:

        • Experience
        • BlogPost
        • Destination
        • WildlifeSpecies
        """

        title = (
            getattr(
                item,
                "meta_title",
                None,
            )
            or getattr(
                item,
                "title",
                None,
            )
            or getattr(
                item,
                "name",
                None,
            )
            or getattr(
                item,
                "common_name",
                None,
            )
            or self.site_name
        )

        description = (
            getattr(
                item,
                "meta_description",
                None,
            )
            or getattr(
                item,
                "excerpt",
                None,
            )
            or getattr(
                item,
                "short_description",
                None,
            )
            or getattr(
                item,
                "description",
                None,
            )
            or self.default_description
        )

        keywords = getattr(
            item,
            "meta_keywords",
            None,
        )

        slug = getattr(
            item,
            "slug",
            None,
        )

        canonical_url = getattr(
            item,
            "canonical_url",
            None,
        )

        if (
            not canonical_url
            and base_url
            and slug
        ):
            prefix = (
                path_prefix.strip("/")
                if path_prefix
                else content_type
            )

            canonical_url = self.build_canonical_url(
                base_url,
                f"{prefix}/{slug}",
            )

        image = (
            getattr(
                item,
                "social_image",
                None,
            )
            or getattr(
                item,
                "featured_image",
                None,
            )
            or self.default_image
        )

        return self.generate_metadata(
            title=title,
            description=description,
            keywords=keywords,
            canonical_url=canonical_url,
            image=image,
            content_type=content_type,
            noindex=not self.should_index(
                item
            ),
        )

    # =========================================================================
    # SEO Validation
    # =========================================================================

    def validate_title(
        self,
        title: Optional[str],
    ) -> Dict[str, Any]:
        """
        Validate an SEO title.
        """

        title = self.clean_text(
            title
        )

        errors = []
        warnings = []

        if not title:
            errors.append(
                "SEO title is missing."
            )

        elif len(title) < self.TITLE_MIN_LENGTH:
            warnings.append(
                "SEO title is shorter than recommended."
            )

        elif len(title) > self.TITLE_MAX_LENGTH:
            warnings.append(
                "SEO title exceeds the recommended length."
            )

        return {
            "valid": not errors,
            "length": len(title),
            "errors": errors,
            "warnings": warnings,
        }

    def validate_description(
        self,
        description: Optional[str],
    ) -> Dict[str, Any]:
        """
        Validate an SEO description.
        """

        description = self.clean_text(
            description
        )

        errors = []
        warnings = []

        if not description:
            errors.append(
                "Meta description is missing."
            )

        elif len(description) < self.DESCRIPTION_MIN_LENGTH:
            warnings.append(
                "Meta description is shorter than recommended."
            )

        elif len(description) > self.DESCRIPTION_MAX_LENGTH:
            warnings.append(
                "Meta description exceeds the recommended length."
            )

        return {
            "valid": not errors,
            "length": len(description),
            "errors": errors,
            "warnings": warnings,
        }

    def validate_model(
        self,
        item: Any,
    ) -> Dict[str, Any]:
        """
        Run SEO validation against a model.
        """

        title = (
            getattr(
                item,
                "meta_title",
                None,
            )
            or getattr(
                item,
                "title",
                None,
            )
            or getattr(
                item,
                "name",
                None,
            )
        )

        description = (
            getattr(
                item,
                "meta_description",
                None,
            )
            or getattr(
                item,
                "excerpt",
                None,
            )
            or getattr(
                item,
                "short_description",
                None,
            )
            or getattr(
                item,
                "description",
                None,
            )
        )

        title_validation = self.validate_title(
            title
        )

        description_validation = self.validate_description(
            description
        )

        errors = (
            title_validation["errors"]
            + description_validation["errors"]
        )

        warnings = (
            title_validation["warnings"]
            + description_validation["warnings"]
        )

        return {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "title": title_validation,
            "description": description_validation,
        }


# =============================================================================
# Service Instance
# =============================================================================

seo_service = SEOService()


# =============================================================================
# Convenience Functions
# =============================================================================

def generate_slug(
    value: str,
    max_length: int = SEOService.SLUG_MAX_LENGTH,
) -> str:
    """
    Generate a URL slug.
    """

    return seo_service.generate_slug(
        value,
        max_length=max_length,
    )


def generate_title(
    title: str,
    section: Optional[str] = None,
) -> str:
    """
    Generate an SEO title.
    """

    return seo_service.generate_title(
        title,
        section=section,
    )


def generate_description(
    description: Optional[str] = None,
    fallback: Optional[str] = None,
) -> str:
    """
    Generate an SEO description.
    """

    return seo_service.generate_description(
        description,
        fallback=fallback,
    )


def generate_metadata(
    title: str,
    description: Optional[str] = None,
    keywords: Optional[Iterable[str] | str] = None,
    canonical_url: Optional[str] = None,
    image: Optional[str] = None,
    content_type: str = "website",
) -> Dict[str, Any]:
    """
    Generate complete SEO metadata.
    """

    return seo_service.generate_metadata(
        title=title,
        description=description,
        keywords=keywords,
        canonical_url=canonical_url,
        image=image,
        content_type=content_type,
    )


def metadata_from_model(
    item: Any,
    content_type: str = "website",
    base_url: Optional[str] = None,
    path_prefix: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate metadata from a model.
    """

    return seo_service.metadata_from_model(
        item=item,
        content_type=content_type,
        base_url=base_url,
        path_prefix=path_prefix,
    )


def validate_model(
    item: Any,
) -> Dict[str, Any]:
    """
    Validate SEO fields on a model.
    """

    return seo_service.validate_model(
        item
    )