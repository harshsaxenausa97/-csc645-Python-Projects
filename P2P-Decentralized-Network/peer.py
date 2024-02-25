# CSC645 Computer Networks
# Lab 8 Solution: peer.py
# Author: Jose Ortiz
# client and server files are from lab 2. However, the server supports multi-threading like in lab 4
from server import Server
from threading import Thread
from client import Client
import uuid
from tracker import Tracker
from torrent import Torrent
from downloader import Downloader
from pwp import PWP
from config import Config
import sys
from os import path

class Peer(Server):
    """
    In this part of the peer class we implement methods to connect to multiple peers.
    Once the connection is created downloading data is done in similar way as in TCP assigment.
    """
    SERVER_PORT = 5000
    CLIENT_MIN_PORT_RANGE = 5001
    CLIENT_MAX_PORT_RANGE = 5010

    MAX_NUM_CONNECTIONS = 10
    MAX_UPLOAD_RATE = 100
    MAX_DOWNLOAD_RATE = 1000

    PEER = 'peer'
    LEECHER = 'leecher'
    SEEDER = 'seeder'

    def __init__(self, role=SEEDER, server_ip_address='127.0.0.1'):
        """
        Class constructor
        :param server_ip_address: used when need to use the ip assigned by LAN
        """

        self.server_ip_address = server_ip_address
        self.peer_id = uuid.uuid4()  # creates unique peer_id for the peer
        self.config = Config()
        self.role = role
        self.torrent = Torrent(self.torrent_path())
        self.pwp = PWP()
        self.pwp.msg.init_bitfield(self.torrent.num_pieces)
        self.bitfield = self.pwp.msg.get_bitfield()
        self.server = Server(server_ip_address, self.SERVER_PORT, self.peer_id, self.torrent, self.pwp, self.bitfield)  # inherits methods from the server
        self.tracker = Tracker(self.torrent, self.server, self.peer_id)



    def interested(self):
        interested = self.pwp.message(self.pwp.INTERESTED)
        return interested


    def non_interested(self):
        non_interested = self.pwp.message(self.pwp.INTERESTED)
        return non_interested

    def torrent_path(self):
        # try:
        #     if len(sys.argv) > 0:
        #         is_option = sys.argv[1]
        #         if is_option == '-t' and sys.argv[2]:
        #             file = sys.argv[2]
        #             torrent_path = "resources/torrents/" + file
        #             if path.exists(torrent_path):
        #                 return torrent_path
        #     return -1
        # except Exception as error:
        #     print(error)
        torrent_path = "resources/torrents/" + "age.torrent"
        return torrent_path

    def run_server(self):
        """
        Already implemented. puts this peer to listen for connections requests from other peers
        :return: VOID
        """
        try:
            # must thread the server, otherwise it will block the main thread
            #print("Peer: " + str(self.peer_id) + " running its server: ")
            Thread(target=self.server.run, daemon=True).start()
        except Exception as error:
            print(error)  # server failed to run

    def run_tracker(self):
        """
        Already implemented. puts this peer to listen for connections requests from other peers
        :return: VOID
        """
        try:
            Thread(target=self.tracker.run, daemon=True).start()
        except Exception as error:
            print(error)  # server failed to run



    # noinspection PyMethodMayBeStatic
    def _connect_to_peer(self, client_port_to_bind, peer_ip_address, peer_port=SERVER_PORT, interested=True, keep_alive=True):
        """
        This method connects a client from this peer to another peer.
        :param client_port_to_bind: port to bind the client to have more control over the ports used by our P2P network
        :param peer_ip_address: the ip address of the peer
        :param peer_port: the port of the peer
        :return: True if the client connected to the Peer. Otherwise, returns False
        """
        client = Client(self.peer_id, self.pwp, self.torrent)
        try:
            # binds the client to the ip address assigned by LAN
            client.bind('0.0.0.0', client_port_to_bind)  # note: when you bind, the port bound will be the client id
            Thread(target=client.connect_to_server, args=(peer_ip_address, peer_port)).start()  # threads server
            return True
        except Exception as error:
            print(error)  # client failed to bind or connect to server
            """
              Note that the following line does not unbind the port. Sometimes, once the socket is closed 
              The port will be still bound until WAIT_TIME gets completed. If you get the error: 
              "[Errno 48] Address already in use" 
              Then, go to your terminal and do the following to unbind the port:
                  lsof -i tcp:<client_port>
              Then copy the "pid" of the process, and execute the following
                  kill -i <pid>
              There are also other ways to unbind the port in code. Try the following line in the server file right 
              after you create the server socket
                  serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
              The above line only works sometimes depending on the system and how busy is your CPU.
            """
            client.close()
            return False

    def connect(self, peers_ip_addresses):
        """
        With this function this peer creates multiple clients that connect to multiple peers
        :param peers_ip_addresses: the ip addresses of the peers (their servers ip_addresses)
        :return: VOID
        """
        client_port = self.CLIENT_MIN_PORT_RANGE
        default_peer_port = self.SERVER_PORT
        for peer_ip in peers_ip_addresses:
            if client_port > self.CLIENT_MAX_PORT_RANGE:
                break
            if "/" in peer_ip:  # checks if the ip address includes ports
                # This part is good if your P2P supports sharing different files
                # Then the same peer can run different servers in the same machine
                ip_and_port = peer_ip.split("/")
                peer_ip = ip_and_port[0]  # the ip address of the peer
                default_peer_port = int(ip_and_port[1])  # the port of the peer
            if self._connect_to_peer(client_port, peer_ip, default_peer_port):
                # the client connected. incrementing the client port here prevents
                # wasting ports in the range of ports assigned if the client connection fails.
                client_port += 1


