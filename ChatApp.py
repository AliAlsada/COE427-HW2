
import os
import argparse
import threading

from posixpath import split
from time import sleep

from os import error, path as os_path

file_path = os_path.dirname(os_path.realpath(__file__))

parser = argparse.ArgumentParser(description='DDS Chat Application')

parser.add_argument('user', help='User name', type=str)
parser.add_argument('group', help='Group name', type=str)
parser.add_argument('-f', '--firstname', help='First name', type=str, default='')
parser.add_argument('-l', '--lastname', help='Last name', type=str, default='')

args = parser.parse_args()

os.environ['user'] = str(args.user)
os.environ['group'] = str(args.group)

import rticonnextdds_connector as rti

lock = threading.RLock()
finish_thread = False

def user_subscriber_task(user_input):
    global finish_thread

    while finish_thread == False:
        try:
            user_input.wait(500)
        except rti.TimeoutError as error:
            continue

        with lock:
            user_input.read()
            for sample in user_input.samples:
                if (sample.info['sample_state'] == 'NOT_READ') and (sample.valid_data == False) and (sample.info['instance_state'] == 'NOT_ALIVE_NO_WRITERS'):
                    print("User: " + sample.get_string("username") + " - Group: " + sample.get_string("group") + " - Status: Disconnected")

def message_subscriber_task(message_input):
    global finish_thread

    while finish_thread == False:
        try:
            message_input.wait(500)
        except rti.TimeoutError as error:
            continue

        with lock:
            message_input.take()
            for sample in message_input.samples.valid_data_iter:
                print("From: " + sample.get_string("fromuser") + " - " + sample.get_string("message"))


def command_task(user, message_output, user_input):
    global finish_thread

    while finish_thread == False:
        command = input("Enter command: ")
        if command == "exit":
            finish_thread = True
        elif command == "list":
            with lock:
                user_input.read()
                for sample in user_input.samples.valid_data_iter:
                    if sample.info['instance_state'] == 'ALIVE':
                        print("User: " + sample.get_string("username") + " - Group: " + sample.get_string("group"))
        elif command.startswith("send"):
            destination = command.split(maxsplit=2)
            if len(destination) == 3:
                with lock:
                    message_output.instance.set_string("fromuser", user)
                    message_output.instance.set_string("touser", destination[1])
                    message_output.instance.set_string("togroup", destination[1])
                    message_output.instance.set_string("message", destination[2])   

                    message_output.write()
            else:
                print("Wrong usage: Use \"send user|group message\"\n")  
        else:
            print("Unknown command")

with rti.open_connector(
    config_name = "ChatParticipantLibrary::ChatParticipant",
    url="./ChatApp.xml") as connector:

    user_output = connector.get_output("ChatUser_Publisher::ChatUser_Writer")
    message_output = connector.get_output("ChatMessagePublisher::ChatMessage_Writer")

    user_input = connector.get_input("ChatUserSubscription::ChatUser_Reader")
    message_input = connector.get_input("ChatMessageSubscription::ChatMessage_Reader")

    user_output.instance.set_string("username", args.user)
    user_output.instance.set_string("group", args.group)
    if args.firstname:
        user_output.instance.set_string("firstname", args.firstname)
    if args.lastname:
        user_output.instance.set_string("lastname", args.lastname)

    user_output.write()

    t1 = threading.Thread(target=command_task, args=(args.user, message_output, user_input,))
    t1.start()

    t2 = threading.Thread(target=message_subscriber_task, args=(message_input,))   
    t2.start()

    t3 = threading.Thread(target=user_subscriber_task, args=(user_input,))
    t3.start()

    t1.join()
    t2.join()
    t3.join()

#    sleep(5)

    #unregister
    user_output.instance.set_string("username", args.user)
    user_output.write(action="unregister")
