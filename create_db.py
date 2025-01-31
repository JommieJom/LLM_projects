import sqlite3
import csv

db_file = "sleep.db"
csv_file = "sleep_health_lifestyle_dataset.csv"
table_name = "sleep_data"  # Choose a suitable table name

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create the table (assuming you know the column names and types)
#  Replace with your actual column names and datatypes (e.g., TEXT, INTEGER, REAL)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS sleep_data (
        "Person ID" INTEGER,
        Gender TEXT,
        Age INTEGER,
        Occupation TEXT,
        "Sleep Duration (hours)" REAL,
        "Quality of Sleep (scale: 1-10)" REAL,
        "Physical Activity Level (minutes/day)" INTEGER,
        "Stress Level (scale: 1-10)" INTEGER,
        "BMI Category" TEXT,
        "Blood Pressure (systolic/diastolic)" TEXT,
        "Heart Rate (bpm)" INTEGER,
        "Daily Steps" INTEGER,
        "Sleep Disorder" TEXT
    )
"""
)

with open(csv_file, "r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row if present

    for row in reader:
        # Prepare the SQL INSERT statement dynamically
        placeholders = ",".join(["?"] * len(row))
        cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

conn.commit()
conn.close()

print(f"Data inserted into {db_file} successfully.")
