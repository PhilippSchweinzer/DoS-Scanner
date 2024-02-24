import sqlite3

# Create in-memory sqlite3 database connection
connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

# Create an Endpoint table
cursor.execute(
    """
    CREATE TABLE Endpoint (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        http_method TEXT NOT NULL,
        UNIQUE(url, http_method)
    )
"""
)

# Commit the changes to the database and close the cursor
connection.commit()
cursor.close()

# Export the connection to be used by other modules
__all__ = ["connection"]
