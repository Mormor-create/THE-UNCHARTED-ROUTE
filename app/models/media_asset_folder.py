"""
===============================================================================
The Uncharted Route
Media Asset Folder Association
===============================================================================
Connects MediaAsset records to MediaFolder records.
An asset can belong to multiple folders.
Example:
    elephant.jpg
    Destinations / Amboseli
    Experiences / Wildlife & Conservation
    Heroes / Destinations
"""
from datetime import datetime
from extensions import db

class MediaAssetFolder(db.Model):
    """
    Association between a MediaAsset and a MediaFolder.
    """
    __tablename__ = "media_asset_folders"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Foreign Keys
    # =========================================================================
    media_asset_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_assets.id",
            ondelete="CASCADE"),
        nullable=False,
        index=True)

    folder_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_folders.id",
            ondelete="CASCADE"),
        nullable=False,
        index=True)

    # =========================================================================
    # Assignment Information
    # =========================================================================
    is_primary = db.Column(db.Boolean,nullable=False,default=False)

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)

    # =========================================================================
    # Relationships
    # =========================================================================
    media_asset = db.relationship("MediaAsset",back_populates="folder_assignments")
    folder = db.relationship("MediaFolder",back_populates="assets")

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<MediaAssetFolder "
            f"asset={self.media_asset_id} "
            f"folder={self.folder_id}>")