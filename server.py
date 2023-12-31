# Mohammad Al Ramis - 201920170
# Mohammed Althunayan – 201944590
# Ali Alsada – 201960570


import rticonnextdds_connector as rti
import threading
import sqlite3
import time
import os


lock = threading.RLock()

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


# Insert data into the database
def insert_patient_data(data):
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('data.db')
    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Define SQL query to insert data into the table
    insert_query = '''INSERT INTO patients 
                        (patient_id, heart_rate, blood_pressure, oxygen_saturation, timestamp)
                        VALUES (?, ?, ?, ?, ?)'''
    
    # 'data' is a dictionary with keys corresponding to the table columns
    cursor.execute(insert_query, (data['patient_id'], data['heart_rate'], 
                                  data['blood_pressure'], data['oxygen_saturation'], data['timestamp']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Initialize the database
initialize_database()


# Define the callback for the message subscriber
def publish_data(server_input, server_output):
    # Connect to SQLite database (or create it if it doesn't exist)
    while True:
        try:
            server_input.wait()
        except rti.TimeoutError as error:
            continue

        server_input.read() # Read the data from the input
        for sample in server_input.samples:
            if (sample.info['sample_state'] == 'NOT_READ') and (sample.valid_data == False) and (sample.info['instance_state'] == 'NOT_ALIVE_NO_WRITERS'):
                print("Sensor: " + sample.get_string("sensor_id") + " - Status: Disconnected")
                break
            else:
                # Process each valid data sample
                data = sample.get_dictionary()
                print("Received data:", data)
                # Insert data into the database
                insert_patient_data(data)
                # Forward data to healthcare providers
                server_output.instance.set_dictionary(data)
                server_output.write()


"""
This thread will monitor the joining and leaving of a provider
"""
def provider_sub(provider_input):
    # Connect to SQLite database (or create it if it doesn't exist)
    while True:
        try:
            provider_input.wait(500)
        except rti.TimeoutError as error:
            continue

        provider_input.take() # Read the data from the input
        # Process each valid data sample
        for sample in provider_input.samples:
            # Process each valid data sample
            if (sample.info['sample_state'] == 'NOT_READ') and (sample.valid_data == False) and (sample.info['instance_state'] == 'NOT_ALIVE_NO_WRITERS'):
                print("Provider: " + sample.get_string("username") + " - Status: Disconnected") # Disconnected
                break
            else:
                print("Provider: " + sample.get_string("username") + " - Status: connected") # Connected
             

with rti.open_connector(
    config_name="DomainParticipantLibrary::Server_Participant",
    url="COE427-HW2.xml") as connector:

    # Getting input and output
    server_input = connector.get_input("Server_Subscriber::Sensor_Reader")
    provider_input = connector.get_input("Server_Subscriber::Provider_Reader")
    server_output = connector.get_output("Server_Publisher::Server_Writer")

    
    #  Start threads
    t1 = threading.Thread(target=publish_data, args=(server_input, server_output))
    t1.start()

    t2 = threading.Thread(target=provider_sub, args=(provider_input,))
    t2.start()

    # Wait for threads to finish
    t1.join()
    t2.join()