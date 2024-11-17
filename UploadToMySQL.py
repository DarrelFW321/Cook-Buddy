import mysql.connector

# Database connection details
db_config = {
    "host": "your-db-endpoint.amazonaws.com",
    "user": "your-username",
    "password": "your-password",
    "database": "your-database-name",
}

# Connect to the database
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    print("Connected to the database!")
except mysql.connector.Error as err:
    print(f"Error: {err}")

# Example: Insert data into a table
try:
    cursor.execute("INSERT INTO your_table_name (column1, column2) VALUES (%s, %s)", ("value1", "value2"))
    connection.commit()  # Commit the transaction
    print("Data inserted successfully!")
except mysql.connector.Error as err:
    print(f"Error: {err}")

# Example: Fetch data from a table
try:
    cursor.execute("SELECT * FROM your_table_name")
    results = cursor.fetchall()  # Fetch all rows
    for row in results:
        print(row)
except mysql.connector.Error as err:
    print(f"Error: {err}")

cursor.close()
connection.close()