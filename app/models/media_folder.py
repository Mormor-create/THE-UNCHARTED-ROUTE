"""
===============================================================================
The Uncharted Route
Media Folder Model
===============================================================================
Hierarchical organization system for the Central Digital Asset Management
(DAM) library.
A MediaFolder determines WHERE media assets are organized.

Examples:

    Homepage
        ├── Hero
        ├── Featured Experiences
        └── Destinations

    Experiences
        ├── Wildlife & Conservation
        ├── Adventure & Outdoors
        ├── Culture & Heritage
        └── Coastal & Beach

    Destinations
        ├── Nairobi
        ├── Maasai Mara
        ├── Amboseli
        └── Samburu

    Stays
        └── JW Marriott
            ├── Hero
            ├── Gallery
            └── Rooms
                ├── Deluxe Room
                └── Presidential Suite

A folder may contain child folders, allowing the DAM to scale to a large
media library without requiring duplicate uploads.
"""

from datetime import datetime
from extensions import db

class MediaFolder(db.Model):
    """
    Hierarchical folder used to organize MediaAsset records.

    A folder may have a parent folder, allowing structures such as:

        Destinations
            └── Nairobi

        Experiences
            └── Wildlife & Conservation

        Stays
            └── JW Marriott
                └── Rooms
                    └── Deluxe Room
    """

    __tablename__ = "media_folders"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True,)

    # =========================================================================
    # Basic Information
    # =========================================================================
    name = db.Column(db.String(150),nullable=False,)
    slug = db.Column(db.String(180),nullable=False,unique=True,index=True,)
    description = db.Column(db.Text,)

    # =========================================================================
    # Hierarchy
    # =========================================================================
    parent_id = db.Column(
        db.Integer,db.ForeignKey(
            "media_folders.id",
            ondelete="SET NULL",),nullable=True,index=True,)
    parent = db.relationship("MediaFolder",remote_side=[id],back_populates="children",)
    children = db.relationship(
        "MediaFolder",
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="MediaFolder.display_order",
        lazy="dynamic",)

    # =========================================================================
    # Classification
    # =========================================================================
    #
    # These values describe the role of the folder in the DAM.
    #
    # Supported values currently used by the media service:
    #
    # general
    # hero
    # destination
    # experience
    # experience_category
    # stay
    # stay_room
    # icon
    # logo
    # social
    # document
    # Root folders such as "Homepage", "Experiences", "Destinations",
    # "Stays", "Site", and "Social" can therefore be classified according
    # to their purpose.
    folder_type = db.Column(db.String(50),nullable=False,default="general",)

    # =========================================================================
    # Display
    # =========================================================================
    display_order = db.Column(db.Integer,nullable=False,default=0,)
    active = db.Column(db.Boolean,nullable=False,default=True,)

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False,)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False,)

    # =========================================================================
    # Media Asset Relationships
    # =========================================================================
    assets = db.relationship(
        "MediaAssetFolder",
        back_populates="folder",
        cascade="all, delete-orphan",
        lazy="dynamic",)

    # =========================================================================
    # Properties
    # =========================================================================
    @property
    def asset_count(self):
        """
        Return the number of media assets directly assigned to this folder.
        This does not include assets assigned only to child folders.
        """
        return self.assets.count()

    @property
    def total_asset_count(self):
        """
        Return the total number of media assets contained in this folder
        and all descendant folders.
        """

        total = self.asset_count
        for child in self.children.all():
            total += child.total_asset_count
        return total

    @property
    def full_path(self):
        """
        Return the complete human-readable folder path.
        Example:
            Destinations / Nairobi

        Or:
            Stays / JW Marriott / Rooms / Deluxe Room
        """
        parts = []
        current = self
        while current is not None:
            parts.append(current.name)
            current = current.parent
        return " / ".join(reversed(parts))

    @property
    def is_root(self):
        """
        Return True when this folder has no parent.
        """
        return self.parent_id is None

    @property
    def child_count(self):
        """
        Return the number of direct child folders.
        """
        return self.children.count()

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return f"<MediaFolder {self.full_path}>"