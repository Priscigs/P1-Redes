import base64
from userDetails import userDetails
from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream.stanzabase import ET
from sleekxmpp.exceptions import IqTimeout, IqError
from sleekxmpp.plugins.xep_0004.stanza.form import Form

SERVER = '@alumchat.xyz'
ROOM_SERVER = '@conference.alumchat.xyz'
PORT = 3000

class Client(ClientXMPP):
    def __init__(self, idUser, password, name=None, email=None, registering=False):
        ClientXMPP.__init__(self, idUser, password)
        self.password = password
        self.name = name
        self.email = email
        self.registering = registering # True if client was created for registration, False if client was created for login
        self.to_chat = False # Indicates if the client is waiting for a response to a message
        self.contacts = []
        self.rooms = {}
        self.connected = False
        self.add_event_handler('session_start', self.serverOnRegis)
        self.add_event_handler("register", self.registerServer)
        self.add_event_handler("onOff_subscribe", self.subscribe)
        self.add_event_handler("onOff_unsubscribe", self.unsubscribe)
        self.add_event_handler("got_offline", self.offlineServer)
        self.add_event_handler("got_online", self.onlineServer)
        self.add_event_handler("message", self.sendMessages)
        self.add_event_handler("changed_status", self.status)
        self.add_event_handler("groupchat_invite", self.groupChatInvitation)
        self.add_event_handler("connection_failed", self.failedConnectionServer)
        self.add_event_handler("failed_auth", self.failedConnectionServer)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0065') # SOCKS5 Bytestreams
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0071') # XHTML-IM
        self.register_plugin('xep_0077') # In-band Registration
        self['xep_0077'].force_registration = True
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0096') # File transfer
        self.register_plugin('xep_0231') # BOB

    def serverOnRegis(self, event):
        # Set the status of the chat to 'available'
        self.set_status('chat', 'available')
        
        # Update the roster for the first time
        self.update_roster(firts_time=True)  # Typo: 'firts_time' should be 'first_time'
        
        # Mark the connection as established
        self.connected = True

    # Register 
    def registerServer(self, event):
        # Check if registration is in progress
        if self.registering:
            # Create a new IQ (Info/Query) packet
            iq = self.Iq()
            
            # Set the IQ packet type to 'set'
            iq['type'] = 'set'
            
            # Set the registration information in the IQ packet
            iq['register']['username'] = self.boundidUser.user  
            iq['register']['password'] = self.password  
            iq['register']['name'] = self.name  
            iq['register']['email'] = self.email  
            
            try:
                # Send the IQ packet immediately (now=True)
                iq.send(now=True)
            except IqError as e:
                # Handle an IQ error by printing the IQ packet that caused it
                print(e.iq)
            except IqTimeout:
                # Handle a timeout error by printing a message
                print('Times Up! ⏳')

    # A notification will pop up when someone added you as a friend
    def subscribe(self, onOff):
        username = onOff['from'].bare
        message = f'{username} wants to add you as a friend 🥳'
        print(f'\n{message}')

    # A notification will pop up when someone removed you from their friend's list
    def unsubscribe(self, onOff):
        username = onOff['from'].bare
        message = f'{username} has removed you from their friends list 🤡'
        print(f'\n{message}')

    # A notification will pop uo when someone's offline the server
    def offlineServer(self, onOff):
        # Check if the bound user's bare JID (Jabber ID) is not in the 'from' attribute of the onOff
        if self.boundidUser.bare not in str(onOff['from']):
            # Convert the 'from' attribute to a user-friendly username
            u = self.idUser_to_user(str(onOff['from']))
            
            # Print a message indicating that a user has disconnected from the server
            print(f'\n{u} has disconnected from the server')
            
            # Iterate through the contacts to find and remove the disconnected user
            for i in self.contacts:
                if i.idUser == str(onOff['from']):
                    # Remove the user from the contacts list
                    self.contacts.remove(i)  
                    break

    # A notification will pop up when someone's online the server
    def onlineServer(self, onOff):
        # Check if the bound user's bare JID (Jabber ID) is not in the 'from' attribute of the onOff
        if self.boundidUser.bare not in str(onOff['from']):
            # Convert the 'from' attribute to a user-friendly username
            u = self.idUser_to_user(str(onOff['from']))
            
            # Print a message indicating that a user is connected to the server
            print(f'\n{u} is connected to the server')
            
            # Iterate through the contacts to find and update the online status of the connected user
            for i in self.contacts:
                if i.idUser == str(onOff['from']):
                    # Set the online status of the user to True
                    i.online = True  
                    break

    # Send a message to an user
    def sendMessages(self, messageToSend):
        show_response = True  # Initialize a flag to indicate whether to show a response
        
        if messageToSend['type'] == 'groupchat':
            nick = messageToSend['mucnick']  # Get the sender's nickname
            
            # Check if the sender is the same as the bound user, don't show the response
            if nick == self.boundidUser.user:
                show_response = False
            else:
                # Extract room name from 'from' attribute
                room = messageToSend['from'].bare.split('@')[0]
                message = messageToSend['body']  # Get the message body
                
                # Print and store the message with room information
                print(f'\n[{room}] {nick}: {message}')
                self.rooms[room].append(f'[{room}] {nick}: {message}')
                self.to_chat_type = 'room'  # Set the chat type to 'room'
                self.message_receiver = room  # Set the message receiver as the room name
        else:
            # Extract user name from 'from' attribute
            user = messageToSend['from'].bare.split('@')[0]
            
            # Check if the sender is the same as the bound user, don't show the response
            if user == self.boundidUser.user:
                show_response = False
            else:
                # Print the message with user information
                print(f'\n{user}: {messageToSend["body"]}')
                
                # Loop through the contacts to find the matching user and add the message
                for contact in self.contacts:
                    if contact.idUser == user + SERVER:  # Assumes SERVER is defined elsewhere
                        contact.add_message(f'{user}: {messageToSend["body"]}')
                        self.to_chat_type = 'contact'  # Set the chat type to 'contact'
                        self.message_receiver = user  # Set the message receiver as the user name
                        break
        
        # If show_response is True, ask if the user wants to answer
        if show_response:
            print("Wanna answer? (Y/n)")
            self.to_chat = True  # Set 'to_chat' flag to indicate a response is expected

    # A notification woll pop up when a status has changed
    def status(self, onOff):
        username = onOff['from'].bare
        user_status = self.client_roster.onOff[username]['status']
        message = f'\n{username} has changed his/her status to: {user_status}'
        
        print(user_status)
        print(message)

    # A notification will pop up when you're invited to a new eoom
    def groupChatInvitation(self, inv):
        print('\nRoom Invitation 👾')

    # Failed connection
    def failedConnectionServer(self, error):
        print(f'\nError!!! ❌: {error}\nPress "Enter" to try again!!')
        self.connected = False
        self.disconnect()

    # Connect to server
    def login(self):
        result = self.connect((SERVER[1:], PORT), use_ssl=False, use_tls=False)
        print(result)
        if result:
            self.process()
            return True
        return False
