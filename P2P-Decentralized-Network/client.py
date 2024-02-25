########################################################################################################################
# Class: Computer Networks
# Date: 02/03/2020
# Lab3: TCP Client Socket
# Goal: Learning Networking in Python with TCP sockets
# Student Name:
# Student ID:
# Student Github Username:
# Instructions: Read each problem carefully, and implement them correctly.  No partial credit will be given.
########################################################################################################################

# don't modify this imports.
import socket
import pickle
from downloader import Downloader

######################################## Client Socket ###############################################################3
"""
Client class that provides functionality to create a client socket is provided. Implement all the TODO parts 
"""


class Client(object):

    def __init__(self, client_id, pwp, torrent):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_id = client_id
        self.pwp = pwp
        self.torrent = torrent

    def connect_to_server(self, server_ip_address, server_port):
        """
        TODO: Create a connection from client to server
        :param server_ip_address:
        :param server_port:
        :return:
        """
        self.client.connect((server_ip_address, server_port))
        self.set_client_id()
        print("Client id " + str(self.client_id) + " connected to peer " + server_ip_address + "/" + str(server_port))
        self.send(self.pwp.INTERESTED)
        msg = self.receive()
        if msg == self.pwp.UNCHOKE:
            Downloader(client, self.peer_id, self.torrent, self.pwp, self.pwp.interested, self.pwp.KEEP_ALIVE)

    def bind(self, host, port):
        """
        :return: VOID
        """
        self.client.bind((host, port))

    def send(self, data):
        """
        Serializes and then sends data to server
        :param data:
        :return:
        """
        data = pickle.dumps(data)
        self.client.send(data)

    def receive(self, MAX_BUFFER_SIZE=4090):
        """
        Desearializes the data received by the server
        :param MAX_BUFFER_SIZE: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        raw_data = self.client.recv(MAX_BUFFER_SIZE)
        return pickle.loads(raw_data)

    def set_client_id(self):
        """
        Sets the client id assigned by the server to this client after a succesfull connection
        :return:
        """
        data = self.receive()
        client_id = data['clientid']
        self.client_id = client_id

    def close(self):
        """
        close this client
        :return: VOID
        """
        client.close()


# main execution
if __name__ == '__main__':
    server_ip_address = "127.0.0.1"
    server_port = 12000
    client = Client()
    client.connect(server_ip_address, server_port)