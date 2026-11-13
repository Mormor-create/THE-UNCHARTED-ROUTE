"""
===============================================================================
The Uncharted Route
Experience Requirement Service
===============================================================================

Business logic for managing participation requirements attached to experiences.

Responsibilities
----------------

• Create experiences requirements
• Retrieve requirements
• Filter requirements by experiences
• Update requirements
• Delete requirements
• Activate / deactivate requirements
• Mark requirements as mandatory / optional
• Reorder requirements
• Retrieve mandatory requirements
• Retrieve active requirements
"""

from extensions import db

from app.models import ExperienceRequirement
from app.models.experience import Experience


# =============================================================================
# Experience Requirement Service
# =============================================================================


class ExperienceRequirementService:
    """
    Service layer for ExperienceRequirement operations.
    """

    # =========================================================================
    # CREATE
    # =========================================================================

    @staticmethod
    def create_requirement(
        experience_id,
        title,
        description=None,
        category="General",
        mandatory=True,
        icon="clipboard-check",
        display_order=0,
        active=True
    ):
        """
        Create a new participation requirement for an experiences.

        Parameters
        ----------
        experience_id : int
            ID of the experiences.

        title : str
            Requirement title.

        description : str, optional
            Detailed explanation.

        category : str
            Requirement category.

        mandatory : bool
            Whether the requirement is mandatory.

        icon : str
            Display icon.

        display_order : int
            Ordering position.

        active : bool
            Whether the requirement is active.

        Returns
        -------
        ExperienceRequirement
            Created requirement.

        Raises
        ------
        ValueError
            If the experiences does not exist or title is invalid.
        """

        if not title or not title.strip():
            raise ValueError(
                "Requirement title is required."
            )

        experience = Experience.query.get(experience_id)

        if not experience:
            raise ValueError(
                "Experience not found."
            )

        requirement = ExperienceRequirement(
            experience_id=experience_id,
            title=title.strip(),
            description=description,
            category=category or "General",
            mandatory=mandatory,
            icon=icon or "clipboard-check",
            display_order=display_order,
            active=active
        )

        db.session.add(requirement)
        db.session.commit()

        return requirement

    # =========================================================================
    # GET BY ID
    # =========================================================================

    @staticmethod
    def get_requirement(requirement_id):
        """
        Retrieve a requirement by ID.
        """

        return ExperienceRequirement.query.get(
            requirement_id
        )

    # =========================================================================
    # GET BY EXPERIENCE
    # =========================================================================

    @staticmethod
    def get_experience_requirements(
        experience_id,
        active_only=False,
        mandatory_only=False
    ):
        """
        Retrieve requirements belonging to an experiences.

        Results are ordered by display_order.
        """

        query = ExperienceRequirement.query.filter_by(
            experience_id=experience_id
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        if mandatory_only:
            query = query.filter_by(
                mandatory=True
            )

        return query.order_by(
            ExperienceRequirement.display_order.asc(),
            ExperienceRequirement.id.asc()
        ).all()

    # =========================================================================
    # GET ACTIVE REQUIREMENTS
    # =========================================================================

    @staticmethod
    def get_active_requirements(experience_id):
        """
        Return all active requirements for an experiences.
        """

        return ExperienceRequirementService.get_experience_requirements(
            experience_id=experience_id,
            active_only=True
        )

    # =========================================================================
    # GET MANDATORY REQUIREMENTS
    # =========================================================================

    @staticmethod
    def get_mandatory_requirements(experience_id):
        """
        Return mandatory requirements for an experiences.
        """

        return ExperienceRequirementService.get_experience_requirements(
            experience_id=experience_id,
            active_only=True,
            mandatory_only=True
        )

    # =========================================================================
    # UPDATE
    # =========================================================================

    @staticmethod
    def update_requirement(
        requirement_id,
        title=None,
        description=None,
        category=None,
        mandatory=None,
        icon=None,
        display_order=None,
        active=None
    ):
        """
        Update an existing experiences requirement.

        Only supplied fields are changed.
        """

        requirement = ExperienceRequirement.query.get(
            requirement_id
        )

        if not requirement:
            raise ValueError(
                "Requirement not found."
            )

        if title is not None:

            if not title.strip():
                raise ValueError(
                    "Requirement title cannot be empty."
                )

            requirement.title = title.strip()

        if description is not None:
            requirement.description = description

        if category is not None:
            requirement.category = category

        if mandatory is not None:
            requirement.mandatory = mandatory

        if icon is not None:
            requirement.icon = icon

        if display_order is not None:
            requirement.display_order = display_order

        if active is not None:
            requirement.active = active

        db.session.commit()

        return requirement

    # =========================================================================
    # ACTIVATE
    # =========================================================================

    @staticmethod
    def activate_requirement(requirement_id):
        """
        Activate a requirement.
        """

        requirement = ExperienceRequirement.query.get(
            requirement_id
        )

        if not requirement:
            raise ValueError(
                "Requirement not found."
            )

        requirement.active = True

        db.session.commit()

        return requirement

    # =========================================================================
    # DEACTIVATE
    # =========================================================================

    @staticmethod
    def deactivate_requirement(requirement_id):
        """
        Deactivate a requirement without deleting it.
        """

        requirement = ExperienceRequirement.query.get(
            requirement_id
        )

        if not requirement:
            raise ValueError(
                "Requirement not found."
            )

        requirement.active = False

        db.session.commit()

        return requirement

    # =========================================================================
    # MARK MANDATORY
    # =========================================================================

    @staticmethod
    def make_mandatory(requirement_id):
        """
        Mark a requirement as mandatory.
        """

        requirement = ExperienceRequirement.query.get(
            requirement_id
        )

        if not requirement:
            raise ValueError(
                "Requirement not found."
            )

        requirement.mandatory = True

        db.session.commit()

        return requirement

    # =========================================================================
    # MARK OPTIONAL
    # =========================================================================

    @staticmethod
    def make_optional(requirement_id):
        """
        Mark a requirement as optional.
        """

        requirement = ExperienceRequirement.query.get(
            requirement_id
        )

        if not requirement:
            raise ValueError(
                "Requirement not found."
            )

        requirement.mandatory = False

        db.session.commit()

        return requirement

    # =========================================================================
    # REORDER
    # =========================================================================

    @staticmethod
    def reorder_requirement(
        requirement_id,
        display_order
    ):
        """
        Change the display order of a requirement.
        """

        requirement = ExperienceRequirement.query.get(
            requirement_id
        )

        if not requirement:
            raise ValueError(
                "Requirement not found."
            )

        requirement.display_order = display_order

        db.session.commit()

        return requirement

    # =========================================================================
    # DELETE
    # =========================================================================

    @staticmethod
    def delete_requirement(requirement_id):
        """
        Permanently delete a requirement.
        """

        requirement = ExperienceRequirement.query.get(
            requirement_id
        )

        if not requirement:
            raise ValueError(
                "Requirement not found."
            )

        db.session.delete(requirement)
        db.session.commit()

        return True

    # =========================================================================
    # COUNT
    # =========================================================================

    @staticmethod
    def count_requirements(
        experience_id,
        active_only=False
    ):
        """
        Return the number of requirements attached to an experiences.
        """

        query = ExperienceRequirement.query.filter_by(
            experience_id=experience_id
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.count()

    # =========================================================================
    # COUNT MANDATORY
    # =========================================================================

    @staticmethod
    def count_mandatory_requirements(
        experience_id
    ):
        """
        Return the number of mandatory requirements.
        """

        return ExperienceRequirement.query.filter_by(
            experience_id=experience_id,
            mandatory=True,
            active=True
        ).count()

    # =========================================================================
    # BULK REORDER
    # =========================================================================

    @staticmethod
    def bulk_reorder(requirement_orders):
        """
        Reorder multiple requirements.

        Parameters
        ----------
        requirement_orders : dict
            Example:

            {
                1: 0,
                5: 1,
                8: 2
            }

        Returns
        -------
        list
            Updated requirements.
        """

        updated = []

        for requirement_id, display_order in requirement_orders.items():

            requirement = ExperienceRequirement.query.get(
                requirement_id
            )

            if not requirement:
                continue

            requirement.display_order = display_order

            updated.append(requirement)

        db.session.commit()

        return updated