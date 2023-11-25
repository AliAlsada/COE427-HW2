import rticonnextdds_connector as rti
import sqlite3
import time
import os

def initialize_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('data.db')

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Define SQL query to create a table
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        heart_rate INTEGER,
        blood_pressure INTEGER,
        oxygen_saturation INTEGER,
        timestamp DATETIME
    );
    '''

    # Execute the query
    cursor.execute(create_table_query)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def insert_patient_data(data):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    insert_query = '''INSERT INTO patients 
                        (patient_id, heart_rate, blood_pressure, oxygen_saturation, timestamp)
                        VALUES (?, ?, ?, ?, ?)'''
    
    # 'data' is a dictionary with keys corresponding to the table columns
    cursor.execute(insert_query, (data['patient_id'], data['heart_rate'], 
                                  data['blood_pressure'], data['oxygen_saturation'], data['timestamp']))

    conn.commit()
    conn.close()


initialize_database()


def publish_data(server_input, server_output):
    while True:
        server_input.wait()  # Wait for data
        server_input.take()

        for sample in server_input.samples.valid_data_iter:
            # Process each valid data sample
            data = sample.get_dictionary()
            print("Received data:", data)

            # Insert data into the database
            insert_patient_data(data)

            # Forward data to healthcare providers
            server_output.instance.set_dictionary(data)
            server_output.write()



with rti.open_connector(
    config_name="DomainParticipantLibrary::Server_Participant",
    url="COE427-HW2.xml") as connector:

    server_input = connector.get_input("Server_Subscriber::Sensor_Reader")
    server_output = connector.get_output("Server_Publisher::Server_Writer")

    while True:
        server_input.wait()  # Wait for data
        server_input.take()

        for sample in server_input.samples.valid_data_iter:
            # Process each valid data sample
            data = sample.get_dictionary()
            print("Received data:", data)

            # Insert data into the database
            insert_patient_data(data)

            # Forward data to healthcare providers
            server_output.instance.set_dictionary(data)
            server_output.write()



        
