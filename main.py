# **********************************
#    Priscilla González - 20689
#              Redes
# **********************************

from client import Client

SERVER = '@alumchat.xyz'

is_authenticated = False

def print_main_menu():
    main_menu = '''
    ╔═══════════════╗
    ║      Menu     ║
    ╠═══════════════╣
    ║  1. Login     ║
    ║  2. Register  ║
    ║  3. Log Out   ║
    ╚═══════════════╝
    '''
    print(main_menu)

def print_authenticated_menu():
    authenticated_menu = '''
    ╔════════════════════════════════╗
    ║              Menu              ║
    ╠════════════════════════════════╣
    ║  1. >>> Show Connected Users   ║
    ║  2. >>> Add User               ║
    ║  3. >>> Show User Details      ║
    ║  4. >>> Send a Private Message ║
    ║  5. >>> Create Group           ║
    ║  6. >>> Join Group             ║
    ║  7. >>> Send Message to Group  ║
    ║  8. >>> Send Presence          ║
    ║  9. >>> Delete User            ║
    ║ 10. >>> Delete Account         ║
    ║ 11. >>> End                    ║
    ╚════════════════════════════════╝
    '''
    print(authenticated_menu)

def status_pres(value):
    if value == "1":
        return "available"
    elif value == "2":
        return "away"
    elif value == "3":
        return "xa"
    elif value == "4":
        return "dnd"
    else:
        return "available"

login_option = ""
client = None

while login_option != "3":
    is_authenticated = False # Reset the authentication flag on logout
    print_main_menu()
    login_option = input("Choose an Option 🤹🏼‍♀️: ")
    # Login
    if login_option == "1":
        username = input("\nUsername: ")
        password = input("Password: ")
        client = Client(username + SERVER, password)
        print("\nLOG IN...")
        if client.login():
            is_authenticated = True
            print("\nLog In Succesfully ✅")
        else:
            print("\nError 🆘")
    # Register
    elif login_option == "2":
        username = input("\nUsername: ")
        password = input("Password: ")
        name = input("Name: ")
        email = input("Email: ")
        client = Client(username + SERVER, password, name, email, registering=True)
        if client.login():
            is_authenticated = True
            print("\nAccount Succesfully Created ✅")
        else:
            print("\nError 🆘")
    elif login_option == "3":
        print("LOGING OUT...")
    else:
        print("Invalid Option ❌")

    def option1(client):
        client.gettingC()

    def option2(client):
        user_to_add = input("Enter the username to add: ")
        subscription_message = input("Enter the subscription request message: ")
        client.addingC(user_to_add, subscription_message)
        print("\nSubscription sent")

    def option3(client):
        user_to_search = input("Enter the username to search for: ")
        client.searchU(user_to_search)

    def option4(client):
        user_to_send = input("Enter the username to send the message to: ")
        client.chatHis(user_to_send)
        message = input(">>> (You): ")
        client.sendMessagesToServerSingle(user_to_send, message)

    def option5(client):
        group_name = input("Enter the groups name: >>> ")
        client.createGrupo(group_name)
        print("\nGroup Created Succesfully ✅")

    def option6(client):
        group_name = input("Enter the groups name: >>> ")
        client.joinGroup(group_name)
        print("\nYou have joined the group sucessfully 🥳")

    def option7(client):
        group_to_send = input("Enter the groups name to send the message: >>> ")
        client.roomHis(group_to_send)
        message = input(">>> (You): ")
        client.sendMessagesToServerGroup(group_to_send, message)

    def option8(client):
        print("\n1. Available\n2. Away\n3. Not Available\n4. Busy")
        value = input("Enter your status: ")
        message = input("Enter the presence message: ")
        show = status_pres(value)
        client.presenceMessage(show, message)

    def option9(client):
        user_to_delete = input("Enter the username to delete: ")
        client.deleteFriend(user_to_delete)
        print("\nContact deleted 🤡")

    def option10(client):
        client.deleteAccount()
        print("\nAccount Deleted 💀")
        print("Closing Session...")
        client.disconnect()

    def option11(client):
        print("Closing Session...")
        client.disconnect()
        
    menu_options = {
        "1": option1,
        "2": option2,
        "3": option3,
        "4": option4,
        "5": option5,
        "6": option6,
        "7": option7,
        "8": option8,
        "9": option9,
        "10": option10,
        "11": option11
    }

    if is_authenticated:
        option = ""
        while option != "11":
            print_authenticated_menu()
            option = input("Choose an Option 🤹🏼‍♀️: ")

            # Dictionary options
            if option in menu_options:
                menu_options[option](client)
            elif not client.connected:
                option = "11"

            # This is used to respond to a received message
            elif option == "Y" or option == "y":
                # If a new message is received waiting to be responded to
                if client.to_chat:
                    client.to_chat = False
                    # Message received from contact
                    if client.to_chat_type == "contact":
                        client.chatHis(client.message_receiver)
                        message = input(">>> (You): ")
                        client.sendMessagesToServerSingle(client.message_receiver, message)
                    # Message received from group
                    else:
                        client.roomHis(client.message_receiver)
                        message = input(">>> (You): ")
                        client.sendMessagesToServerGroup(client.message_receiver, message)
                else:
                    print("Invalid Option ❌")
            # Non valid options
            else:
                # This is used when user decides to not respond to a message
                if option == "n" or option == "N" and client.to_chat:
                    client.to_chat = False
                else:
                    print("Invalid Option ❌")
