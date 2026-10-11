
from sqlalchemy import inspect, text

from app.core.database import engine


columns = ["goals", "processes", "technology", "constraints"]

with engine.begin() as connection:
    inspector = inspect(connection)

    if not inspector.has_table("organisations"):
        raise RuntimeError(
            "Organisations table not found in the configured database."
        )

    existing = {
        column["name"]
        for column in inspector.get_columns("organisations")
    }

    for column in columns:
        if column not in existing:
            connection.execute(
                text(
                    f'ALTER TABLE organisations '
                    f'ADD COLUMN "{column}" JSON '
                    f"NOT NULL DEFAULT '[]'"
                )
            )
            print(f"Added: {column}")
        else:
            print(f"Already exists: {column}")

print("Migration completed.")
