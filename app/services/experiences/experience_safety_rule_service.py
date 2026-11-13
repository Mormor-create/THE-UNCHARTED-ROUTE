"""
===============================================================================
The Uncharted Route
Experience Safety Rule Service
===============================================================================

Business logic for managing safety guidelines attached to experiences.

Responsibilities
----------------

• Create safety rules
• Retrieve safety rules
• Update safety rules
• Delete safety rules
• Activate / deactivate rules
• Filter rules by category
• Filter rules by priority
• Retrieve critical/high-priority rules
• Reorder safety rules
• Count safety rules
"""

from extensions import db
from app.models import Experience, ExperienceSafetyRule

# =============================================================================
# Constants
# =============================================================================

VALID_PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical",
]

VALID_CATEGORIES = [
    "Wildlife",
    "Health",
    "Hiking",
    "Water Safety",
    "Transport",
    "Weather",
    "Emergency",
    "General",
]


# =============================================================================
# Validation
# =============================================================================

def validate_safety_rule_data(data):
    """
    Validate safety rule input data.
    """

    if not data:
        raise ValueError("Safety rule data is required.")

    title = data.get("title")

    if not title:
        raise ValueError(
            "Safety rule title is required."
        )

    priority = data.get(
        "priority",
        "Medium"
    )

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority: {priority}."
        )

    category = data.get(
        "category",
        "General"
    )

    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category: {category}."
        )

    return {
        "title": title.strip(),
        "description": data.get("description"),
        "category": category,
        "priority": priority,
        "icon": data.get(
            "icon",
            "shield-check"
        ),
        "display_order": data.get(
            "display_order",
            0
        ),
        "active": data.get(
            "active",
            True
        ),
    }


# =============================================================================
# Experience Helpers
# =============================================================================

def get_experience(experience_id):
    """
    Retrieve an experiences by ID.
    """

    return db.session.get(
        Experience,
        experience_id
    )


# =============================================================================
# Create
# =============================================================================

def create_safety_rule(
    experience_id,
    data,
):
    """
    Create a safety rule for an experiences.
    """

    experience = get_experience(
        experience_id
    )

    if not experience:
        raise ValueError(
            "Experience not found."
        )

    validated = validate_safety_rule_data(
        data
    )

    rule = ExperienceSafetyRule(
        experience_id=experience_id,
        **validated
    )

    db.session.add(rule)
    db.session.commit()

    return rule


# =============================================================================
# Retrieve
# =============================================================================

def get_safety_rule(rule_id):
    """
    Retrieve a safety rule by ID.
    """

    return db.session.get(
        ExperienceSafetyRule,
        rule_id
    )


def get_experience_safety_rules(
    experience_id,
    active_only=False,
):
    """
    Retrieve safety rules belonging to an experiences.
    """

    query = ExperienceSafetyRule.query.filter_by(
        experience_id=experience_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceSafetyRule.display_order.asc(),
        ExperienceSafetyRule.created_at.asc()
    ).all()


# =============================================================================
# Category Filtering
# =============================================================================

def get_rules_by_category(
    experience_id,
    category,
    active_only=True,
):
    """
    Retrieve safety rules belonging to a category.
    """

    query = ExperienceSafetyRule.query.filter_by(
        experience_id=experience_id,
        category=category,
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceSafetyRule.display_order.asc()
    ).all()


# =============================================================================
# Priority Filtering
# =============================================================================

def get_rules_by_priority(
    experience_id,
    priority,
    active_only=True,
):
    """
    Retrieve safety rules by priority.
    """

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority: {priority}."
        )

    query = ExperienceSafetyRule.query.filter_by(
        experience_id=experience_id,
        priority=priority,
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceSafetyRule.display_order.asc()
    ).all()


# =============================================================================
# High Priority Rules
# =============================================================================

def get_high_priority_rules(
    experience_id,
    active_only=True,
):
    """
    Retrieve High and Critical safety rules.
    """

    query = ExperienceSafetyRule.query.filter(
        ExperienceSafetyRule.experience_id == experience_id,
        ExperienceSafetyRule.priority.in_([
            "High",
            "Critical",
        ])
    )

    if active_only:
        query = query.filter(
            ExperienceSafetyRule.active.is_(True)
        )

    return query.order_by(
        ExperienceSafetyRule.display_order.asc()
    ).all()


def get_critical_rules(
    experience_id,
    active_only=True,
):
    """
    Retrieve Critical safety rules.
    """

    query = ExperienceSafetyRule.query.filter_by(
        experience_id=experience_id,
        priority="Critical",
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceSafetyRule.display_order.asc()
    ).all()


