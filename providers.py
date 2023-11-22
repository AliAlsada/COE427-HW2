import threading
import time
import os


import rticonnextdds_connector as rti

lock = threading.RLock()
finish_thread = True
search_thread = True

def command_task(patient_data):
    
    global finish_thread
    global search_thread

    while finish_thread:
        command = input("Enter command: \n")

        if command == "exit":
            finish_thread = False
            search_thread = False

        elif command.startswith("monitor"):

            search_thread = True 
            patient_id = int(input("Enter the patient id: "))

            monitor_thread = threading.Thread(target=search_patient_data, args=(patient_id, patient_data, lock))
            monitor_thread.start()

        elif command == "stop":
                search_thread = False
                monitor_thread.join()


def search_patient_data(patient_id, patient_data, lock):

    while search_thread:
        with lock:
            patient_data.wait()
            patient_data.take()
            for sample in patient_data.samples.valid_data_iter:
                if sample["patient_id"] == patient_id:
                    data = sample.get_dictionary()
                    print("Received data:", data)
            


def data_subscriber_task(patient_data):
    global finish_thread

    while finish_thread == False:
        try:
            patient_data.wait(500)
        except rti.TimeoutError as error:
            continue

        # with lock:
        #     patient_data.wait()
        #     patient_data.take()
        #     for sample in patient_data.samples.valid_data_iter:
        #             data = sample.get_dictionary()
        #             print("Received data:", data)
        



with rti.open_connector(
    config_name="DomainParticipantLibrary::Providers_Participant",
    url="COE427-HW2.xml") as connector:


    patient_data = connector.get_input("Provider_Subscriber::Provider_Reader")

    t1 = threading.Thread(target=command_task, args=(patient_data,))
    t1.start()


    t1.join()


