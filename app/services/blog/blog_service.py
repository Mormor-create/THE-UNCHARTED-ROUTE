"""
===============================================================================
The Uncharted Route
Blog Service
===============================================================================

Business logic and database operations for BlogPost.

Responsibilities:

    • Create blog posts
    • Retrieve blog posts
    • Search blog posts
    • Filter blog posts
    • Manage drafts
    • Manage review status
    • Schedule posts
    • Publish posts
    • Archive posts
    • Restore posts
    • Manage featured and pinned posts
    • Manage related experiences
    • Manage related destinations
    • Manage SEO information
    • Manage marketing CTAs
    • Track views, likes and shares
    • Manage newsletter/search indexing status
    • Calculate reading information
    • Duplicate posts
    • Provide statistics
    • Perform bulk actions
    • Delete posts
"""

import re
from datetime import datetime

from extensions import db
from app.models import BlogPost, BlogCategory


# =============================================================================
# Blog Service
# =============================================================================
class BlogService:
    """
    Service layer for BlogPost operations.
    """
    # =========================================================================
    # Internal Helpers
    # =========================================================================
    @staticmethod
    def _normalize_slug(slug):
        """
        Convert a slug into a URL-safe format.
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
    def _generate_slug(title):
        """
        Generate a slug from a blog post title.
        """

        return BlogService._normalize_slug(
            title
        )

    @staticmethod
    def _validate_status(status):
        """
        Validate a blog post status.
        """

        if status not in BlogPost.STATUSES:
            raise ValueError(
                f"Invalid blog post status: {status}"
            )

    @staticmethod
    def _validate_category(category_id):
        """
        Ensure the selected category exists.
        """

        if not category_id:
            raise ValueError(
                "Blog category is required."
            )

        category = db.session.get(
            BlogCategory,
            category_id
        )

        if not category:
            raise ValueError(
                "Selected blog category does not exist."
            )

        return category

    @staticmethod
    def _calculate_reading_stats(content):
        """
        Calculate word count and reading time.
        """

        if not content:
            return 0, 1

        words = content.split()

        word_count = len(words)

        reading_time = max(
            1,
            round(word_count / 200)
        )

        return word_count, reading_time

    @staticmethod
    def _prepare_status_fields(
        status,
        published_at=None,
        scheduled_for=None
    ):
        """
        Normalize publication timestamps according to status.
        """

        BlogService._validate_status(
            status
        )

        if status == BlogPost.STATUS_PUBLISHED:

            if published_at is None:
                published_at = datetime.utcnow()

            scheduled_for = None

        elif status == BlogPost.STATUS_SCHEDULED:

            if scheduled_for is None:
                raise ValueError(
                    "Scheduled publication date is required."
                )

            if scheduled_for <= datetime.utcnow():
                raise ValueError(
                    "Scheduled publication date must be in the future."
                )

            published_at = None

        elif status in (
            BlogPost.STATUS_DRAFT,
            BlogPost.STATUS_REVIEW,
            BlogPost.STATUS_ARCHIVED
        ):

            if status != BlogPost.STATUS_ARCHIVED:
                published_at = None

            scheduled_for = None

        return published_at, scheduled_for

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_post(
        category_id,
        title,
        slug=None,
        content=None,
        author=None,
        subtitle=None,
        excerpt=None,
        author_title=None,
        author_photo=None,
        featured_image=None,
        featured_image_alt=None,
        cover_video=None,
        gallery=None,
        reading_time=None,
        word_count=None,
        status=BlogPost.STATUS_DRAFT,
        published_at=None,
        scheduled_for=None,
        featured=False,
        pinned=False,
        allow_comments=True,
        related_experience_id=None,
        related_destination_id=None,
        cta_title=None,
        cta_text=None,
        cta_button_text=None,
        cta_button_url=None,
        meta_title=None,
        meta_description=None,
        meta_keywords=None,
        canonical_url=None,
        social_title=None,
        social_description=None,
        social_image=None
    ):
        """
        Create a new blog post.
        """

        # ---------------------------------------------------------------------
        # Required Fields
        # ---------------------------------------------------------------------

        BlogService._validate_category(
            category_id
        )

        if not title or not title.strip():
            raise ValueError(
                "Blog post title is required."
            )

        if not content or not content.strip():
            raise ValueError(
                "Blog post content is required."
            )

        if not author or not author.strip():
            raise ValueError(
                "Blog post author is required."
            )

        title = title.strip()
        author = author.strip()

        # ---------------------------------------------------------------------
        # Slug
        # ---------------------------------------------------------------------

        if not slug:
            slug = BlogService._generate_slug(
                title
            )

        slug = BlogService._normalize_slug(
            slug
        )

        if not slug:
            raise ValueError(
                "A valid blog post slug is required."
            )

        existing_slug = BlogPost.query.filter_by(
            slug=slug
        ).first()

        if existing_slug:
            raise ValueError(
                "A blog post with this slug already exists."
            )

        # ---------------------------------------------------------------------
        # Reading Statistics
        # ---------------------------------------------------------------------

        calculated_word_count, calculated_reading_time = (
            BlogService._calculate_reading_stats(
                content
            )
        )

        if word_count is None:
            word_count = calculated_word_count

        if reading_time is None:
            reading_time = calculated_reading_time

        # ---------------------------------------------------------------------
        # Status
        # ---------------------------------------------------------------------

        published_at, scheduled_for = (
            BlogService._prepare_status_fields(
                status,
                published_at,
                scheduled_for
            )
        )

        # ---------------------------------------------------------------------
        # Create
        # ---------------------------------------------------------------------

        post = BlogPost(
            category_id=category_id,
            title=title,
            slug=slug,
            subtitle=subtitle,
            excerpt=excerpt,
            content=content,
            author=author,
            author_title=author_title,
            author_photo=author_photo,
            featured_image=featured_image,
            featured_image_alt=featured_image_alt,
            cover_video=cover_video,
            gallery=gallery,
            reading_time=reading_time,
            word_count=word_count,
            status=status,
            published_at=published_at,
            scheduled_for=scheduled_for,
            featured=bool(featured),
            pinned=bool(pinned),
            allow_comments=bool(allow_comments),
            related_experience_id=related_experience_id,
            related_destination_id=related_destination_id,
            cta_title=cta_title,
            cta_text=cta_text,
            cta_button_text=cta_button_text,
            cta_button_url=cta_button_url,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            canonical_url=canonical_url,
            social_title=social_title,
            social_description=social_description,
            social_image=social_image
        )

        db.session.add(post)
        db.session.commit()

        return post

    # =========================================================================
    # Retrieve By ID
    # =========================================================================

    @staticmethod
    def get_by_id(post_id):
        """
        Retrieve a blog post by ID.
        """

        if not post_id:
            return None

        return db.session.get(
            BlogPost,
            post_id
        )

    # =========================================================================
    # Retrieve By Slug
    # =========================================================================

    @staticmethod
    def get_by_slug(
        slug,
        published_only=False
    ):
        """
        Retrieve a blog post by slug.
        """

        if not slug:
            return None

        query = BlogPost.query.filter_by(
            slug=BlogService._normalize_slug(slug)
        )

        if published_only:
            query = query.filter_by(
                status=BlogPost.STATUS_PUBLISHED
            )

        return query.first()

    # =========================================================================
    # Get All
    # =========================================================================

    @staticmethod
    def get_all(
        status=None,
        category_id=None,
        featured_only=False,
        pinned_only=False
    ):
        """
        Retrieve blog posts.
        """

        query = BlogPost.query

        if status:
            BlogService._validate_status(
                status
            )

            query = query.filter_by(
                status=status
            )

        if category_id:
            query = query.filter_by(
                category_id=category_id
            )

        if featured_only:
            query = query.filter_by(
                featured=True
            )

        if pinned_only:
            query = query.filter_by(
                pinned=True
            )

        return query.order_by(
            BlogPost.published_at.desc(),
            BlogPost.created_at.desc()
        ).all()

    # =========================================================================
    # Filter / Paginate
    # =========================================================================

    @staticmethod
    def filter_posts(
        search=None,
        category_id=None,
        status=None,
        author=None,
        featured=None,
        pinned=None,
        allow_comments=None,
        search_indexed=None,
        newsletter_sent=None,
        sort="newest",
        page=1,
        per_page=20
    ):
        """
        Filter and paginate blog posts for the admin CMS.
        """

        query = BlogPost.query

        # ---------------------------------------------------------------------
        # Search
        # ---------------------------------------------------------------------

        if search:

            search_term = f"%{search.strip()}%"

            query = query.filter(
                db.or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.subtitle.ilike(search_term),
                    BlogPost.excerpt.ilike(search_term),
                    BlogPost.content.ilike(search_term),
                    BlogPost.author.ilike(search_term),
                    BlogPost.slug.ilike(search_term)
                )
            )

        # ---------------------------------------------------------------------
        # Category
        # ---------------------------------------------------------------------

        if category_id:
            query = query.filter_by(
                category_id=category_id
            )

        # ---------------------------------------------------------------------
        # Status
        # ---------------------------------------------------------------------

        if status:

            BlogService._validate_status(
                status
            )

            query = query.filter_by(
                status=status
            )

        # ---------------------------------------------------------------------
        # Author
        # ---------------------------------------------------------------------

        if author:

            query = query.filter(
                BlogPost.author.ilike(
                    f"%{author.strip()}%"
                )
            )

        # ---------------------------------------------------------------------
        # Boolean Filters
        # ---------------------------------------------------------------------

        if featured is not None:
            query = query.filter_by(
                featured=bool(featured)
            )

        if pinned is not None:
            query = query.filter_by(
                pinned=bool(pinned)
            )

        if allow_comments is not None:
            query = query.filter_by(
                allow_comments=bool(allow_comments)
            )

        if search_indexed is not None:
            query = query.filter_by(
                search_indexed=bool(search_indexed)
            )

        if newsletter_sent is not None:
            query = query.filter_by(
                newsletter_sent=bool(newsletter_sent)
            )

        # ---------------------------------------------------------------------
        # Sorting
        # ---------------------------------------------------------------------

        sort_map = {
            "newest": BlogPost.created_at.desc(),
            "oldest": BlogPost.created_at.asc(),
            "title_asc": BlogPost.title.asc(),
            "title_desc": BlogPost.title.desc(),
            "views_desc": BlogPost.views.desc(),
            "likes_desc": BlogPost.likes.desc(),
            "shares_desc": BlogPost.shares.desc(),
            "published_desc": BlogPost.published_at.desc(),
            "updated_desc": BlogPost.updated_at.desc(),
        }

        query = query.order_by(
            sort_map.get(
                sort,
                BlogPost.created_at.desc()
            )
        )

        # ---------------------------------------------------------------------
        # Pagination
        # ---------------------------------------------------------------------

        return query.paginate(
            page=max(int(page or 1), 1),
            per_page=max(int(per_page or 20), 1),
            error_out=False
        )

    # =========================================================================
    # Published Posts
    # =========================================================================

    @staticmethod
    def get_published(
        category_id=None,
        featured_only=False,
        pinned_only=False
    ):
        """
        Retrieve publicly published blog posts.
        """

        query = BlogPost.query.filter_by(
            status=BlogPost.STATUS_PUBLISHED
        )

        if category_id:
            query = query.filter_by(
                category_id=category_id
            )

        if featured_only:
            query = query.filter_by(
                featured=True
            )

        if pinned_only:
            query = query.filter_by(
                pinned=True
            )

        return query.order_by(
            BlogPost.published_at.desc(),
            BlogPost.created_at.desc()
        ).all()

    # =========================================================================
    # Featured Posts
    # =========================================================================

    @staticmethod
    def get_featured(
        published_only=True
    ):
        """
        Retrieve featured blog posts.
        """

        query = BlogPost.query.filter_by(
            featured=True
        )

        if published_only:
            query = query.filter_by(
                status=BlogPost.STATUS_PUBLISHED
            )

        return query.order_by(
            BlogPost.published_at.desc(),
            BlogPost.created_at.desc()
        ).all()

    # =========================================================================
    # Pinned Posts
    # =========================================================================

    @staticmethod
    def get_pinned(
        published_only=True
    ):
        """
        Retrieve pinned blog posts.
        """

        query = BlogPost.query.filter_by(
            pinned=True
        )

        if published_only:
            query = query.filter_by(
                status=BlogPost.STATUS_PUBLISHED
            )

        return query.order_by(
            BlogPost.published_at.desc(),
            BlogPost.created_at.desc()
        ).all()

    # =========================================================================
    # Search
    # =========================================================================

    @staticmethod
    def search(
        query_text,
        published_only=True,
        category_id=None
    ):
        """
        Search blog posts.
        """

        if not query_text:
            return []

        search_term = f"%{query_text.strip()}%"

        query = BlogPost.query.filter(
            db.or_(
                BlogPost.title.ilike(search_term),
                BlogPost.subtitle.ilike(search_term),
                BlogPost.excerpt.ilike(search_term),
                BlogPost.content.ilike(search_term),
                BlogPost.author.ilike(search_term),
                BlogPost.slug.ilike(search_term)
            )
        )

        if published_only:
            query = query.filter_by(
                status=BlogPost.STATUS_PUBLISHED
            )

        if category_id:
            query = query.filter_by(
                category_id=category_id
            )

        return query.order_by(
            BlogPost.published_at.desc(),
            BlogPost.created_at.desc()
        ).all()

    # =========================================================================
    # Drafts
    # =========================================================================

    @staticmethod
    def get_drafts():
        """
        Return draft posts.
        """

        return BlogService.get_all(
            status=BlogPost.STATUS_DRAFT
        )

    # =========================================================================
    # Review
    # =========================================================================

    @staticmethod
    def get_review_posts():
        """
        Return posts awaiting review.
        """

        return BlogService.get_all(
            status=BlogPost.STATUS_REVIEW
        )

    # =========================================================================
    # Scheduled
    # =========================================================================

    @staticmethod
    def get_scheduled():
        """
        Return scheduled posts ordered by publication time.
        """

        return BlogPost.query.filter_by(
            status=BlogPost.STATUS_SCHEDULED
        ).order_by(
            BlogPost.scheduled_for.asc()
        ).all()

    # =========================================================================
    # Archived
    # =========================================================================

    @staticmethod
    def get_archived():
        """
        Return archived posts.
        """

        return BlogService.get_all(
            status=BlogPost.STATUS_ARCHIVED
        )

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_post(
        post_id,
        **updates
    ):
        """
        Update an existing blog post.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        # ---------------------------------------------------------------------
        # Category
        # ---------------------------------------------------------------------

        if "category_id" in updates:

            BlogService._validate_category(
                updates["category_id"]
            )

        # ---------------------------------------------------------------------
        # Slug
        # ---------------------------------------------------------------------

        if "slug" in updates:

            slug = BlogService._normalize_slug(
                updates["slug"]
            )

            if not slug:
                raise ValueError(
                    "Blog post slug cannot be empty."
                )

            duplicate_slug = BlogPost.query.filter(
                BlogPost.slug == slug,
                BlogPost.id != post.id
            ).first()

            if duplicate_slug:
                raise ValueError(
                    "Another blog post with this slug already exists."
                )

            updates["slug"] = slug

        # ---------------------------------------------------------------------
        # Title
        # ---------------------------------------------------------------------

        if "title" in updates:

            if not updates["title"] or not updates["title"].strip():
                raise ValueError(
                    "Blog post title cannot be empty."
                )

            updates["title"] = updates["title"].strip()

        # ---------------------------------------------------------------------
        # Content
        # ---------------------------------------------------------------------

        if "content" in updates:

            if not updates["content"] or not updates["content"].strip():
                raise ValueError(
                    "Blog post content cannot be empty."
                )

            calculated_word_count, calculated_reading_time = (
                BlogService._calculate_reading_stats(
                    updates["content"]
                )
            )

            updates.setdefault(
                "word_count",
                calculated_word_count
            )

            updates.setdefault(
                "reading_time",
                calculated_reading_time
            )

        # ---------------------------------------------------------------------
        # Status
        # ---------------------------------------------------------------------

        if "status" in updates:

            new_status = updates["status"]

            BlogService._validate_status(
                new_status
            )

            current_published_at = updates.get(
                "published_at",
                post.published_at
            )

            current_scheduled_for = updates.get(
                "scheduled_for",
                post.scheduled_for
            )

            published_at, scheduled_for = (
                BlogService._prepare_status_fields(
                    new_status,
                    current_published_at,
                    current_scheduled_for
                )
            )

            updates["published_at"] = published_at
            updates["scheduled_for"] = scheduled_for

        # ---------------------------------------------------------------------
        # Allowed Fields
        # ---------------------------------------------------------------------

        allowed_fields = {
            "category_id",
            "title",
            "slug",
            "subtitle",
            "excerpt",
            "content",
            "author",
            "author_title",
            "author_photo",
            "featured_image",
            "featured_image_alt",
            "cover_video",
            "gallery",
            "reading_time",
            "word_count",
            "status",
            "published_at",
            "scheduled_for",
            "featured",
            "pinned",
            "allow_comments",
            "related_experience_id",
            "related_destination_id",
            "cta_title",
            "cta_text",
            "cta_button_text",
            "cta_button_url",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "canonical_url",
            "social_title",
            "social_description",
            "social_image",
            "newsletter_sent",
            "search_indexed"
        }

        for field, value in updates.items():

            if field in allowed_fields:
                setattr(
                    post,
                    field,
                    value
                )

        db.session.commit()

        return post

    # =========================================================================
    # Submit For Review
    # =========================================================================

    @staticmethod
    def submit_for_review(post_id):
        """
        Move a post into editorial review.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.submit_for_review()

        db.session.commit()

        return post

    # =========================================================================
    # Schedule
    # =========================================================================

    @staticmethod
    def schedule(
        post_id,
        scheduled_for
    ):
        """
        Schedule a blog post for future publication.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        if not scheduled_for:
            raise ValueError(
                "Scheduled publication date is required."
            )

        if scheduled_for <= datetime.utcnow():
            raise ValueError(
                "Scheduled publication date must be in the future."
            )

        post.schedule(
            scheduled_for
        )

        db.session.commit()

        return post

    # =========================================================================
    # Publish
    # =========================================================================

    @staticmethod
    def publish(
        post_id,
        published_at=None
    ):
        """
        Publish a blog post immediately.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        if published_at is None:
            published_at = datetime.utcnow()

        if published_at > datetime.utcnow():
            raise ValueError(
                "Publication date cannot be in the future."
            )

        post.publish(
            published_at
        )

        db.session.commit()

        return post

    # =========================================================================
    # Unpublish
    # =========================================================================

    @staticmethod
    def unpublish(post_id):
        """
        Move a published post back to draft.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.unpublish()

        db.session.commit()

        return post

    # =========================================================================
    # Archive
    # =========================================================================

    @staticmethod
    def archive(post_id):
        """
        Archive a blog post.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.archive()

        db.session.commit()

        return post

    # =========================================================================
    # Restore
    # =========================================================================

    @staticmethod
    def restore_to_draft(post_id):
        """
        Restore an archived post to draft status.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.restore()

        db.session.commit()

        return post

    # =========================================================================
    # Feature
    # =========================================================================

    @staticmethod
    def feature(post_id):
        """
        Mark a blog post as featured.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.featured = True

        db.session.commit()

        return post

    # =========================================================================
    # Unfeature
    # =========================================================================

    @staticmethod
    def unfeature(post_id):
        """
        Remove featured status.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.featured = False

        db.session.commit()

        return post

    # =========================================================================
    # Pin
    # =========================================================================

    @staticmethod
    def pin(post_id):
        """
        Pin a blog post.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.pinned = True

        db.session.commit()

        return post

    # =========================================================================
    # Unpin
    # =========================================================================

    @staticmethod
    def unpin(post_id):
        """
        Remove pinned status.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.pinned = False

        db.session.commit()

        return post

    # =========================================================================
    # Views
    # =========================================================================

    @staticmethod
    def increment_views(
        post_id,
        amount=1
    ):
        """
        Increment the view counter.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        amount = max(
            int(amount or 1),
            1
        )

        post.increment_views(
            amount
        )

        db.session.commit()

        return post.views

    # =========================================================================
    # Likes
    # =========================================================================

    @staticmethod
    def increment_likes(
        post_id,
        amount=1
    ):
        """
        Increment the like counter.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        amount = max(
            int(amount or 1),
            1
        )

        post.increment_likes(
            amount
        )

        db.session.commit()

        return post.likes

    # =========================================================================
    # Shares
    # =========================================================================

    @staticmethod
    def increment_shares(
        post_id,
        amount=1
    ):
        """
        Increment the share counter.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        amount = max(
            int(amount or 1),
            1
        )

        post.increment_shares(
            amount
        )

        db.session.commit()

        return post.shares

    # =========================================================================
    # Newsletter Status
    # =========================================================================

    @staticmethod
    def mark_newsletter_sent(post_id):
        """
        Mark a blog post as included in a newsletter.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.newsletter_sent = True

        db.session.commit()

        return post

    # =========================================================================
    # Reset Newsletter Status
    # =========================================================================

    @staticmethod
    def reset_newsletter_status(post_id):
        """
        Reset newsletter sent status.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.newsletter_sent = False

        db.session.commit()

        return post

    # =========================================================================
    # Search Index
    # =========================================================================

    @staticmethod
    def mark_search_indexed(post_id):
        """
        Mark a blog post as indexed by the search system.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.search_indexed = True

        db.session.commit()

        return post

    # =========================================================================
    # Reset Search Index
    # =========================================================================

    @staticmethod
    def reset_search_index(post_id):
        """
        Mark a post as not indexed.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.search_indexed = False

        db.session.commit()

        return post

    # =========================================================================
    # Reading Information
    # =========================================================================

    @staticmethod
    def update_reading_information(
        post_id,
        word_count=None,
        reading_time=None
    ):
        """
        Update reading statistics.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        if word_count is None or reading_time is None:

            calculated_word_count, calculated_reading_time = (
                BlogService._calculate_reading_stats(
                    post.content
                )
            )

            if word_count is None:
                word_count = calculated_word_count

            if reading_time is None:
                reading_time = calculated_reading_time

        if word_count < 0:
            raise ValueError(
                "Word count cannot be negative."
            )

        if reading_time < 1:
            raise ValueError(
                "Reading time must be at least one minute."
            )

        post.word_count = word_count
        post.reading_time = reading_time

        db.session.commit()

        return post

    # =========================================================================
    # Recalculate Reading Information
    # =========================================================================

    @staticmethod
    def recalculate_reading_information(post_id):
        """
        Calculate reading information directly from post content.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        word_count, reading_time = (
            BlogService._calculate_reading_stats(
                post.content
            )
        )

        post.word_count = word_count
        post.reading_time = reading_time

        db.session.commit()

        return post

    # =========================================================================
    # Related Experience
    # =========================================================================

    @staticmethod
    def attach_experience(
        post_id,
        experience_id
    ):
        """
        Associate a blog post with an experience.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.related_experience_id = experience_id

        db.session.commit()

        return post

    # =========================================================================
    # Remove Related Experience
    # =========================================================================

    @staticmethod
    def detach_experience(post_id):
        """
        Remove the related experience.
        """

        return BlogService.attach_experience(
            post_id,
            None
        )

    # =========================================================================
    # Related Destination
    # =========================================================================

    @staticmethod
    def attach_destination(
        post_id,
        destination_id
    ):
        """
        Associate a blog post with a destination.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.related_destination_id = destination_id

        db.session.commit()

        return post

    # =========================================================================
    # Remove Related Destination
    # =========================================================================

    @staticmethod
    def detach_destination(post_id):
        """
        Remove the related destination.
        """

        return BlogService.attach_destination(
            post_id,
            None
        )

    # =========================================================================
    # SEO Update
    # =========================================================================

    @staticmethod
    def update_seo(
        post_id,
        meta_title=None,
        meta_description=None,
        meta_keywords=None,
        canonical_url=None,
        social_title=None,
        social_description=None,
        social_image=None
    ):
        """
        Update SEO and social metadata.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.meta_title = meta_title
        post.meta_description = meta_description
        post.meta_keywords = meta_keywords
        post.canonical_url = canonical_url
        post.social_title = social_title
        post.social_description = social_description
        post.social_image = social_image

        db.session.commit()

        return post

    # =========================================================================
    # CTA Update
    # =========================================================================

    @staticmethod
    def update_cta(
        post_id,
        cta_title=None,
        cta_text=None,
        cta_button_text=None,
        cta_button_url=None
    ):
        """
        Update the marketing call-to-action.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return None

        post.cta_title = cta_title
        post.cta_text = cta_text
        post.cta_button_text = cta_button_text
        post.cta_button_url = cta_button_url

        db.session.commit()

        return post

    # =========================================================================
    # Duplicate
    # =========================================================================

    @staticmethod
    def duplicate(
        post_id,
        title=None
    ):
        """
        Create a draft copy of an existing post.
        """

        original = BlogService.get_by_id(
            post_id
        )

        if not original:
            return None

        new_title = (
            title.strip()
            if title and title.strip()
            else f"{original.title} Copy"
        )

        base_slug = BlogService._generate_slug(
            new_title
        )

        slug = base_slug
        counter = 2

        while BlogPost.query.filter_by(
            slug=slug
        ).first():

            slug = f"{base_slug}-{counter}"
            counter += 1

        copy_post = BlogPost(
            category_id=original.category_id,
            title=new_title,
            slug=slug,
            subtitle=original.subtitle,
            excerpt=original.excerpt,
            content=original.content,
            author=original.author,
            author_title=original.author_title,
            author_photo=original.author_photo,
            featured_image=original.featured_image,
            featured_image_alt=original.featured_image_alt,
            cover_video=original.cover_video,
            gallery=original.gallery,
            reading_time=original.reading_time,
            word_count=original.word_count,
            status=BlogPost.STATUS_DRAFT,
            published_at=None,
            scheduled_for=None,
            featured=False,
            pinned=False,
            allow_comments=original.allow_comments,
            related_experience_id=original.related_experience_id,
            related_destination_id=original.related_destination_id,
            cta_title=original.cta_title,
            cta_text=original.cta_text,
            cta_button_text=original.cta_button_text,
            cta_button_url=original.cta_button_url,
            meta_title=original.meta_title,
            meta_description=original.meta_description,
            meta_keywords=original.meta_keywords,
            canonical_url=None,
            social_title=original.social_title,
            social_description=original.social_description,
            social_image=original.social_image,
            newsletter_sent=False,
            search_indexed=False
        )

        db.session.add(copy_post)
        db.session.commit()

        return copy_post

    # =========================================================================
    # Statistics
    # =========================================================================

    @staticmethod
    def get_statistics():
        """
        Return comprehensive blog statistics.
        """

        total = BlogPost.query.count()

        drafts = BlogPost.query.filter_by(
            status=BlogPost.STATUS_DRAFT
        ).count()

        review = BlogPost.query.filter_by(
            status=BlogPost.STATUS_REVIEW
        ).count()

        scheduled = BlogPost.query.filter_by(
            status=BlogPost.STATUS_SCHEDULED
        ).count()

        published = BlogPost.query.filter_by(
            status=BlogPost.STATUS_PUBLISHED
        ).count()

        archived = BlogPost.query.filter_by(
            status=BlogPost.STATUS_ARCHIVED
        ).count()

        featured = BlogPost.query.filter_by(
            featured=True
        ).count()

        pinned = BlogPost.query.filter_by(
            pinned=True
        ).count()

        newsletter_sent = BlogPost.query.filter_by(
            newsletter_sent=True
        ).count()

        search_indexed = BlogPost.query.filter_by(
            search_indexed=True
        ).count()

        total_views = db.session.query(
            db.func.coalesce(
                db.func.sum(BlogPost.views),
                0
            )
        ).scalar()

        total_likes = db.session.query(
            db.func.coalesce(
                db.func.sum(BlogPost.likes),
                0
            )
        ).scalar()

        total_shares = db.session.query(
            db.func.coalesce(
                db.func.sum(BlogPost.shares),
                0
            )
        ).scalar()

        total_words = db.session.query(
            db.func.coalesce(
                db.func.sum(BlogPost.word_count),
                0
            )
        ).scalar()

        return {
            "total": total,
            "drafts": drafts,
            "review": review,
            "scheduled": scheduled,
            "published": published,
            "archived": archived,
            "featured": featured,
            "pinned": pinned,
            "newsletter_sent": newsletter_sent,
            "search_indexed": search_indexed,
            "not_search_indexed": total - search_indexed,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_shares": total_shares,
            "total_words": total_words
        }

    # =========================================================================
    # Count
    # =========================================================================

    @staticmethod
    def count(status=None):
        """
        Return the number of blog posts.
        """

        query = BlogPost.query

        if status:
            BlogService._validate_status(
                status
            )

            query = query.filter_by(
                status=status
            )

        return query.count()

    # =========================================================================
    # Engagement
    # =========================================================================

    @staticmethod
    def get_top_posts(
        limit=10,
        metric="views"
    ):
        """
        Return top-performing posts.
        """

        metric_map = {
            "views": BlogPost.views,
            "likes": BlogPost.likes,
            "shares": BlogPost.shares,
        }

        column = metric_map.get(
            metric,
            BlogPost.views
        )

        return BlogPost.query.filter_by(
            status=BlogPost.STATUS_PUBLISHED
        ).order_by(
            column.desc(),
            BlogPost.published_at.desc()
        ).limit(
            max(int(limit or 10), 1)
        ).all()

    # =========================================================================
    # Bulk Actions
    # =========================================================================

    @staticmethod
    def bulk_action(
        post_ids,
        action
    ):
        """
        Perform a bulk action on blog posts.

        Supported actions:

            publish
            unpublish
            review
            archive
            restore
            feature
            unfeature
            pin
            unpin
            delete
        """

        if not post_ids:
            return 0

        posts = BlogPost.query.filter(
            BlogPost.id.in_(post_ids)
        ).all()

        if action not in {
            "publish",
            "unpublish",
            "review",
            "archive",
            "restore",
            "feature",
            "unfeature",
            "pin",
            "unpin",
            "delete"
        }:
            raise ValueError(
                f"Unsupported bulk action: {action}"
            )

        for post in posts:

            if action == "publish":
                post.publish()

            elif action == "unpublish":
                post.unpublish()

            elif action == "review":
                post.submit_for_review()

            elif action == "archive":
                post.archive()

            elif action == "restore":
                post.restore()

            elif action == "feature":
                post.featured = True

            elif action == "unfeature":
                post.featured = False

            elif action == "pin":
                post.pinned = True

            elif action == "unpin":
                post.pinned = False

            elif action == "delete":
                db.session.delete(post)

        db.session.commit()

        return len(posts)

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete(post_id):
        """
        Permanently delete a blog post.
        """

        post = BlogService.get_by_id(
            post_id
        )

        if not post:
            return False

        db.session.delete(post)
        db.session.commit()

        return True