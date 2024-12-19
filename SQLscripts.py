### worked correctly


import mysql.connector
import requests

# API Endpoint
url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key=dZU00gRy0KfAS06TyK7hvodG4SMK1ClUD44W5o4M"
headers = {"accept": "application/json"}

# Fetch data from the API with timeout
try:
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from API: {e}")
    exit(1)

# Check if the request was successful
if response.status_code != 200:
    print(f"Error: Received status code {response.status_code} from API.")
    print(response.text)
    exit(1)

# Process the JSON data
data = response.json()

# Establish a connection to the MySQL database
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Replace with your actual password
        database="sports_tennis"
    )
    mycursor = connection.cursor()

    # Set lock wait timeout
    mycursor.execute("SET innodb_lock_wait_timeout = 600;")

    categories_to_insert = []
    batch_size = 100
    inserted_count = 0

    for competition in data["competitions"]:
        category = competition["category"]
        category_id = category["id"]
        category_name = category["name"]
        
        # Log category being processed
        print(f"Processing category_id: {category_id}, category_name: {category_name}")

        categories_to_insert.append((category_id, category_name))

        # Insert in batches
        if len(categories_to_insert) >= batch_size:
            try:
                # Use INSERT IGNORE to skip duplicates
                mycursor.executemany("""
                    INSERT IGNORE INTO Categories (category_id, category_name)
                    VALUES (%s, %s)
                """, categories_to_insert)
                connection.commit()
                inserted_count += mycursor.rowcount  # Count the successful inserts
                categories_to_insert = []  # Clear after batch insert
            except mysql.connector.Error as err:
                connection.rollback()
                print(f"Error inserting data: {err}")

    # Insert any remaining categories
    if categories_to_insert:
        try:
            mycursor.executemany("""
                INSERT IGNORE INTO Categories (category_id, category_name)
                VALUES (%s, %s)
            """, categories_to_insert)
            connection.commit()
            inserted_count += mycursor.rowcount  # Count the successful inserts
        except mysql.connector.Error as err:
            connection.rollback()
            print(f"Error inserting data: {err}")

    print(f"Inserted {inserted_count} rows into Categories table.")
finally:
    mycursor.close()
    connection.close()
