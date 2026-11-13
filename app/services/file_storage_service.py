"""
===============================================================================
The Uncharted Route
File Storage Service
===============================================================================

Centralized service for handling uploaded files and media.

Responsibilities

• Validate uploaded files
• Generate safe filenames
• Store files in organized directories
• Delete stored files
• Generate file URLs
• Prevent unsafe file uploads
• Provide reusable storage utilities

This service is intentionally independent of any specific model so it can
be used by experiences, blog posts, destinations, testimonials, users,
conservation stories, galleries, and other modules.
"""

import os
import uuid
from pathlib import Path
from typing import Iterable, Optional

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_UPLOAD_FOLDER = "app/static/uploads"

DEFAULT_ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",
    "svg",
    "pdf",
    "mp4",
    "webm",
    "mov",
}

DEFAULT_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",
    "svg",
}

DEFAULT_VIDEO_EXTENSIONS = {
    "mp4",
    "webm",
    "mov",
}

DEFAULT_DOCUMENT_EXTENSIONS = {
    "pdf",
}


# =============================================================================
# Exceptions
# =============================================================================

class FileStorageError(Exception):
    """
    Base exception for file storage errors.
    """


class InvalidFileError(FileStorageError):
    """
    Raised when an uploaded file is invalid.
    """


class UnsupportedFileTypeError(FileStorageError):
    """
    Raised when a file extension is not allowed.
    """


class FileTooLargeError(FileStorageError):
    """
    Raised when a file exceeds the configured size limit.
    """


# =============================================================================
# File Storage Service
# =============================================================================

