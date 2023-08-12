from client import Client

SERVER = '@alumchat.xyz'

is_authenticated = False

menu_login = '''
    ╔═══════════════╗
    ║      Menu     ║
    ╠═══════════════╣
    ║  1. Login     ║
    ║  2. Register  ║
    ║  3. Log Out   ║
    ╚═══════════════╝
'''

menu = '''
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

def get_show_presence(value):
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
    print(menu_login)
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

    # Main menu for authenticated users
    if is_authenticated:
        option = ""
        while option != "11":
            print(menu)
            option = input("Choose an Option 🤹🏼‍♀️: ")
            if not client.connected:
                option = "11"
            # Show connected users
            if option == "1":
                client.gettingC()
            # Add contact
            elif option == "2":
                user_to_add = input("Enter the username of the user to add: ")
                subscription_message = input("Enter the subscription request message: ")
                client.addingC(user_to_add, subscription_message)
                print("\nSubscription sent")
            # Show contact details
            elif option == "3":
                user_to_search = input("Enter the username of the user to search for: ")
                client.searchU(user_to_search)
            # Send message to a user
            elif option == "4":
                print("\n1. Send Message\n2. Send File")
                message_option = input("Select an Option 🤹🏼‍♀️: ")
                if message_option == "1":
                    user_to_send = input("Enter the username of the user to send the message to: ")
                    client.chatHis(user_to_send)
                    message = input(">>> (You): ")
                    client.sendMessagesToServerSingle(user_to_send, message)
                elif message_option == "2":
                    user_to_send = input("Enter the username of the user to send the file to: ")
                    file_path = input("Enter the path of the file to send: ")
                    client.send_file_to_user(user_to_send, file_path)
            # Create group
            elif option == "5":
                group_name = input("Enter the groups name: >>> ")
                client.createGrupo(group_name)
                print("\nGroup Created Succesfully ✅")
            # Join group
            elif option == "6":
                group_name = input("Enter the groups name: >>> ")
                client.joinGroup(group_name)
                print("\nYou have joined the group sucessfully 🥳")
            # Send message to group
            elif option == "7":
                group_to_send = input("Enter the groups name to send the message: >>> ")
                client.roomHis(group_to_send)
                message = input(">>> (You): ")
                client.sendMessagesToServerGroup(group_to_send, message)
            # Send presence message
            elif option == "8":
                print("\n1. Available\n2. Away\n3. Not Available\n4. Busy")
                value = input("Enter your status: ")
                message = input("Enter the presence message: ")
                show = get_show_presence(value)
                client.presenceMessage(show, message)
            # Delete contact
            elif option == "9":
                user_to_delete = input("Enter the username to delete: ")
                client.deleteFriend(user_to_delete)
                print("\nContact deleted 🤡")
            # Delete account
            elif option == "10":
                client.deleteAccount()
                print("\nAccount Deleted 💀")
                option = "11"
            # Logout
            elif option == "11":
                print("Closing Session...")
                client.disconnect()
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