# testing
print("\n***** P2P client App *****\n")
peer = Peer(role='peer')

print("Peer id: " + str(peer.peer_id))
print("Peer IP Address: " + peer.server_ip_address)
peer.run_server()
peer.run_tracker()

print("Max download rate: ")
print("Max upload rate: ")

print("\nTorrent: ages.torrent")
print("file: ages.txt")
print("seeder/s: " + peer.server.host + ":" + str(peer.server.port) + "\n")
ip_and_port = peer.torrent.announce()
# print("Peer: " + str(peer.id) + " running its clients: ")
# Two ways of testing this:
#  Locally (same machine):
#      1. Run two peers in the same machine using different ports. Comment out the next two lines (only servers run)
#      2. Then run a third peer, executing the next two lines of code.
#  Using different machines
#      1. Run two peers in different machines.
#      2. Run a peer in this machine.
if peer.role == peer.LEECHER or peer.role == peer.PEER:
    peer.tracker.add_peer_to_dht(peer.server_ip_address, peer.SERVER_PORT)
    peer.tracker.add_peer_to_swarm(peer.peer_id, peer.server_ip_address, peer.SERVER_PORT)
    print("Peer: " + str(peer.peer_id) + " running its clients: ")
    peer_ips = ['127.0.0.1/4998', '127.0.0.1/4999']  # this list will be sent by the tracker in your P2P assignment
    peer.connect(peer_ips)

while True:
    continue

""" Output running this in the same machine """
# Peer: 6d223864-9cd7-4327-ad02-7856d636af66 running its server:
# Listening for new peers at 127.0.0.1/5000
# Peer: 6d223864-9cd7-4327-ad02-7856d636af66 running its clients:
# Client id 5001 connected to peer 127.0.0.1/7001
# Client id 5002 connected to peer 127.0.0.1/7000

""" Output running one peer in this machibe in the other two in different machines """
# Peer: 6f4e024e9-0265-47ba-a525-1c880a7a9a5d running its server:
# Listening for new peers at 10.0.0.248/5000
# Peer: f4e024e9-0265-47ba-a525-1c880a7a9a5d running its clients:
# Client id 5001 connected to peer 10.0.0.251/5000
# Client id 5002 connected to peer 127.0.0.242/5000