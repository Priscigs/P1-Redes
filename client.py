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
        self.add_event_handler("presence_subscribe", self.subscribe)
        self.add_event_handler("presence_unsubscribe", self.unsubscribe)
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


    