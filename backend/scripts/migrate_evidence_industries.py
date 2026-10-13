from sqlalchemy import inspect, text

from app.core.database import engine


def migrate():
    inspector = inspect(engine)

    columns = {
        column["name"]
        for column in inspector.get_columns("evidence")
    }

    if "industries" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE evidence "
                    "ADD COLUMN industries JSON "
                    "NOT NULL DEFAULT '[]'"
                )
            )
        print("Added evidence.industries column.")
    else:
        print("evidence.industries already exists.")

    print("Evidence migration completed.")


if __name__ == "__main__":
    migrate()