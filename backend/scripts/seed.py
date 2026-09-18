import sys
from pathlib import Path


# Add backend/ to Python path.
BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_DIR),
    )


from app.core.database import (
    SessionLocal,
    init_db,
)

from app.seed.loader import (
    seed_database,
)


def main():
    """
    Initialise the database and load seed data.
    """

    print("\nInitialising database...")

    init_db()

    db = SessionLocal()

    try:
        seed_database(db)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()