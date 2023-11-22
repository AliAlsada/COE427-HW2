import rticonnextdds_connector as rti
from datetime import datetime
import random
import time
import os




with rti.open_connector(
    config_name="DomainParticipantLibrary::Sensor_Participant",
    url="COE427-HW2.xml") as connector:

    sensor_output = connector.get_output("Sensor_Publisher::Sensor_Writer")

    patient_id = int(input("Write Patient ID: "))

    while True:
        # Generate random vital sign data
        heart_rate = random.randint(60, 100)
        blood_pressure = random.randint(70, 120)
        oxygen_saturation = random.randint(95, 100)

        #Unix time
        timestamp = time.time()

        # Converting Unix timestamp to a datetime object
        timestamp = datetime.fromtimestamp(timestamp)

        # Formatting the datetime object into a string with 12-hour format without fractional seconds
        formatted_timestamp = timestamp.strftime('%Y-%m-%d %I:%M:%S %p')

        # Set data and write
        sensor_output.instance.set_number("patient_id", patient_id)
        sensor_output.instance.set_number("heart_rate", heart_rate)
        sensor_output.instance.set_number("blood_pressure", blood_pressure)
        sensor_output.instance.set_number("oxygen_saturation", oxygen_saturation)
        sensor_output.instance.set_string("timestamp", formatted_timestamp)
        sensor_output.write()

        time.sleep(10)  # Publish every 10 second
