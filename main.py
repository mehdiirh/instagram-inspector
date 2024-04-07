import os.path

if __name__ == "__main__":
    if not os.path.exists("database.sqlite3"):
        raise ValueError(
            "Database not found. copy database-sample.sqlite3 and rename it to database.sqlite3"
        )

    # importing telegram will execute program
    from telegram import main  # noqa
