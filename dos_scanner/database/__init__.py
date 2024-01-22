import sqlite3

# Create in-memory sqlite3 database connection
connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

# Create an Endpoint table
cursor.execute(
    """
    CREATE TABLE Endpoint (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL
    )
"""
)

# Commit the changes to the database
connection.commit()

# Close the cursor
cursor.close()

# Export the connection to be used by other modules
__all__ = ["connection"]
