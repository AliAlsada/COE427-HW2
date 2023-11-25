import threading
import time
import os


import rticonnextdds_connector as rti

lock = threading.RLock()
thread_state = True
patient_id = False # by defualt their is no patient to monitor


ABNORMAL_THRESHOLDS = {
    'heart_rate': {'low': 50, 'high': 170},  # Beats per minute
    'blood_pressure': {'low': 76, 'high': 130},  # Systolic pressure
    'oxygen_saturation': {'low': 92, 'high': 100}  # Percentage
}

def command_task(patient_data):
    
    global thread_state
    global patient_id

    while thread_state:
        command = input("Enter command: \n")

        #Terminate all threads
        if command.upper() == "EXIT":
            thread_state = False

        #monitor a specific patient vital sign  
        elif command.upper() == "MONITOR":        
            patient_id = int(input("Enter the patient id: "))

        #stop monitoring the patient
        elif command.upper() == "STOP":
            patient_id = False
            


def check_for_abnormalities(sample):
    """
    Check if the patient data exceeds any of the predefined thresholds.
    """
    for key, thresholds in ABNORMAL_THRESHOLDS.items():
        # Extract the value for the current health metric
        value = sample.get(key)

        # Check if the value is outside the normal range
        if value is not None and (value < thresholds['low'] or value > thresholds['high']):
            print(f"Alert-- Patient {sample['patient_id']}: {key} is abnormal. Value: {value}")
   



def reading_thread(patient_data):
    global patient_id
    global thread_state

    while thread_state:
        with lock:
            patient_data.wait()
            patient_data.take()
            for sample in patient_data.samples.valid_data_iter:

                # Check for abnormalities in the sample data.
                # This function analyzes the sample data against predefined thresholds.
                check_for_abnormalities(sample.get_dictionary())

                # Filter the data based on the patient_id.
                # This conditional ensures that the thread only processes data 
                # relevant to the specific patient we're interested in.
                if sample["patient_id"] == patient_id:
                    data = sample.get_dictionary()
                    print("Received data:", data)


with rti.open_connector(
    config_name="DomainParticipantLibrary::Providers_Participant",
    url="COE427-HW2.xml") as connector:


    patient_data = connector.get_input("Provider_Subscriber::Provider_Reader")

    t1 = threading.Thread(target=command_task, args=(patient_data,))
    t1.start()

    t2 = threading.Thread(target=reading_thread, args=(patient_data,))
    t2.start()

    t1.join()
    t2.join()


