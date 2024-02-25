#######################################################################
# File:             client_handler.py
# Author:           Jose Ortiz
# Purpose:          CSC645 Assigment #1 TCP socket programming
# Description:      Template ClientHandler class. You are free to modify this
#                   file to meet your own needs. Additionally, you are
#                   free to drop this client handler class, and use a version of yours instead.
# Running:          Python 2: python server.py
#                   Python 3: python3 server.py
#                   Note: Must run the server before the client.
########################################################################
import datetime
import sys
from menu import Menu


class ClientHandler(object):
    """
    The ClientHandler class provides methods to meet the functionality and services provided
    by a server. Examples of this are sending the menu options to the client when it connects,
    or processing the data sent by a specific client to the server.
    """
    def __init__(self, server_instance, clientsocket, addr):
        """
        Class constructor already implemented for you
        :param server_instance: normally passed as self from server object
        :param clientsocket: the socket representing the client accepted in server side
        :param addr: addr[0] = <server ip address> and addr[1] = <client id>
        """
        self.client_id = addr[1]
        self.server = server_instance
        self.clientsocket = clientsocket
        self.unreaded_messages = []

    def set_client_name(self):
        self.client_name= self.server.receive(self.clientsocket)

    def send_menu(self):
        """
        Already implemented for you.
        sends the menu options to the client after the handshake between client and server is done.
        :return: VOID
        """
        menu = Menu()
        self.server.send(self.clientsocket, menu)

    def send_client_id(self):
        self.server.send(self.clientsocket, self.client_id)

    def process_options(self):
        """
        Process the option selected by the user and the data sent by the client related to that
        option. Note that validation of the option selected must be done in client and server.
        In this method, I already implemented the server validation of the option selected.
        :return:
        """
        data = self.server.receive(self.clientsocket)
        if 'option_selected' in data.keys() and 1 <= data['option_selected'] <= 7:
            option = data['option_selected']
            if option == 1:
                self._send_user_list()
            elif option == 2:
                recipient = int(data['recipient'])
                message = data['message']
                self._save_message(recipient, message)
            elif option == 3:
                self._send_messages()
            elif option == 4:
                room_id = data['room_id']
                self._create_chat(room_id)
            elif option == 5:
                room_id = data['room_id']
                if room_id in self.server.chat_room:
                    self._join_chat(room_id)
                else:
                    self.server.send(self.clientsocket, "CHAT_ROOM_DO_NOT_EXIST")
            elif option == 6:
                self._disconnect_from_server()
                return "CLIENT_DISCONNECTED"
            elif option == 7:
                room_id = data['room_id']
                message = data['message']
                self._process_chat_root_message(room_id, message)
        else:
            print("The option selected is invalid")

    def _send_user_list(self):
        """
        TODO: send the list of users (clients ids) that are connected to this server.
        :return: VOID
        """
        users = self.server.clients
        users_list = []
        for client_id in users:
            users_list.append(users[client_id].client_name + ":" + str(client_id))
        data = "Users in server: " + ', '.join(users_list)
        self.server.send(self.clientsocket, data)
        print("List of users sent to client: {}".format(self.client_id))

    def _save_message(self, recipient_id, message):
        """
        TODO: link and save the message received to the correct recipient. handle the error if recipient was not found
        :param recipient_id:
        :param message:
        :return: VOID
        """
        client_handler = self.server.clients[recipient_id]
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        client_message = {"time_stamp": time_stamp, "sender_name": self.client_name, "message": message}
        client_handler.unreaded_messages.append(client_message)
        print("Message from " + self.client_name + ": " + message)


    def _send_messages(self):
        """
        TODO: send all the unreaded messages of this client. if non unread messages found, send an empty list.
        TODO: make sure to delete the messages from list once the client acknowledges that they were read.
        :return: VOID
        """
        messages = []
        if len(self.unreaded_messages) != 0:
            for message in self.unreaded_messages:
                msg = message["time_stamp"] + ": " + message["message"] + " (from: " + message["sender_name"] + ")"
                messages.append(msg)
            data = ",".join(messages)
        else:
            data = "You got no messages at this time"

        self.server.send(self.clientsocket, data)
        print("List of messages sent to {}".format(self.client_id))
        self.delete_client_data()

    def _create_chat(self, room_id):
        """
        TODO: Creates a new chat in this server where two or more users can share messages in real time.
        :param room_id:
        :return: VOID
        """
        self.server.chat_room_owner[room_id] = self.client_id
        self.server.chat_room[room_id] = [self.client_id]
        self.server.chat_room_messages[room_id] = []
        data = """\n----------------------- Chat Room {} ------------------------\n
Type 'exit' to close the chat room.
Chat room created by: {}
Waiting for other users to join....
        """.format(room_id, self.client_name)
        self.server.send(self.clientsocket, data)

    def _join_chat(self, room_id):
        """
        TODO: join a chat in a existing room
        :param room_id:
        :return: VOID
        """
        chat_room = self.server.chat_room[room_id]
        chat_room.append(self.client_id)
        chat_room_messages = self.server.chat_room_messages[room_id]

        intro_msg = """----------------------- Chat Room {} ------------------------
Joined to chat room {} 
Type 'bye' to exit this chat room.""".format(room_id, room_id)
        client_joined = ""
        for client_id in chat_room:
            client_name = self.server.clients[client_id].client_name
            client_joined += client_name + " joined.\n"

        client_messages = ""
        for message in chat_room_messages:
            time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            msg = message["sender_name"] + "> " + message["message"] + "\n"
            client_messages += msg

        data = intro_msg + "\n" + client_joined + client_messages
        self.server.send(self.clientsocket, data)

        # send message to all the clients on the chat room
        message = self.client_name + " joined."

        except_client_list = [self.client_id]
        self._push_message_to_chat_room(chat_room, message, except_client_list)

    def _process_chat_root_message(self, room_id, message):

        owner_client_id = self.server.chat_room_owner[room_id]
        clients_list = self.server.chat_room[room_id]
        except_client_list = []

        if message.upper() == "EXIT" and owner_client_id == self.client_id:
            chat_room_msg = "CHAT_ROOM_CLOSED"
            del self.server.chat_room_messages[room_id]
            del self.server.chat_room[room_id]
            del self.server.chat_room_owner[room_id]

        elif message.upper() == "BYE" and owner_client_id != self.client_id:
            chat_room_msg = self.client_name + " disconnected from the chat."
            client_list = self.server.chat_room[room_id]
            client_list.remove(self.client_id)
            #send CHAT_ROOM_CLOSED to current client
            client = self.server.clients[self.client_id]
            client.server.send(client.clientsocket, "CHAT_ROOM_EXIT")

        else:
            time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            message = {"time_stamp": time_stamp, "sender_name": self.client_name, "message": message}
            chat_room_messages = self.server.chat_room_messages[room_id]
            chat_room_messages.append(message)
            chat_room_msg = message["sender_name"] + "> " + message["message"]
            except_client_list = [self.client_id]

        # send message to all the clients on the chat room
        self._push_message_to_chat_room(clients_list, chat_room_msg, except_client_list)

    def _push_message_to_chat_room(self, clients_list, message, except_client_list):
        for client_id in clients_list:
            if client_id not in except_client_list:
                client = self.server.clients[client_id]
                client.server.send(client.clientsocket, message)

    def delete_client_data(self):
        """
        TODO: delete all the data related to this client from the server.
        :return: VOID
        """
        self.unreaded_messages.clear()

    def _disconnect_from_server(self):
        """
        TODO: call delete_client_data() method, and then, disconnect this client from the server.
        :return: VOID
        """
        self.server.send(self.clientsocket, "CLIENT_DISCONNECTED")
        self.delete_client_data()
        del self.server.clients[self.client_id]
        print("Client {} disconnected from server".format(self.client_id))
        self.clientsocket.close()