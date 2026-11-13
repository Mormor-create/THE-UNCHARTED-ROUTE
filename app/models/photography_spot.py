from datetime import datetime
from extensions import db

class PhotographySpot(db.Model):
    """Stores reusable photography locations."""

    __tablename__ = "photography_spots"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Basic information
    name = db.Column(db.String(255), nullable=False, unique=True)
    slug = db.Column(db.String(255), unique=True, index=True)
    description = db.Column(db.Text)

    # Destination and specific location
    destination_id = db.Column(
        db.Integer,
        db.ForeignKey("destinations.id"),
        nullable=True,
        index=True,
    )
    location = db.Column(db.String(255))
    destination = db.relationship("Destination")

    # Coordinates
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude = db.Column(db.Integer)

    # Photography information
    photography_type = db.Column(db.String(100))
    difficulty = db.Column(db.String(50), default="Easy")

    # Photography timing
    best_time = db.Column(db.String(255))
    best_time_to_visit = db.Column(db.String(255))
    best_time_to_photograph = db.Column(db.String(255))
    best_season = db.Column(db.String(255))

    # Photography equipment
    recommended_lens = db.Column(db.String(255))
    recommended_lenses = db.Column(db.Text)
    recommended_equipment = db.Column(db.Text)

    # Photography conditions
    lighting_conditions = db.Column(db.Text)
    weather_conditions = db.Column(db.Text)

    # Camera guidance
    camera_settings = db.Column(db.Text)

    # Visitor information
    accessibility = db.Column(db.String(100))
    photography_tips = db.Column(db.Text)
    safety_notes = db.Column(db.Text)

    # Display
    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )
    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    # Experience associations
    experiences = db.relationship(
        "ExperiencePhotography",
        back_populates="spot",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # Audit fields
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    @property
    def experience_count(self):
        return self.experiences.count()

    @property
    def has_coordinates(self):
        return (
            self.latitude is not None
            and self.longitude is not None
        )

    def __repr__(self):
        return f"<PhotographySpot {self.name}>"
