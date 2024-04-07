import os.path
import shutil

if __name__ == "__main__":
    if not os.path.exists("database.sqlite3"):
        shutil.copy("database-sample.sqlite3", "database.sqlite3")

    # importing telegram will execute program
    from telegram import main  # noqa
