"""
===============================================================================
The Uncharted Route
Stay Room Media Model
===============================================================================

Associates a StayRoom with an existing MediaAsset.

Used for room-specific photographs and videos.
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Stay Room Media Model
# =============================================================================

class StayRoomMedia(db.Model):
    """
    Associates a room with a media asset.
    """

    __tablename__ = "stay_room_media"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Relationships
    # =========================================================================
    room_id = db.Column(db.Integer,db.ForeignKey("stay_rooms.id"),nullable=False,index=True)
    media_asset_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_assets.id"
        ),
        nullable=False,
        index=True
    )

    # =========================================================================
    # Usage
    # =========================================================================
    usage = db.Column(db.String(30),nullable=False,default="gallery")

    # hero
    # thumbnail
    # gallery

    display_order = db.Column(db.Integer,nullable=False,default=0)
    caption = db.Column(db.Text)

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =========================================================================
    # Relationships
    # =========================================================================
    room = db.relationship("StayRoom",back_populates="media")
    media_asset = db.relationship("MediaAsset",back_populates="stay_room_media")

    # =========================================================================
    # Audit Fields
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_image(self):
        return bool(
            self.media_asset
            and self.media_asset.is_image
        )

    @property
    def is_video(self):
        return bool(
            self.media_asset
            and self.media_asset.is_video
        )

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<StayRoomMedia "
            f"room={self.room_id} "
            f"media={self.media_asset_id}>"
        )