# =============================================================================
# Update
# =============================================================================

def update_safety_rule(
    rule_id,
    data,
):
    """
    Update an existing safety rule.
    """

    rule = get_safety_rule(
        rule_id
    )

    if not rule:
        raise ValueError(
            "Safety rule not found."
        )

    validated = validate_safety_rule_data(
        data
    )

    for field, value in validated.items():
        setattr(
            rule,
            field,
            value
        )

    db.session.commit()

    return rule


# =============================================================================
# Partial Update
# =============================================================================

def update_safety_rule_fields(
    rule_id,
    **fields,
):
    """
    Update selected safety rule fields.

    Useful when an admin only wants to change one or two fields.
    """

    rule = get_safety_rule(
        rule_id
    )

    if not rule:
        raise ValueError(
            "Safety rule not found."
        )

    allowed_fields = {
        "title",
        "description",
        "category",
        "priority",
        "icon",
        "display_order",
        "active",
    }

    invalid_fields = set(fields) - allowed_fields

    if invalid_fields:
        raise ValueError(
            "Invalid fields: "
            + ", ".join(sorted(invalid_fields))
        )

    if "title" in fields:

        if not fields["title"]:
            raise ValueError(
                "Safety rule title cannot be empty."
            )

        fields["title"] = fields["title"].strip()

    if "category" in fields:

        if fields["category"] not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {fields['category']}."
            )

    if "priority" in fields:

        if fields["priority"] not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority: {fields['priority']}."
            )

    for field, value in fields.items():
        setattr(
            rule,
            field,
            value
        )

    db.session.commit()

    return rule


# =============================================================================
# Activation
# =============================================================================

def activate_safety_rule(rule_id):
    """
    Activate a safety rule.
    """

    rule = get_safety_rule(
        rule_id
    )

    if not rule:
        raise ValueError(
            "Safety rule not found."
        )

    rule.active = True

    db.session.commit()

    return rule


def deactivate_safety_rule(rule_id):
    """
    Deactivate a safety rule without deleting it.
    """

    rule = get_safety_rule(
        rule_id
    )

    if not rule:
        raise ValueError(
            "Safety rule not found."
        )

    rule.active = False

    db.session.commit()

    return rule


def toggle_safety_rule(rule_id):
    """
    Toggle the active state of a safety rule.
    """

    rule = get_safety_rule(
        rule_id
    )

    if not rule:
        raise ValueError(
            "Safety rule not found."
        )

    rule.active = not rule.active

    db.session.commit()

    return rule


# =============================================================================
# Reordering
# =============================================================================

def reorder_safety_rule(
    rule_id,
    display_order,
):
    """
    Change the display order of a safety rule.
    """

    rule = get_safety_rule(
        rule_id
    )

    if not rule:
        raise ValueError(
            "Safety rule not found."
        )

    if display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    rule.display_order = display_order

    db.session.commit()

    return rule


def reorder_safety_rules(
    experience_id,
    ordered_rule_ids,
):
    """
    Reorder multiple safety rules.

    Parameters
    ----------
    experience_id:
        Experience whose rules are being reordered.

    ordered_rule_ids:
        List of rule IDs in their desired order.

    Example
    -------
    [5, 2, 8, 1]
    """

    rules = ExperienceSafetyRule.query.filter(
        ExperienceSafetyRule.experience_id == experience_id,
        ExperienceSafetyRule.id.in_(
            ordered_rule_ids
        )
    ).all()

    rules_by_id = {
        rule.id: rule
        for rule in rules
    }

    for position, rule_id in enumerate(
        ordered_rule_ids
    ):

        rule = rules_by_id.get(
            rule_id
        )

        if rule:
            rule.display_order = position

    db.session.commit()

    return get_experience_safety_rules(
        experience_id
    )


# =============================================================================
# Counts
# =============================================================================

def count_safety_rules(
    experience_id,
    active_only=False,
):
    """
    Count safety rules for an experiences.
    """

    query = ExperienceSafetyRule.query.filter_by(
        experience_id=experience_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.count()


def count_rules_by_priority(
    experience_id,
    priority,
):
    """
    Count safety rules by priority.
    """

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority: {priority}."
        )

    return ExperienceSafetyRule.query.filter_by(
        experience_id=experience_id,
        priority=priority,
        active=True,
    ).count()


# =============================================================================
# Delete
# =============================================================================

def delete_safety_rule(rule_id):
    """
    Permanently delete a safety rule.
    """

    rule = get_safety_rule(
        rule_id
    )

    if not rule:
        raise ValueError(
            "Safety rule not found."
        )

    db.session.delete(rule)
    db.session.commit()

    return True