####
    # Send message and updates the chat history of the contact
    def sendMessagesToServerSingle(self, idUser, message):
        # Send the message to the user
        self.send_message(mto=idUser + SERVER, mbody=message, mtype='chat')

        # Update the chat history of the contact
        for contact in self.contacts:
            if contact.idUser == idUser:
                contact.add_message(f'You: {message}')
                break

    # Shows the chat history of a contact
    def chatHis(self, idUser):
        for contact in self.contacts:
            if contact.idUser == idUser:
                for message in contact.messages:
                    print(message)
                break

    # Create a group chat room
    def createGrupo(self, room):
        # Combine the room name with the server to form the complete room JID
        room_with_server = room + ROOM_SERVER
        
        # Join the group chat room with the bound user as the owner
        self.plugin['xep_0045'].joinMUC(room_with_server, self.boundidUser.user, wait=True)
        
        # Set the affiliation of the bound user to 'owner' in the room
        self.plugin['xep_0045'].setAffiliation(room_with_server, self.boundidUser.full, affiliation='owner')
        
        # Configure the room settings, possibly with options like who can join
        self.plugin['xep_0045'].configureRoom(room_with_server, ifrom=self.boundidUser.full)
        
        # Initialize an empty list to store messages for this room
        self.rooms[room] = []

    # Join an existing group chat room
    def joinGroup(self, room):
        # Combine the room name with the server to form the complete room JID
        room_with_server = room + ROOM_SERVER
        
        # Join the group chat room with the bound user
        self.plugin['xep_0045'].joinMUC(room_with_server, self.boundidUser.user)
        
        # Initialize an empty list to store messages for this room
        self.rooms[room] = []
        
        # Define the event handler for when someone in the room goes online
        muc_event = "muc::%s::got_online" % room_with_server
        
        # Add the event handler to handle online presence events in the room
        self.add_event_handler(muc_event, self.muc_online)

    # Send message to a room and updates the room chat history
    def sendMessagesToServerGroup(self, room, message):
        if room in self.rooms:
            room_with_server = room + ROOM_SERVER
            self.send_message(mto=room_with_server, mbody=message, mtype='groupchat')
            self.rooms[room].append(f'[{room}] {self.boundidUser.user}: {message}')

    # A notification will pop up when you get a group invitation
    def groupInvite(self, inv):
        print('\nRoom Invitation 👾')

    # Shows the chat history of a contact
    def roomHis(self, room):
        if room in self.rooms.keys():
            for message in self.rooms[room]:
                print(message)
        else:
            print('Youre not in the room! 💀')
            
    # Add new contacts
    def addingC(self, idUser, subscription_message):
        # Check if the user already exists in the contact list
        if any(contact.idUser == idUser for contact in self.contacts):
            print('This user already exists')
        else:
            # Send a subscription request to the new contact
            self.send_presence(pto=idUser + SERVER, pstatus=subscription_message, ptype="subscribe")

    # Show details of the user
    def gettingC(self, idUser='*'):
        iq = self.get_search_iq(idUser)
        users = []
        try:
            search_result = iq.send()
            search_result = ET.fromstring(str(search_result))
            for query in search_result:
                for x in query:
                    for item in x:
                        values = {}
                        for field in list(item):
                            for value in list(field):
                                values[field.attrib['var']] = value.text
                        if values != {}:
                            users.append(userDetails(
                                idUser=values['idUser'], email=values['email'], username=values['username'], name=values['name']))
        except IqError as e:
            print(e.iq)
        except IqTimeout:
            print('Times Up! ⏳')
        print("\nUsers Connected 🟢:")
        for user in users:
            print(user)
        return users
    
    # Leave a presence message
    def presenceMessage(self, show, status):
        self.send_presence(pshow=show, pstatus=status)

    # Search for users
    def searchU(self, idUser):
        matching_contacts = self.get_contact_by_idUser(idUser)
        self.update_contacts(matching_contacts)
        self.get_contacts(idUser)
    
    # Get contacts list and search the idUser
    def getIdUser(self, idUser):
        self.update_roster()
        groups = self.client_roster.groups()
        contacts = []

        for group in groups:
            for user in groups[group]:
                if idUser in user:
                    user_roster = self.client_roster[user]
                    contact = userDetails(idUser=user)
                    contact.set_info('name', user_roster.get('name', ''))
                    contact.set_info('Subscription', user_roster.get('subscription', ''))
                    contact.set_info('Groups', user_roster.get('groups', ''))
                    connected_roster = self.client_roster.presence(user)
                    
                    # Presence info set (show, status)
                    for _, state in connected_roster.items():
                        for k, v in state.items():
                            contact.set_info(k, v)
                    
                    contacts.append(contact)

        print("\Contacts 👥:")
        for contact in contacts:
            print(contact)
        
        return contacts

    # Receive a new list of contacts and update the self.contacts list, adding new contacts and updating existing ones.
    def updatingC(self, new_contacts):
        for new_contact in new_contacts:
            existing_contact = next((contact for contact in self.contacts if contact.idUser == new_contact.idUser), None)
            if existing_contact:
                existing_contact.update(new_contact)
            else:
                self.contacts.append(new_contact)

     # Get the contacts list and updates it
    def getC(self, first_time=False):
        try:
            # Get the current roster information from the server
            roster = self.get_roster()
            contacts_roster = []

            # Iterate through the items in the roster
            for idUser in roster['roster']['items'].keys():
                # Create a userDetails object for each contact
                contact = userDetails(idUser)
                
                # Iterate through the attributes of the contact and set them in the userDetails object
                for k, v in roster['roster']['items'][idUser].items():
                    contact.set_info(k, v)
                
                # Add the contact to the list of contacts
                contacts_roster.append(contact)
            
            # If it's the first time updating, replace the existing contacts list with the new one
            if first_time:
                self.contacts = contacts_roster
            else:
                # Otherwise, update the existing contacts list with the new information
                self.update_contacts(contacts_roster)
        
        except IqError as e:
            # Handle IQ errors by printing the IQ packet that caused the error
            print(e.iq)
        except IqTimeout:
            # Handle a timeout error by printing a message
            print('Times Up! ⏳')

    # A notification will pop up when someone's in the room now
    def userOnlineRoom(self, presence):
        user_nick = presence['muc']['nick']
        room_name = presence['muc']['room']
        
        # Check if the user who joined is not the current user
        if user_nick != self.boundidUser.user:
            message = f'{user_nick} is in the room 🔅'
            print(message)
            self.rooms[room_name].append(message)

    # Remove contacts
    def deleteUser(self, idUser):
        jid_to_delete = idUser + SERVER
        
        # Delete the roster item for the specified JID
        self.del_roster_item(jid_to_delete)
        
        # Use a list comprehension to filter out the contact to delete
        self.contacts = [contact for contact in self.contacts if contact.idUser != idUser]

    # Remove accounts
    def deleteAccount(self):
        iq = self.Iq()
        iq['type'] = 'set'
        iq['from'] = self.boundidUser.bare
        iq['register']['remove'] = True
        try:
            result = iq.send()
            if result['type'] == 'result':
                print('Deleted Account ')
                self.disconnect()
        except IqError as e:
            print(e.iq)
            self.disconnect()
        except IqTimeout:
            print('Times Up! ⏳')
            self.disconnect()