class FileStorageService:
    """
    Centralized file upload and storage manager.
    """

    def __init__(
        self,
        upload_folder: Optional[str] = None,
        base_url: str = "/static/uploads",
        allowed_extensions: Optional[Iterable[str]] = None,
        max_file_size: int = 20 * 1024 * 1024,
    ):
        """
        Initialize the storage service.

        Args:
            upload_folder:
                Physical directory where files are stored.

            base_url:
                Public URL prefix used when generating file URLs.

            allowed_extensions:
                Collection of permitted file extensions.

            max_file_size:
                Maximum file size in bytes.
                Default: 20 MB.
        """

        self.upload_folder = Path(
            upload_folder or DEFAULT_UPLOAD_FOLDER
        )

        self.base_url = base_url.rstrip("/")

        self.allowed_extensions = {
            extension.lower().lstrip(".")
            for extension in (
                allowed_extensions
                or DEFAULT_ALLOWED_EXTENSIONS
            )
        }

        self.max_file_size = max_file_size

    # =========================================================================
    # Directory Management
    # =========================================================================

    def ensure_directory(
        self,
        directory: Optional[str] = None,
    ) -> Path:
        """
        Ensure that a storage directory exists.
        """

        path = (
            Path(directory)
            if directory
            else self.upload_folder
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def get_directory(
        self,
        category: str = "general",
    ) -> Path:
        """
        Return and create a category-specific storage directory.

        Example:

            uploads/
                experiences/
                blog/
                destinations/
                users/
                testimonials/
        """

        safe_category = secure_filename(
            category
        ).lower()

        if not safe_category:
            safe_category = "general"

        return self.ensure_directory(
            self.upload_folder / safe_category
        )

    # =========================================================================
    # File Validation
    # =========================================================================

    def validate_file(
        self,
        file: FileStorage,
    ) -> bool:
        """
        Validate an uploaded file.
        """

        if not file:
            raise InvalidFileError(
                "No file was provided."
            )

        if not file.filename:
            raise InvalidFileError(
                "The uploaded file has no filename."
            )

        extension = self.get_extension(
            file.filename
        )

        if not extension:
            raise UnsupportedFileTypeError(
                "The uploaded file has no extension."
            )

        if extension not in self.allowed_extensions:
            raise UnsupportedFileTypeError(
                f"File type '.{extension}' is not allowed."
            )

        self.validate_file_size(file)

        return True

    def validate_file_size(
        self,
        file: FileStorage,
    ) -> bool:
        """
        Validate the size of an uploaded file.
        """

        try:
            current_position = file.stream.tell()

            file.stream.seek(
                0,
                os.SEEK_END
            )

            size = file.stream.tell()

            file.stream.seek(
                current_position
            )

        except (OSError, AttributeError):
            return True

        if size > self.max_file_size:
            raise FileTooLargeError(
                "The uploaded file exceeds the "
                f"maximum allowed size of "
                f"{self.max_file_size // (1024 * 1024)} MB."
            )

        return True

    # =========================================================================
    # Filename Utilities
    # =========================================================================

    @staticmethod
    def get_extension(
        filename: str,
    ) -> str:
        """
        Return a lowercase file extension without the dot.
        """

        if not filename:
            return ""

        return Path(filename).suffix.lower().lstrip(".")

    @staticmethod
    def generate_filename(
        original_filename: str,
        prefix: Optional[str] = None,
    ) -> str:
        """
        Generate a unique and secure filename.

        Example:

            hero-image.jpg

        becomes something similar to:

            hero-image-a8f4d92c.jpg
        """

        extension = Path(
            original_filename
        ).suffix.lower()

        original_name = Path(
            original_filename
        ).stem

        safe_name = secure_filename(
            original_name
        )

        if not safe_name:
            safe_name = "file"

        unique_id = uuid.uuid4().hex[:12]

        if prefix:
            safe_prefix = secure_filename(
                prefix
            )

            if safe_prefix:
                safe_name = (
                    f"{safe_prefix}-{safe_name}"
                )

        return (
            f"{safe_name}-"
            f"{unique_id}"
            f"{extension}"
        )

    # =========================================================================
    # Saving Files
    # =========================================================================

    def save(
        self,
        file: FileStorage,
        category: str = "general",
        prefix: Optional[str] = None,
    ) -> str:
        """
        Validate and save an uploaded file.

        Returns:
            Relative storage path.

        Example:

            experiences/nairobi-national-park-a8f4d92c.jpg
        """

        self.validate_file(file)

        directory = self.get_directory(
            category
        )

        filename = self.generate_filename(
            file.filename,
            prefix=prefix,
        )

        destination = directory / filename

        file.save(destination)

        return str(
            Path(category) / filename
        ).replace("\\", "/")

    # =========================================================================
    # Replacing Files
    # =========================================================================

    def replace(
        self,
        file: FileStorage,
        old_file: Optional[str] = None,
        category: str = "general",
        prefix: Optional[str] = None,
    ) -> str:
        """
        Replace an existing file with a newly uploaded file.
        """

        new_file = self.save(
            file=file,
            category=category,
            prefix=prefix,
        )

        if old_file:
            self.delete(old_file)

        return new_file

    # =========================================================================
    # Deleting Files
    # =========================================================================

    def delete(
        self,
        file_path: Optional[str],
    ) -> bool:
        """
        Delete a stored file.

        Returns:
            True if deleted, False if the file did not exist.
        """

        if not file_path:
            return False

        path = self.resolve_path(
            file_path
        )

        if not path.exists():
            return False

        if not path.is_file():
            return False

        try:
            path.unlink()
            return True

        except OSError as exc:
            raise FileStorageError(
                f"Unable to delete file: {file_path}"
            ) from exc

    # =========================================================================
    # Path Utilities
    # =========================================================================

    def resolve_path(
        self,
        file_path: str,
    ) -> Path:
        """
        Resolve a relative storage path safely.

        Prevents paths from escaping the upload directory.
        """

        relative_path = Path(
            file_path
        )

        if relative_path.is_absolute():
            raise FileStorageError(
                "Absolute file paths are not allowed."
            )

        base = self.upload_folder.resolve()

        target = (
            self.upload_folder / relative_path
        ).resolve()

        if (
            target != base
            and base not in target.parents
        ):
            raise FileStorageError(
                "Invalid file path."
            )

        return target

    def exists(
        self,
        file_path: Optional[str],
    ) -> bool:
        """
        Check whether a stored file exists.
        """

        if not file_path:
            return False

        return self.resolve_path(
            file_path
        ).is_file()

    # =========================================================================
    # URL Utilities
    # =========================================================================

    def url(
        self,
        file_path: Optional[str],
    ) -> Optional[str]:
        """
        Generate a public URL for a stored file.
        """

        if not file_path:
            return None

        normalized_path = str(
            file_path
        ).replace("\\", "/").lstrip("/")

        return (
            f"{self.base_url}/"
            f"{normalized_path}"
        )

    # =========================================================================
    # File Type Helpers
    # =========================================================================

    @staticmethod
    def is_image(
        filename: str,
    ) -> bool:
        """
        Determine whether a file is an image.
        """

        extension = FileStorageService.get_extension(
            filename
        )

        return extension in DEFAULT_IMAGE_EXTENSIONS

    @staticmethod
    def is_video(
        filename: str,
    ) -> bool:
        """
        Determine whether a file is a video.
        """

        extension = FileStorageService.get_extension(
            filename
        )

        return extension in DEFAULT_VIDEO_EXTENSIONS

    @staticmethod
    def is_document(
        filename: str,
    ) -> bool:
        """
        Determine whether a file is a document.
        """

        extension = FileStorageService.get_extension(
            filename
        )

        return extension in DEFAULT_DOCUMENT_EXTENSIONS

    # =========================================================================
    # Size Utilities
    # =========================================================================

    @staticmethod
    def format_size(
        size_bytes: int,
    ) -> str:
        """
        Convert bytes into a human-readable size.
        """

        if size_bytes < 1024:
            return f"{size_bytes} B"

        if size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"

        if size_bytes < 1024 ** 3:
            return (
                f"{size_bytes / (1024 ** 2):.1f} MB"
            )

        return (
            f"{size_bytes / (1024 ** 3):.1f} GB"
        )


# =============================================================================
# Default Service Instance
# =============================================================================

file_storage_service = FileStorageService()


# =============================================================================
# Convenience Functions
# =============================================================================

def save_file(
    file: FileStorage,
    category: str = "general",
    prefix: Optional[str] = None,
) -> str:
    """
    Save a file using the default storage service.
    """

    return file_storage_service.save(
        file=file,
        category=category,
        prefix=prefix,
    )


def delete_file(
    file_path: Optional[str],
) -> bool:
    """
    Delete a stored file using the default storage service.
    """

    return file_storage_service.delete(
        file_path
    )


def replace_file(
    file: FileStorage,
    old_file: Optional[str] = None,
    category: str = "general",
    prefix: Optional[str] = None,
) -> str:
    """
    Replace a stored file using the default storage service.
    """

    return file_storage_service.replace(
        file=file,
        old_file=old_file,
        category=category,
        prefix=prefix,
    )


def file_url(
    file_path: Optional[str],
) -> Optional[str]:
    """
    Generate a public URL using the default storage service.
    """

    return file_storage_service.url(
        file_path
    )