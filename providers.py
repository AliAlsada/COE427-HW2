import threading
import time
import os


import rticonnextdds_connector as rti

lock = threading.RLock()
thread_state = True
monitor_thread_state = True

def command_task(patient_data):
    
    global thread_state
    global monitor_thread_state

    while thread_state:
        command = input("Enter command: \n")

        if command.upper() == "EXIT":
            thread_state = False
            monitor_thread_state = False

        #monitor a specific patient vital sign  
        elif command.upper() == "MONITOR":
            
            patient_id = int(input("Enter the patient id: "))

            monitor_thread_state = True 
            monitor_thread = threading.Thread(target=search_patient_data, args=(patient_id, patient_data, lock))
            monitor_thread.start()

        #stop monitoring a specific patient vital sign
        elif command.upper() == "STOP":
            monitor_thread_state = False
            monitor_thread.join()


def search_patient_data(patient_id, patient_data, lock):

    while monitor_thread_state:
        with lock:
            patient_data.wait()
            patient_data.take()
            for sample in patient_data.samples.valid_data_iter:
                #======== filter the data based on the patient id ==========
                if sample["patient_id"] == patient_id:
                    data = sample.get_dictionary()
                    print("Received data:", data)



with rti.open_connector(
    config_name="DomainParticipantLibrary::Providers_Participant",
    url="COE427-HW2.xml") as connector:


    patient_data = connector.get_input("Provider_Subscriber::Provider_Reader")

    t1 = threading.Thread(target=command_task, args=(patient_data,))
    t1.start()


    t1.join()


