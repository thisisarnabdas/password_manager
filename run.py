import os
from pathlib import Path
from app import app, db
from flask_migrate import upgrade

# base directory and paths for the database folder and file
base_dir = Path(__file__).parent
db_folder = base_dir / 'database'
db_file_path = db_folder / 'app.db'

print(f"Database folder: {db_folder}")
print(f"Database path: {db_file_path}")

# Ensure the database folder exists
os.makedirs(db_folder, exist_ok=True)  # Creates the folder if it doesn't exist
print(f"Database folder created at: {db_folder}")

# Initializing the database if it doesn't exist and apply migrations
with app.app_context():
    if not db_file_path.exists():  # Checking if the database file exists
        print("Creating the database...")
        db.create_all()  # Creating tables if they don't exist
        print("Database created!")
    else:
        print("Database already exists.")

    # Applying migrations to ensure the database schema is up-to-date
    try:
        upgrade()  # This applies any pending migrations
        print("Database migrations applied.")
    except Exception as e:
        print(f"Error applying migrations: {e}")

if __name__ == "__main__":
    app.run(debug=True)
