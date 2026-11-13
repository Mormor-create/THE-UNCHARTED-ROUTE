"""
===============================================================================
The Uncharted Route
SQLAlchemy Model Integrity Checker
===============================================================================
"""

import os
import sys


# =============================================================================
# Add Project Root To Python Path
# =============================================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# =============================================================================
# Application Imports
# =============================================================================

from app import create_app
from extensions import db


# =============================================================================
# Main
# =============================================================================

def main():

    print()
    print("=" * 79)
    print("THE UNCHARTED ROUTE")
    print("SQLAlchemy Model Integrity Check")
    print("=" * 79)
    print()

    print("→ Creating Flask application...")

    try:
        app = create_app()

        print("  ✅ Flask application created")
        print()

    except Exception as error:

        print()
        print("❌ APPLICATION INITIALIZATION FAILED")
        print()
        print(error)
        print()

        raise SystemExit(1)

    print("→ Configuring SQLAlchemy mappers...")

    try:

        with app.app_context():

            db.configure_mappers()

        print("  ✅ All SQLAlchemy mappers configured")
        print()

    except Exception as error:

        print()
        print("❌ MODEL CONFIGURATION FAILED")
        print()
        print(error)
        print()

        raise SystemExit(1)

    print("→ Inspecting registered database tables...")
    print()

    tables = sorted(
        db.metadata.tables.keys()
    )

    if not tables:

        print("❌ No database tables were registered.")

        raise SystemExit(1)

    for table_name in tables:

        print(
            f"  ✅ {table_name}"
        )

    print()

    print("=" * 79)
    print(
        f"✅ MODEL CHECK PASSED — "
        f"{len(tables)} TABLES REGISTERED"
    )
    print("=" * 79)
    print()


if __name__ == "__main__":
    main()