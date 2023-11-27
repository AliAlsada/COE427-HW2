# Mohammad Al Ramis - 201920170
# Mohammed Althunayan – 201944590
# Ali Alsada – 201960570


from datetime import datetime
import threading
import argparse
import random
import time
import os

import rticonnextdds_connector as rti


# Set up argument parser
parser = argparse.ArgumentParser(description='vital sign application')
parser.add_argument('sensor_id', help='Sensor ID', type=int)  

args = parser.parse_args()

# Set environment variables
thread_state = True


# Define the callback for the message subscriber
def generate_vital_sign(sensor_output):
    global thread_state

    patient_id = int(input("Write Patient ID: "))

    while thread_state:
        # Generate random vital sign data
        heart_rate = random.randint(50, 170)
        blood_pressure = random.randint(70, 180)
        oxygen_saturation = random.randint(90, 110)

        #Unix time
        timestamp = time.time()

        # Converting Unix timestamp to a datetime object
        timestamp = datetime.fromtimestamp(timestamp)

        # Formatting the datetime object into a string with 12-hour format without fractional seconds
        formatted_timestamp = timestamp.strftime('%Y-%m-%d %I:%M:%S %p')

        # Set data and write
        sensor_output.instance.set_number("sensor_id", args.sensor_id)
        sensor_output.instance.set_number("patient_id", patient_id)
        sensor_output.instance.set_number("heart_rate", heart_rate)
        sensor_output.instance.set_number("blood_pressure", blood_pressure)
        sensor_output.instance.set_number("oxygen_saturation", oxygen_saturation)
        sensor_output.instance.set_string("timestamp", formatted_timestamp)
        sensor_output.write()

        time.sleep(10)  # Publish every 10 second

# Define the callback for the command task
def command_task():
    global thread_state

    while thread_state == True:
        command = input("Enter command: ")

        if command == "exit":
            thread_state = False


# Set environment variables
with rti.open_connector(
    config_name="DomainParticipantLibrary::Sensor_Participant",
    url="COE427-HW2.xml") as connector:

    # Getting input and output
    sensor_output = connector.get_output("Sensor_Publisher::Sensor_Writer")

    #  Start threads
    t1 = threading.Thread(target=generate_vital_sign, args=(sensor_output,))
    t1.start()

    t2 = threading.Thread(target=command_task)
    t2.start()

    # Wait for threads to finish
    t1.join()
    t2.join()

    #unregister
    sensor_output.instance.set_number("sensor_id", args.sensor_id)
    sensor_output.write(action="unregister")
