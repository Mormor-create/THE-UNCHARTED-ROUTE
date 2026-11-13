"""
===============================================================================
The Uncharted Route
Search Service
===============================================================================

Centralized search functionality for The Uncharted Route.

The search service provides:

• Global website search
• Experience search
• Destination search
• Blog search
• Wildlife search
• Tag-based filtering
• Category filtering
• Keyword matching
• Pagination
• Result ranking
• Search suggestions
• Result serialization

The service is intentionally kept separate from routes and models so that
search behaviour can evolve without tightly coupling it to the frontend.

This implementation is designed to work with SQLAlchemy models while
remaining flexible enough to accommodate the project's evolving model
structure.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


# =============================================================================
# Search Error
# =============================================================================

class SearchError(Exception):
    """
    Raised when a search operation cannot be completed.
    """

    pass


# =============================================================================
# Search Result
# =============================================================================

class SearchResult:
    """
    Represents a single search result.
    """

    def __init__(
        self,
        item: Any,
        result_type: str,
        title: str,
        description: str = "",
        url: Optional[str] = None,
        score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.item = item
        self.result_type = result_type
        self.title = title
        self.description = description
        self.url = url
        self.score = score
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the search result to a dictionary.
        """

        item_id = getattr(
            self.item,
            "id",
            None
        )

        return {
            "id": item_id,
            "type": self.result_type,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "score": self.score,
            "metadata": self.metadata,
        }

    def __repr__(self):
        return (
            f"<SearchResult "
            f"type={self.result_type} "
            f"title={self.title!r} "
            f"score={self.score}>"
        )


# =============================================================================
# Search Response
# =============================================================================

