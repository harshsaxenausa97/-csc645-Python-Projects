#######################################################################################
# File:             menu.py
# Author:           Jose Ortiz
# Purpose:          CSC645 Assigment #1 TCP socket programming
# Description:      Template Menu class. You are free to modify this
#                   file to meet your own needs. Additionally, you are
#                   free to drop this Menu class, and use a version of yours instead.
# Important:        The server sends a object of this class to the client, so the client is
#                   in charge of handling the menu. This behaivor is strictly necesary since
#                   the client does not know which services the server provides until the
#                   clients creates a connection.
# Running:          This class is dependent of other classes.
# Usage :           menu = Menu() # creates object
#
########################################################################################
from threading import Thread


class Menu(object):
    """
    This class handles all the actions related to the user menu.
    An object of this class is serialized ans sent to the client side
    then, the client sets to itself as owner of this menu to handle all
    the available options.
    Note that user interactions are only done between client and user.
    The server or client_handler are only in charge of processing the
    data sent by the client, and send responses back.
    """

    def set_client(self, client):
        self.client = client

    def show_menu(self):
        """
        TODO: 1. send a request to server requesting the menu.
        TODO: 2. receive and process the response from server (menu object) and set the menu object to self.menu
        TODO: 3. print the menu in client console.
        :return: VOID
        """
        menu = self.get_menu()
        print(menu)

    def process_user_data(self):
        """
        TODO: according to the option selected by the user, prepare the data that will be sent to the server.
        :param option:
        :return: VOID
        """
        option = self.option_selected()
        if 1 <= option <= 6:
            if option == 1:
                option_data = self.option1()
                self.client.send(option_data)
                data = self.client.receive()
                print(data)
            elif option == 2:
                option_data = self.option2()
                self.client.send(option_data)
                print("Message sent!")
            elif option == 3:
                option_data = self.option3()
                self.client.send(option_data)
                print("My messages:")
                data = self.client.receive()
                for message in data.split(","):
                    print(message)
            elif option == 4:
                option_data = self.option4()
                self.client.send(option_data)
                data = self.client.receive()
                print(data)
                room_id = option_data['room_id']
                self.client.chat_room_owner = True
                self.client.chat_room_open = True
                Thread(target=self.client.chat_room_incoming_messages_thread, args=(room_id,)).start()
                self.client.chat_room_outgoing_messages(room_id)
                print(self.get_menu())

            elif option == 5:
                option_data = self.option5()
                self.client.send(option_data)
                data = self.client.receive()
                if data == "CHAT_ROOM_DO_NOT_EXIST":
                    print("\n-----------NEW MESSAGE [FROM SERVER]------------------")
                    print(data)
                    print("------------------------------------------------------\n")
                else:
                    print(data)
                    room_id = option_data['room_id']
                    self.client.chat_room_open = True
                    Thread(target=self.client.chat_room_incoming_messages_thread, args=(room_id,)).start()
                    self.client.chat_room_outgoing_messages(room_id)

                print(self.get_menu())

            elif option == 6:
                option_data = self.option6()
                self.client.send(option_data)
                data = self.client.receive()
                if data == "CLIENT_DISCONNECTED":
                    self.client.close()
                    return data
        else:
            print("Invalid Option")


    def option_selected(self):
        """
        TODO: takes the option selected by the user in the menu
        :return: the option selected.
        """
        try:
            option = int(input("\nYour option <enter a number>: "))
            return option
        except:
            return 0

    def get_menu(self):
        """
        TODO: Inplement the following menu
        ****** TCP CHAT ******
        -----------------------
        Options Available:
        1. Get user list
        2. Sent a message
        3. Get my messages
        4. Create a new channel
        5. Chat in a channel with your friends
        6. Disconnect from server
        :return: a string representing the above menu.
        """
        menu = """
****** TCP Message App ******\n-----------------------\nOptions Available:
1. Get user list
2. Sent a message
3. Get my messages
4. Create a new channel
5. Chat in a channel with your friends
6. Disconnect from server\n"""
        return menu

    def option1(self):
        """
        TODO: Prepare the user input data for option 1 in the menu
        :param option:
        :return: a python dictionary with all the data needed from user in option 1.
        """
        data = {}
        data['option_selected'] = 1
        # Your code here.
        return data

    def option2(self):
        """
        TODO: Prepare the user input data for option 2 in the menu
        :param option:
        :return: a python dictionary with all the data needed from user in option 2.
        """
        data = {}

        message = input("Enter your message: ")
        recipient_id = input("Enter recipient id: ")

        data['option_selected'] = 2
        data['message'] = message
        data['recipient'] = recipient_id

        return data

    def option3(self):
        """
        TODO: Prepare the user input data for option 3 in the menu
        :param option:
        :return: a python dictionary with all the data needed from user in option 3.
        """
        data = {}

        data['option_selected'] = 3

        return data

    def option4(self):
        """
        TODO: Prepare the user input data for option 4 in the menu
        :param option:
        :return: a python dictionary with all the data needed from user in option 4.
        """
        data = {}
        room_id = int(input("Enter new chat room id: "))

        data['option_selected'] = 4
        data['room_id'] = room_id

        return data

    def option5(self):
        """
        TODO: Prepare the user input data for option 5 in the menu
        :param option:
        :return: a python dictionary with all the data needed from user in option 5.
        """
        data = {}
        room_id = int(input("Enter chat room id to join: "))

        data['option_selected'] = 5
        data['room_id'] = room_id

        return data

    def option6(self):
        """
        TODO: Prepare the user input data for option 6 in the menu
        :param option:
        :return: a python dictionary with all the data needed from user in option 6.
        """
        data = {}
        data['option_selected'] = 6
        return data
