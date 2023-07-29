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