class SearchResponse:
    """
    Standardized search response.
    """

    def __init__(
        self,
        query: str,
        results: Optional[List[SearchResult]] = None,
        page: int = 1,
        per_page: int = 20,
        total: int = 0,
    ):
        self.query = query
        self.results = results or []
        self.page = page
        self.per_page = per_page
        self.total = total

    @property
    def total_pages(self) -> int:
        """
        Return the total number of result pages.
        """

        if self.per_page <= 0:
            return 0

        return (
            self.total + self.per_page - 1
        ) // self.per_page

    @property
    def has_next(self) -> bool:
        """
        Determine whether another page exists.
        """

        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """
        Determine whether a previous page exists.
        """

        return self.page > 1

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the response to a dictionary.
        """

        return {
            "query": self.query,
            "results": [
                result.to_dict()
                for result in self.results
            ],
            "page": self.page,
            "per_page": self.per_page,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }


# =============================================================================
# Search Service
# =============================================================================

class SearchService:
    """
    Centralized search service.
    """

    # =========================================================================
    # Configuration
    # =========================================================================

    DEFAULT_PER_PAGE = 20

    MAX_PER_PAGE = 100

    # =========================================================================
    # Searchable Fields
    # =========================================================================

    EXPERIENCE_FIELDS = (
        "title",
        "name",
        "short_description",
        "description",
        "overview",
        "location",
        "category",
    )

    DESTINATION_FIELDS = (
        "name",
        "title",
        "description",
        "short_description",
        "location",
        "country",
    )

    BLOG_FIELDS = (
        "title",
        "subtitle",
        "excerpt",
        "content",
        "author",
    )

    WILDLIFE_FIELDS = (
        "common_name",
        "scientific_name",
        "family",
        "description",
        "interesting_fact",
        "habitat",
        "diet",
        "category",
    )

    # =========================================================================
    # Initialization
    # =========================================================================

    def __init__(
        self,
        default_per_page: int = DEFAULT_PER_PAGE,
    ):
        self.default_per_page = self._normalize_per_page(
            default_per_page
        )

    # =========================================================================
    # Normalization
    # =========================================================================

    @staticmethod
    def normalize_query(
        query: Optional[str],
    ) -> str:
        """
        Normalize a search query.
        """

        if not query:
            return ""

        return " ".join(
            str(query)
            .strip()
            .lower()
            .split()
        )

    @staticmethod
    def tokenize(
        query: str,
    ) -> List[str]:
        """
        Convert a query into searchable terms.
        """

        query = SearchService.normalize_query(
            query
        )

        if not query:
            return []

        return [
            token
            for token in query.split()
            if token
        ]

    @staticmethod
    def _normalize_per_page(
        per_page: int,
    ) -> int:
        """
        Normalize pagination size.
        """

        try:
            per_page = int(per_page)
        except (TypeError, ValueError):
            per_page = SearchService.DEFAULT_PER_PAGE

        if per_page <= 0:
            per_page = SearchService.DEFAULT_PER_PAGE

        return min(
            per_page,
            SearchService.MAX_PER_PAGE
        )

    @staticmethod
    def _normalize_page(
        page: int,
    ) -> int:
        """
        Normalize page number.
        """

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        return max(
            page,
            1
        )

    # =========================================================================
    # Text Extraction
    # =========================================================================

    @staticmethod
    def get_text(
        item: Any,
        field: str,
    ) -> str:
        """
        Safely retrieve searchable text from an object.
        """

        value = getattr(
            item,
            field,
            None
        )

        if value is None:
            return ""

        if isinstance(
            value,
            (list, tuple, set)
        ):
            return " ".join(
                str(value)
                for value in value
            )

        return str(value)

    # =========================================================================
    # Scoring
    # =========================================================================

    def score_item(
        self,
        item: Any,
        query: str,
        fields: Iterable[str],
    ) -> float:
        """
        Calculate a basic relevance score.

        Exact title/name matches receive the highest weight.
        Prefix matches and field matches receive progressively lower weight.
        """

        query = self.normalize_query(
            query
        )

        if not query:
            return 0.0

        tokens = self.tokenize(
            query
        )

        score = 0.0

        for field in fields:

            value = self.get_text(
                item,
                field
            ).lower()

            if not value:
                continue

            # ---------------------------------------------------------------
            # Exact field match
            # ---------------------------------------------------------------

            if value == query:

                if field in {
                    "title",
                    "name",
                    "common_name",
                }:
                    score += 100

                else:
                    score += 50

            # ---------------------------------------------------------------
            # Exact phrase
            # ---------------------------------------------------------------

            elif query in value:

                if field in {
                    "title",
                    "name",
                    "common_name",
                }:
                    score += 60

                else:
                    score += 25

            # ---------------------------------------------------------------
            # Individual tokens
            # ---------------------------------------------------------------

            for token in tokens:

                if token not in value:
                    continue

                if field in {
                    "title",
                    "name",
                    "common_name",
                }:
                    score += 20

                elif field in {
                    "subtitle",
                    "excerpt",
                    "short_description",
                }:
                    score += 10

                else:
                    score += 5

        # ---------------------------------------------------------------------
        # Featured content receives a small ranking boost.
        # ---------------------------------------------------------------------

        if getattr(
            item,
            "featured",
            False
        ):
            score += 5

        if getattr(
            item,
            "pinned",
            False
        ):
            score += 3

        return round(
            score,
            2
        )

    # =========================================================================
    # Activity Checks
    # =========================================================================

    @staticmethod
    def is_active(
        item: Any,
    ) -> bool:
        """
        Determine whether an object should be searchable.
        """

        if hasattr(
            item,
            "active"
        ):
            return bool(
                getattr(
                    item,
                    "active"
                )
            )

        if hasattr(
            item,
            "is_active"
        ):
            return bool(
                getattr(
                    item,
                    "is_active"
                )
            )

        return True

    @staticmethod
    def is_published(
        item: Any,
    ) -> bool:
        """
        Determine whether a content object is published.
        """

        status = getattr(
            item,
            "status",
            None
        )

        if status is None:
            return True

        return (
            str(status).lower()
            == "published"
        )

    # =========================================================================
    # URL Generation
    # =========================================================================

    @staticmethod
    def build_url(
        item: Any,
        result_type: str,
    ) -> Optional[str]:
        """
        Build a conventional frontend URL.

        Routes can override these URLs later if the project's route structure
        differs.
        """

        slug = getattr(
            item,
            "slug",
            None
        )

        item_id = getattr(
            item,
            "id",
            None
        )

        if slug:

            paths = {
                "experiences": "/experiences/",
                "destination": "/destinations/",
                "blog": "/blog/",
                "wildlife": "/wildlife/",
                "tag": "/tags/",
            }

            prefix = paths.get(
                result_type,
                "/"
            )

            return f"{prefix}{slug}"

        if item_id is not None:

            paths = {
                "experiences": "/experiences/",
                "destination": "/destinations/",
                "blog": "/blog/",
                "wildlife": "/wildlife/",
                "tag": "/tags/",
            }

            prefix = paths.get(
                result_type,
                "/"
            )

            return f"{prefix}{item_id}"

        return None

    # =========================================================================
    # Result Creation
    # =========================================================================

    def make_result(
        self,
        item: Any,
        result_type: str,
        query: str,
        fields: Iterable[str],
    ) -> Optional[SearchResult]:
        """
        Convert a model instance into a SearchResult.
        """

        if not self.is_active(
            item
        ):
            return None

        if (
            result_type == "blog"
            and not self.is_published(item)
        ):
            return None

        score = self.score_item(
            item=item,
            query=query,
            fields=fields,
        )

        if score <= 0:
            return None

        title = (
            getattr(
                item,
                "title",
                None
            )
            or getattr(
                item,
                "name",
                None
            )
            or getattr(
                item,
                "common_name",
                None
            )
            or "Untitled"
        )

        description = (
            getattr(
                item,
                "excerpt",
                None
            )
            or getattr(
                item,
                "short_description",
                None
            )
            or getattr(
                item,
                "description",
                None
            )
            or ""
        )

        return SearchResult(
            item=item,
            result_type=result_type,
            title=str(title),
            description=str(description),
            url=self.build_url(
                item,
                result_type,
            ),
            score=score,
            metadata={
                "featured": bool(
                    getattr(
                        item,
                        "featured",
                        False
                    )
                ),
            },
        )

    # =========================================================================
    # Collection Search
    # =========================================================================

    def search_collection(
        self,
        collection: Iterable,
        query: str,
        result_type: str,
        fields: Iterable[str],
    ) -> List[SearchResult]:
        """
        Search a collection of model instances.
        """

        query = self.normalize_query(
            query
        )

        if not query:
            return []

        results = []

        for item in collection:

            result = self.make_result(
                item=item,
                result_type=result_type,
                query=query,
                fields=fields,
            )

            if result:
                results.append(
                    result
                )

        results.sort(
            key=lambda result: (
                -result.score,
                result.title.lower(),
            )
        )

        return results

    # =========================================================================
    # Experience Search
    # =========================================================================

    def search_experiences(
        self,
        experiences,
        query: str,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> SearchResponse:
        """
        Search experiences.
        """

        return self._paginate_results(
            results=self.search_collection(
                collection=experiences,
                query=query,
                result_type="experiences",
                fields=self.EXPERIENCE_FIELDS,
            ),
            query=query,
            page=page,
            per_page=per_page,
        )

    # =========================================================================
    # Destination Search
    # =========================================================================

    def search_destinations(
        self,
        destinations,
        query: str,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> SearchResponse:
        """
        Search destinations.
        """

        return self._paginate_results(
            results=self.search_collection(
                collection=destinations,
                query=query,
                result_type="destination",
                fields=self.DESTINATION_FIELDS,
            ),
            query=query,
            page=page,
            per_page=per_page,
        )

    # =========================================================================
    # Blog Search
    # =========================================================================

    def search_blog_posts(
        self,
        posts,
        query: str,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> SearchResponse:
        """
        Search published blog posts.
        """

        return self._paginate_results(
            results=self.search_collection(
                collection=posts,
                query=query,
                result_type="blog",
                fields=self.BLOG_FIELDS,
            ),
            query=query,
            page=page,
            per_page=per_page,
        )

    # =========================================================================
    # Wildlife Search
    # =========================================================================

    def search_wildlife(
        self,
        species,
        query: str,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> SearchResponse:
        """
        Search wildlife species.
        """

        return self._paginate_results(
            results=self.search_collection(
                collection=species,
                query=query,
                result_type="wildlife",
                fields=self.WILDLIFE_FIELDS,
            ),
            query=query,
            page=page,
            per_page=per_page,
        )

    # =========================================================================
    # Global Search
    # =========================================================================

    def global_search(
        self,
        query: str,
        experiences=None,
        destinations=None,
        posts=None,
        wildlife=None,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> SearchResponse:
        """
        Search across multiple website content types.

        Collections should normally be supplied as SQLAlchemy query objects
        or already-loaded model collections.
        """

        query = self.normalize_query(
            query
        )

        if not query:
            return SearchResponse(
                query="",
                results=[],
                page=1,
                per_page=self._normalize_per_page(
                    per_page or self.default_per_page
                ),
                total=0,
            )

        results = []

        if experiences is not None:

            results.extend(
                self.search_collection(
                    experiences,
                    query,
                    "experiences",
                    self.EXPERIENCE_FIELDS,
                )
            )

        if destinations is not None:

            results.extend(
                self.search_collection(
                    destinations,
                    query,
                    "destination",
                    self.DESTINATION_FIELDS,
                )
            )

        if posts is not None:

            results.extend(
                self.search_collection(
                    posts,
                    query,
                    "blog",
                    self.BLOG_FIELDS,
                )
            )

        if wildlife is not None:

            results.extend(
                self.search_collection(
                    wildlife,
                    query,
                    "wildlife",
                    self.WILDLIFE_FIELDS,
                )
            )

        results.sort(
            key=lambda result: (
                -result.score,
                result.title.lower(),
            )
        )

        return self._paginate_results(
            results=results,
            query=query,
            page=page,
            per_page=per_page,
        )

    # =========================================================================
    # Pagination
    # =========================================================================

    def _paginate_results(
        self,
        results: List[SearchResult],
        query: str,
        page: int = 1,
        per_page: Optional[int] = None,
    ) -> SearchResponse:
        """
        Paginate search results.
        """

        page = self._normalize_page(
            page
        )

        per_page = self._normalize_per_page(
            per_page or self.default_per_page
        )

        total = len(
            results
        )

        start = (
            page - 1
        ) * per_page

        end = (
            start + per_page
        )

        return SearchResponse(
            query=self.normalize_query(
                query
            ),
            results=results[start:end],
            page=page,
            per_page=per_page,
            total=total,
        )

    # =========================================================================
    # Suggestions
    # =========================================================================

    def suggestions(
        self,
        collection: Iterable,
        query: str,
        fields: Iterable[str],
        limit: int = 5,
    ) -> List[str]:
        """
        Return simple search suggestions.

        Suggestions are generated from title/name-like fields.
        """

        query = self.normalize_query(
            query
        )

        if not query:
            return []

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 5

        limit = max(
            limit,
            1
        )

        suggestions = []

        for item in collection:

            if not self.is_active(
                item
            ):
                continue

            for field in fields:

                value = self.get_text(
                    item,
                    field
                ).strip()

                if not value:
                    continue

                if query in value.lower():

                    suggestions.append(
                        value
                    )

                    break

        # Remove duplicates while preserving order.

        unique = list(
            dict.fromkeys(
                suggestions
            )
        )

        unique.sort(
            key=lambda value: (
                not value.lower().startswith(
                    query
                ),
                value.lower(),
            )
        )

        return unique[:limit]

    # =========================================================================
    # Related Results
    # =========================================================================

    def related_results(
        self,
        collection: Iterable,
        item: Any,
        fields: Iterable[str],
        result_type: str,
        limit: int = 5,
    ) -> List[SearchResult]:
        """
        Find content related to another item.

        Relatedness is determined using overlapping searchable terms.
        """

        source_values = []

        for field in fields:

            value = self.get_text(
                item,
                field
            ).lower()

            if value:
                source_values.extend(
                    self.tokenize(
                        value
                    )
                )

        source_terms = set(
            source_values
        )

        if not source_terms:
            return []

        results = []

        for candidate in collection:

            if candidate is item:
                continue

            if not self.is_active(
                candidate
            ):
                continue

            candidate_terms = set()

            for field in fields:

                value = self.get_text(
                    candidate,
                    field
                ).lower()

                if value:
                    candidate_terms.update(
                        self.tokenize(
                            value
                        )
                    )

            overlap = (
                source_terms
                & candidate_terms
            )

            if not overlap:
                continue

            score = len(
                overlap
            )

            if getattr(
                candidate,
                "featured",
                False
            ):
                score += 1

            title = (
                getattr(
                    candidate,
                    "title",
                    None
                )
                or getattr(
                    candidate,
                    "name",
                    None
                )
                or getattr(
                    candidate,
                    "common_name",
                    None
                )
                or "Untitled"
            )

            description = (
                getattr(
                    candidate,
                    "excerpt",
                    None
                )
                or getattr(
                    candidate,
                    "short_description",
                    None
                )
                or getattr(
                    candidate,
                    "description",
                    None
                )
                or ""
            )

            results.append(
                SearchResult(
                    item=candidate,
                    result_type=result_type,
                    title=str(title),
                    description=str(description),
                    url=self.build_url(
                        candidate,
                        result_type,
                    ),
                    score=score,
                )
            )

        results.sort(
            key=lambda result: (
                -result.score,
                result.title.lower(),
            )
        )

        return results[:limit]


# =============================================================================
# Service Instance
# =============================================================================

search_service = SearchService()


# =============================================================================
# Convenience Functions
# =============================================================================

def search_experiences(
    experiences,
    query: str,
    page: int = 1,
    per_page: Optional[int] = None,
) -> SearchResponse:
    """
    Convenience wrapper for experiences search.
    """

    return search_service.search_experiences(
        experiences=experiences,
        query=query,
        page=page,
        per_page=per_page,
    )


def search_destinations(
    destinations,
    query: str,
    page: int = 1,
    per_page: Optional[int] = None,
) -> SearchResponse:
    """
    Convenience wrapper for destination search.
    """

    return search_service.search_destinations(
        destinations=destinations,
        query=query,
        page=page,
        per_page=per_page,
    )


def search_blog_posts(
    posts,
    query: str,
    page: int = 1,
    per_page: Optional[int] = None,
) -> SearchResponse:
    """
    Convenience wrapper for blog search.
    """

    return search_service.search_blog_posts(
        posts=posts,
        query=query,
        page=page,
        per_page=per_page,
    )


def search_wildlife(
    species,
    query: str,
    page: int = 1,
    per_page: Optional[int] = None,
) -> SearchResponse:
    """
    Convenience wrapper for wildlife search.
    """

    return search_service.search_wildlife(
        species=species,
        query=query,
        page=page,
        per_page=per_page,
    )


def global_search(
    query: str,
    experiences=None,
    destinations=None,
    posts=None,
    wildlife=None,
    page: int = 1,
    per_page: Optional[int] = None,
) -> SearchResponse:
    """
    Convenience wrapper for global search.
    """

    return search_service.global_search(
        query=query,
        experiences=experiences,
        destinations=destinations,
        posts=posts,
        wildlife=wildlife,
        page=page,
        per_page=per_page,
    )