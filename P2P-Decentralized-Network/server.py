########################################################################################################################
# Class: Computer Networks
# Date: 02/03/2020
# Lab3: TCP Server Socket
# Goal: Learning Networking in Python with TCP sockets
# Student Name:
# Student ID:
# Student Github Username:
# Lab Instructions: No partial credit will be given in this lab
# Program Running instructions: python3 server.py # compatible with python version 3
#
########################################################################################################################

# don't modify this imports.
import socket
import pickle
from threading import Thread
from uploader import Uploader


class Server(object):

    MAX_NUM_CONN = 10  # keeps 10 clients in queue

    def __init__(self, host, port, peer_id, torrent, pwp, bitfield):
        """
        :param host: by default localhost. Note that '0.0.0.0' takes LAN ip address.
        :param port: by default 12000
        """
        self.host = host
        self.port = port
        self.serversocket = None
        self.peer_id = peer_id
        self.torrent = torrent
        self.swarm = {}
        self.connected = {}
        self.pwp = pwp
        self.bitfield = bitfield
        try:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error as err:
            print("socket creation failed with error %s" % err)

    def _bind(self):
        """
        :return: VOID
        """
        self.serversocket.bind((self.host, self.port))

    def _listen(self):
        """
        :return: VOID
        """
        try:
            self._bind()
            self.serversocket.listen(self.MAX_NUM_CONN)
            #print("Listening for new peers at " + self.host + "/" + str(self.port))

        except:
            self.serversocket.close()

    def client_thread(self, clienthandler, addr):
        client_id = addr[1]
        data = {'clientid':  client_id}
        self._send_clientid(clienthandler, data)
        msg = self.receive(clienthandler)
        if msg == self.pwp.INTERESTED:
            self.send(clienthandler, self.pwp.UNCHOKE)
        Uploader(self.peer_id, self, clienthandler, "", self.torrent)



    def _accept_clients(self):
        """
        # Handle client connections to the server
        :return: VOID
        """
        while True:
            try:
                clienthandler, addr = self.serversocket.accept()
                Thread(target=self.client_thread, args=(clienthandler, addr)).start()
            except:
                self.serversocket.close()

    def _send_clientid(self, clienthandler, clientid):
        """
        :param clienthandler:
        :param clientid:
        :return: VOID
        """
        self.send(clienthandler, clientid)

    def send(self, clienthandler, data):
        """
        :param clienthandler: the clienthandler created when connection was accepted
        :param data: raw data (not serialized yet)
        :return: VOID
        """
        serialized_data = pickle.dumps(data)
        clienthandler.send(serialized_data)

    def receive(self, clienthandler, MAX_ALLOC_MEM=4096):
        """
        :param MAX_ALLOC_MEM: default set to 4096
        :return: the deserialized data.
        """
        raw_data = clienthandler.recv(MAX_ALLOC_MEM)
        data = pickle.loads(raw_data)
        return data

    def run(self):
        """
        :return: VOID
        """
        self._listen()
        self._accept_clients()


# main execution
if __name__ == '__main__':
    server = Server()
    server.run()
