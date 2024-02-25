#######################################################################
# File:             client.py
# Author:           Jose Ortiz
# Purpose:          CSC645 Assigment #1 TCP socket programming
# Description:      Template client class. You are free to modify this
#                   file to meet your own needs. Additionally, you are 
#                   free to drop this client class, and add yours instead. 
# Running:          Python 2: python client.py 
#                   Python 3: python3 client.py
#
########################################################################
import socket
import pickle
import sys
sys.path.append("../server/")

class Client(object):
    """
    The client class provides the following functionality:
    1. Connects to a TCP server
    2. Send serialized data to the server by requests
    3. Retrieves and deserialize data from a TCP server
    """

    def __init__(self, client_name):
        """
        Class constractpr
        """
        # Creates the client socket
        # AF_INET refers to the address family ipv4.
        # The SOCK_STREAM means connection oriented TCP protocol.
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientid = 0
        self.client_name = client_name
        self.chat_room_open = False
        self.chat_room_owner = False
        
    def get_client_id(self):
        return self.clientid

    
    def connect(self, host="127.0.0.1", port=12000):
        """
        TODO: Connects to a server. Implements exception handler if connection is resetted.
	    Then retrieves the cliend id assigned from server, and sets
        :param host: 
        :param port: 
        :return: VOID
        """

        try:
            self.clientSocket.connect((host, port))
            self.client_id = self.receive()
            self.send(client_name)

            print("Successfully connected to server:" + host + "/" + str(port))
            print("Your client info is:")
            print("Client Name: " + client_name)
            print("Client ID: " + str(self.client_id) + "\n")


            menu = self.receive()
            menu.set_client(self)
            menu.show_menu()

            while True:
                client_status = menu.process_user_data()
                if client_status == "CLIENT_DISCONNECTED":
                    break
        except:
            self.close()

        self.close()

    def chat_room_incoming_messages_thread(self, room_id):

        while True:
            data = self.receive()
            if data == "CHAT_ROOM_EXIT":
                break
            elif data == "CHAT_ROOM_CLOSED":
                if not self.chat_room_owner:
                    print("\n------------NEW MESSAGE------------------")
                    print(data)
                    print("Type 'MENU' to check the main menu")
                    print("-----------------------------------------\n")
                    self.chat_room_open = False
                    break
                else:
                    self.chat_room_owner = False
                    break
            else:
                print("\n------------NEW MESSAGE------------------")
                print(data)
                print("-----------------------------------------\n")

    def chat_room_outgoing_messages(self, room_id):

        while True:
            #print("Enter your message:")
            #message = sys.stdin.readline().rstrip()
            message = input("Enter your message: ")
            data = {}
            if self.chat_room_open:
                data['option_selected'] = 7
                data['room_id'] = room_id
                if message.upper() == "EXIT" and self.chat_room_owner:
                    data['message'] = message.upper()
                    self.send(data)
                    break
                elif message.upper() == "BYE" and not self.chat_room_owner:
                    data['message'] = message.upper()
                    self.send(data)
                    break
                else:
                    data['message'] = message
                    self.send(data)
            else:
                if message.upper() == "MENU":
                    break
                else:
                    print("\n------------NEW MESSAGE------------------")
                    print("CHAT_ROOM_CLOSED")
                    print("Type 'MENU' to check the main menu")
                    print("-----------------------------------------\n")


    def send(self, data):
        """
        TODO: Serializes and then sends data to server
        :param data:
        :return:
        """
        data = pickle.dumps(data)  # serialized data
        self.clientSocket.send(data)

    def receive(self, MAX_BUFFER_SIZE=4090):
        """
        TODO: Desearializes the data received by the server
        :param MAX_BUFFER_SIZE: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        raw_data = self.clientSocket.recv(MAX_BUFFER_SIZE)
        return pickle.loads(raw_data)

    def close(self):
        """
        TODO: close the client socket
        :return: VOID
        """
        self.clientSocket.close()


if __name__ == '__main__':

    host = input("Enter the server IP Address: ")
    port = int(input("Enter the server port: "))
    client_name = input("Your id key (i.e your name): ")

    client = Client(client_name)
    client.connect(host, port)
