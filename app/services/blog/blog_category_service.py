"""
===============================================================================
The Uncharted Route
Blog Category Service
===============================================================================

Business logic and database operations for BlogCategory.

Responsibilities:

    • Create blog categories
    • Retrieve blog categories
    • Search categories
    • Manage featured categories
    • Manage active/inactive categories
    • Manage category ordering
    • Retrieve categories with posts
    • Update categories
    • Delete categories safely
    • Provide category statistics
"""

import re

from extensions import db
from app.models import BlogCategory, BlogPost


# =============================================================================
# Blog Category Service
# =============================================================================

class BlogCategoryService:
    """
    Service layer for BlogCategory operations.
    """

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    @staticmethod
    def _normalize_name(name):
        """
        Normalize a category name.
        """

        if name is None:
            return None

        return " ".join(
            str(name).strip().split()
        )

    @staticmethod
    def _normalize_slug(slug):
        """
        Normalize a category slug.
        """

        if not slug:
            return None

        slug = str(slug).strip().lower()

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            slug
        )

        slug = re.sub(
            r"-+",
            "-",
            slug
        )

        return slug.strip("-")

    @staticmethod
    def _generate_slug(name):
        """
        Generate a URL-friendly slug from a category name.
        """

        return BlogCategoryService._normalize_slug(name)

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_category(
        name,
        slug=None,
        description=None,
        icon=None,
        color="#14B8A6",
        banner_image=None,
        meta_title=None,
        meta_description=None,
        meta_keywords=None,
        featured=False,
        active=True,
        sort_order=0
    ):
        """
        Create a new blog category.
        """

        name = BlogCategoryService._normalize_name(name)

        if not name:
            raise ValueError(
                "Category name is required."
            )

        if not slug:
            slug = BlogCategoryService._generate_slug(name)

        slug = BlogCategoryService._normalize_slug(slug)

        if not slug:
            raise ValueError(
                "A valid category slug is required."
            )

        # ---------------------------------------------------------------------
        # Duplicate Name
        # ---------------------------------------------------------------------

        existing_name = BlogCategory.query.filter(
            db.func.lower(BlogCategory.name) == name.lower()
        ).first()

        if existing_name:
            raise ValueError(
                "A blog category with this name already exists."
            )

        # ---------------------------------------------------------------------
        # Duplicate Slug
        # ---------------------------------------------------------------------

        existing_slug = BlogCategory.query.filter_by(
            slug=slug
        ).first()

        if existing_slug:
            raise ValueError(
                "A blog category with this slug already exists."
            )

        # ---------------------------------------------------------------------
        # Create
        # ---------------------------------------------------------------------

        category = BlogCategory(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            color=color or "#14B8A6",
            banner_image=banner_image,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            featured=bool(featured),
            active=bool(active),
            sort_order=sort_order or 0
        )

        db.session.add(category)
        db.session.commit()

        return category

    # =========================================================================
    # Retrieve By ID
    # =========================================================================

    @staticmethod
    def get_by_id(category_id):
        """
        Retrieve a category by ID.
        """

        if not category_id:
            return None

        return db.session.get(
            BlogCategory,
            category_id
        )

    # =========================================================================
    # Retrieve By Slug
    # =========================================================================

    @staticmethod
    def get_by_slug(slug, active_only=False):
        """
        Retrieve a category by slug.
        """

        if not slug:
            return None

        query = BlogCategory.query.filter_by(
            slug=BlogCategoryService._normalize_slug(slug)
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.first()

    # =========================================================================
    # Retrieve By Name
    # =========================================================================

    @staticmethod
    def get_by_name(name, active_only=False):
        """
        Retrieve a category by name.
        """

        if not name:
            return None

        query = BlogCategory.query.filter(
            db.func.lower(BlogCategory.name) == name.strip().lower()
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.first()

    # =========================================================================
    # Get All
    # =========================================================================

    @staticmethod
    def get_all(
        active_only=False,
        featured_only=False
    ):
        """
        Return all blog categories.
        """

        query = BlogCategory.query

        if active_only:
            query = query.filter_by(
                active=True
            )

        if featured_only:
            query = query.filter_by(
                featured=True
            )

        return query.order_by(
            BlogCategory.sort_order.asc(),
            BlogCategory.name.asc()
        ).all()

    # =========================================================================
    # Search
    # =========================================================================

    @staticmethod
    def search(
        query_text=None,
        active_only=True,
        featured_only=False
    ):
        """
        Search blog categories.
        """

        query = BlogCategory.query

        if query_text:
            search_term = f"%{query_text.strip()}%"

            query = query.filter(
                db.or_(
                    BlogCategory.name.ilike(search_term),
                    BlogCategory.description.ilike(search_term),
                    BlogCategory.slug.ilike(search_term)
                )
            )

        if active_only:
            query = query.filter_by(
                active=True
            )

        if featured_only:
            query = query.filter_by(
                featured=True
            )

        return query.order_by(
            BlogCategory.sort_order.asc(),
            BlogCategory.name.asc()
        ).all()

    # =========================================================================
    # Featured Categories
    # =========================================================================

    @staticmethod
    def get_featured(active_only=True):
        """
        Return featured blog categories.
        """

        query = BlogCategory.query.filter_by(
            featured=True
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.order_by(
            BlogCategory.sort_order.asc(),
            BlogCategory.name.asc()
        ).all()

    # =========================================================================
    # Categories With Posts
    # =========================================================================

    @staticmethod
    def get_categories_with_posts(
        active_only=True,
        published_only=False
    ):
        """
        Return categories containing at least one post.
        """

        query = BlogCategory.query

        if active_only:
            query = query.filter_by(
                active=True
            )

        categories = query.order_by(
            BlogCategory.sort_order.asc(),
            BlogCategory.name.asc()
        ).all()

        if not published_only:
            return [
                category
                for category in categories
                if category.post_count > 0
            ]

        return [
            category
            for category in categories
            if category.posts.filter_by(
                status=BlogPost.STATUS_PUBLISHED
            ).count() > 0
        ]

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_category(
        category_id,
        **updates
    ):
        """
        Update an existing blog category.
        """

        category = BlogCategoryService.get_by_id(
            category_id
        )

        if not category:
            return None

        # ---------------------------------------------------------------------
        # Name
        # ---------------------------------------------------------------------

        if "name" in updates:

            name = BlogCategoryService._normalize_name(
                updates["name"]
            )

            if not name:
                raise ValueError(
                    "Category name cannot be empty."
                )

            duplicate_name = BlogCategory.query.filter(
                db.func.lower(BlogCategory.name) == name.lower(),
                BlogCategory.id != category.id
            ).first()

            if duplicate_name:
                raise ValueError(
                    "Another blog category with this name already exists."
                )

            updates["name"] = name

        # ---------------------------------------------------------------------
        # Slug
        # ---------------------------------------------------------------------

        if "slug" in updates:

            slug = BlogCategoryService._normalize_slug(
                updates["slug"]
            )

            if not slug:
                raise ValueError(
                    "Category slug cannot be empty."
                )

            duplicate_slug = BlogCategory.query.filter(
                BlogCategory.slug == slug,
                BlogCategory.id != category.id
            ).first()

            if duplicate_slug:
                raise ValueError(
                    "Another blog category with this slug already exists."
                )

            updates["slug"] = slug

        # ---------------------------------------------------------------------
        # Allowed Fields
        # ---------------------------------------------------------------------

        allowed_fields = {
            "name",
            "slug",
            "description",
            "icon",
            "color",
            "banner_image",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "featured",
            "active",
            "sort_order"
        }

        for field, value in updates.items():

            if field in allowed_fields:
                setattr(
                    category,
                    field,
                    value
                )

        db.session.commit()

        return category

    # =========================================================================
    # Activate
    # =========================================================================

    @staticmethod
    def activate(category_id):
        """
        Activate a blog category.
        """

        category = BlogCategoryService.get_by_id(
            category_id
        )

        if not category:
            return None

        category.active = True

        db.session.commit()

        return category

    # =========================================================================
    # Deactivate
    # =========================================================================

    @staticmethod
    def deactivate(category_id):
        """
        Deactivate a blog category without deleting it.
        """

        category = BlogCategoryService.get_by_id(
            category_id
        )

        if not category:
            return None

        category.active = False

        db.session.commit()

        return category

    # =========================================================================
    # Feature
    # =========================================================================

    @staticmethod
    def feature(category_id):
        """
        Mark a category as featured.
        """

        category = BlogCategoryService.get_by_id(
            category_id
        )

        if not category:
            return None

        category.featured = True

        db.session.commit()

        return category

    # =========================================================================
    # Unfeature
    # =========================================================================

    @staticmethod
    def unfeature(category_id):
        """
        Remove featured status.
        """

        category = BlogCategoryService.get_by_id(
            category_id
        )

        if not category:
            return None

        category.featured = False

        db.session.commit()

        return category

    # =========================================================================
    # Reorder
    # =========================================================================

    @staticmethod
    def update_sort_order(
        category_id,
        sort_order
    ):
        """
        Update category display order.
        """

        category = BlogCategoryService.get_by_id(
            category_id
        )

        if not category:
            return None

        if sort_order is None:
            raise ValueError(
                "Sort order is required."
            )

        if int(sort_order) < 0:
            raise ValueError(
                "Sort order cannot be negative."
            )

        category.sort_order = int(sort_order)

        db.session.commit()

        return category

    # =========================================================================
    # Count
    # =========================================================================

    @staticmethod
    def count(active_only=False):
        """
        Return the total number of categories.
        """

        query = BlogCategory.query

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.count()

    # =========================================================================
    # Statistics
    # =========================================================================

    @staticmethod
    def get_statistics():
        """
        Return blog category statistics.
        """

        total = BlogCategory.query.count()

        active = BlogCategory.query.filter_by(
            active=True
        ).count()

        inactive = BlogCategory.query.filter_by(
            active=False
        ).count()

        featured = BlogCategory.query.filter_by(
            featured=True
        ).count()

        active_featured = BlogCategory.query.filter_by(
            featured=True,
            active=True
        ).count()

        categories_with_posts = (
            BlogCategoryService.get_categories_with_posts(
                active_only=True
            )
        )

        total_posts = BlogPost.query.count()

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "featured": featured,
            "active_featured": active_featured,
            "categories_with_posts": len(
                categories_with_posts
            ),
            "empty_categories": max(
                0,
                active - len(categories_with_posts)
            ),
            "total_posts": total_posts
        }

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete(category_id):
        """
        Permanently delete a blog category.

        A category cannot be deleted while blog posts are assigned to it.
        This prevents accidental loss of blog content.
        """

        category = BlogCategoryService.get_by_id(
            category_id
        )

        if not category:
            return False

        post_count = category.post_count

        if post_count > 0:
            raise ValueError(
                "This category cannot be deleted because "
                f"{post_count} blog post(s) are assigned to it. "
                "Move or delete those posts first."
            )

        db.session.delete(category)
        db.session.commit()

        return True

    # =========================================================================
    # Bulk Status
    # =========================================================================

    @staticmethod
    def bulk_set_active(
        category_ids,
        active=True
    ):
        """
        Activate or deactivate multiple categories.
        """

        if not category_ids:
            return 0

        categories = BlogCategory.query.filter(
            BlogCategory.id.in_(category_ids)
        ).all()

        for category in categories:
            category.active = bool(active)

        db.session.commit()

        return len(categories)