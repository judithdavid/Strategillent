
from sqlalchemy import inspect, text

from app.core.database import engine


def migrate():
    inspector = inspect(engine)

    columns = {
        column["name"]
        for column in inspector.get_columns(
            "transformation_dimensions"
        )
    }

    if "industries" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE transformation_dimensions "
                    "ADD COLUMN industries JSON "
                    "NOT NULL DEFAULT '[]'"
                )
            )
        print("Added transformation_dimensions.industries.")
    else:
        print("transformation_dimensions.industries already exists.")

    print("Transformation dimension migration completed.")


if __name__ == "__main__":
    migrate()
