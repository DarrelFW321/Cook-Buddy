import os
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG)

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

try:
    print("Starting connection...")
    connection = mysql.connector.connect(**db_config)
    print("Connected successfully!")
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



"""
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG)

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

try:
    print("Starting connection...")
    connection = mysql.connector.connect(**db_config)
    print("Connected successfully!")
except mysql.connector.Error as err:
    print(f"MySQL Error: {err}")
except Exception as e:
    print(f"Unexpected Error: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Connection closed.")

# try:
#     # Connect to the database
#     print("Starting connection...")
#     connection = mysql.connector.connect(**db_config)
#     print("Connection object created...")
#     cursor = connection.cursor()
#     print("Cursor object created...")
#     print("SUCCESS")

#     # Insert list into the database
#     insert_query = "INSERT INTO my_table (value) VALUES (%s)"
#     cursor.executemany(insert_query, [(item,) for item in examples])

#     # Commit the transaction
#     connection.commit()
#     print(f"Inserted {cursor.rowcount} rows successfully.")

# except mysql.connector.Error as err:
#     print(f"Error: {err}")
# finally:
#     if connection.is_connected():
#         cursor.close()
#         connection.close()
#         print("Connection closed.")
"""