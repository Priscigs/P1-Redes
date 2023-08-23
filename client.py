# **********************************
#    Priscilla González - 20689
#              Redes
# **********************************

import base64
from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream.stanzabase import ET
from sleekxmpp.exceptions import IqTimeout, IqError
from sleekxmpp.plugins.xep_0004.stanza.form import Form
from userDetails import userDetails

SERVER = '@alumchat.xyz'

# Multi-User Chat https://xmpp.org/extensions/xep-0045.html
# Each room is identified as a "room JID" <room@service> (e.g., <jdev@conference.jabber.org>), 
# where "room" is the name of the room and "service" is the hostname at which the multi-user chat service is running.
# So added @conference to the server
ROOM_SERVER = '@conference.alumchat.xyz'
PORT = 5222

class Client(ClientXMPP):
    def __init__(self, jid, password, Name=None, Email=None, registering=False):
        ClientXMPP.__init__(self, jid, password)
        self.password = password
        self.Name = Name
        self.Email = Email
        self.registering = registering 
        self.to_chat = False 
        self.contacts = []
        self.rooms = {}
        self.connected = False
        self.add_event_handler('session_start', self.on_session_start)
        self.add_event_handler("register", self.on_register)
        self.add_event_handler("presence_subscribe", self.on_presence_subscribe)
        self.add_event_handler("presence_unsubscribe", self.on_presence_unsubscribe)
        self.add_event_handler("got_offline", self.on_got_offline)
        self.add_event_handler("got_online", self.on_got_online)
        self.add_event_handler("message", self.on_message)
        self.add_event_handler("changed_status", self.on_changed_status)
        self.add_event_handler("groupchat_invite", self.muc_invite)
        self.add_event_handler("connection_failed", self.on_connection_failed)
        self.add_event_handler("failed_auth", self.on_connection_failed)
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

    def on_session_start(self, event):
        self.presenceMessage('chat', 'available')
        self.update_roster(firts_time=True)
        self.connected = True

    # Send a message to an user
    def on_message(self, msg):
        show_response = True
        self.to_chat_type = None  # Inicializa to_chat_type como None u otro valor apropiado
        # For messages received from a groupchat
        if msg['type'] == 'groupchat':
            # get the nick
            nick = msg['mucnick']
            # If you sent the message, don't show the notification
            if nick == self.boundjid.user:
                show_response = False
            # For other's messages, show the notification
            else:
                # get the room
                room = msg['from'].bare.split('@')[0]
                # get the message
                message = msg['body']
                print(f'\n[{room}] {nick}: {message}')
                # add the message to the room chat history
                self.rooms[room].append(f'[{room}] {nick}: {message}')
                self.to_chat_type = 'room'
                self.message_receiver = room
        # For messages received from an user
        else:
            # remove all after @
            user = msg['from'].bare.split('@')[0]
            # If you sent the message, don't show the notification
            if user == self.boundjid.user:
                show_response = False
            # For other's messages, show the notification
            else:
                print(f'\n{user}: {msg["body"]}')
                # add the message to the chat history
                for contact in self.contacts:
                    if contact.jid == user+SERVER:
                        contact.add_message(f'{user}: {msg["body"]}')
                        self.to_chat_type = 'contact'
                        self.message_receiver = user
                        break
        if show_response:
            print("Wanna Answer? (Y/n)")
            self.to_chat = True

    # Shows the chat history of a contact
    def chatHis(self, jid): #show_chat
        for contact in self.contacts:
            if contact.jid == jid:
                for message in contact.messages:
                    print(message)
                break

    # Shows the chat history of a contact
    def roomHis(self, room):
        if room in self.rooms.keys():
            for message in self.rooms[room]:
                print(message)
        else:
            print('Youre not in the room! 💀')

    # A notification will pop uo when someone's offline the server
    def on_got_offline(self, presence):        
        if self.boundjid.bare not in str(presence['from']):
            u = self.jid_to_user(str(presence['from']))
            print(f'\n{u} is disconnected!')
            for i in self.contacts:
                if i.jid == str(presence['from']):
                    self.contacts.remove(i)
                    break

    # A notification will pop uo when someone's online
    def on_got_online(self, presence):
        if self.boundjid.bare not in str(presence['from']):
            u = self.jid_to_user(str(presence['from']))
            print(f'\n{u} is connected!')
            for i in self.contacts:
                if i.jid == str(presence['from']):
                    i.online = True
                    break

    # Get the roster (contacts list) and updates the contacts list
    def update_roster(self, firts_time=False):
        try:
            roster = self.get_roster()
            contacts_roster = []
            for jid in roster['roster']['items'].keys():
                contact = userDetails(jid)
                for k, v in roster['roster']['items'][jid].items():
                    contact.set_info(k, v)
                contacts_roster.append(contact)
            if firts_time:
                self.contacts = contacts_roster
            else:
                self.update_contacts(contacts_roster)
        except IqError as e:
            print(e.iq)
        except IqTimeout:
            print('Times Up! ⏳')

    # Send message and updates the chat history of the contact
    def sendMessagesToServerSingle(self, jid, message): #send_message_to_user
        # Send the message to the user
        self.send_message(mto=jid + SERVER, mbody=message, mtype='chat')

        # Update the chat history of the contact
        for contact in self.contacts:
            if contact.jid == jid:
                contact.add_message(f'>>> (You): {message}')
                break

    # A notification will pop up when someone added you as a friend
    def on_presence_subscribe(self, presence):
        username = presence['from'].bare
        print(f'\n{username} wants to add you as a friend 🫶🏼')

    # A notification will pop up when someone removed you from their friend's list
    def on_presence_unsubscribe(self, presence):
        username = presence['from'].bare
        print(f'\n{username} has removed you from their friends list 🤡')

    # A notification woll pop up when a status has changed
    def on_changed_status(self, presence):
        username = presence['from'].bare
        print(self.client_roster.presence[username]['status'])
        print(f'\n{username} has changed his/her status to: {self.client_roster.presence[username]["status"]}')

    # Connect to the server, used on login and register
    def login(self):
        result = self.connect((SERVER[1:], PORT), use_ssl=False, use_tls=False)
        print(result)
        if result:
            self.process()
            return True
        return False

    # Failed connection
    def on_connection_failed(self, error):
        print(f'\nError!!! ❌: {error}\nPress "Enter" to try again!!')
        self.connected = False
        self.disconnect()

    # Leave a presence message
    def presenceMessage(self, show, status):
        self.send_presence(pshow=show, pstatus=status)

    # Add a new contact to the contact list if it doesn't exist
    def add_contact(self, jid, subscription_meessage):
        can_add_contact = True
        for contact in self.contacts:
            if contact.jid == jid:
                print('This user already exists')
                can_add_contact = False
                continue
        if can_add_contact:
            self.send_presence(
                pto=jid + SERVER, pstatus=subscription_meessage, ptype="subscribe")
            
    # Add new contacts
    def addingC(self, jid, subscription_message): #add_contact
        # Check if the user already exists in the contact list
        if any(contact.jid == jid for contact in self.contacts):
            print('This user already exists')
        else:
            # Send a subscription request to the new contact
            self.send_presence(pto=jid + SERVER, pstatus=subscription_message, ptype="subscribe")

    # show all the users in the server or show users that match the jid
    def gettingC(self, jid='*'):
        iq = self.get_search_iq(jid)
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
                                jid=values['jid'], Email=values['Email'], Username=values['Username'], Name=values['Name']))
        except IqError as e:
            print(e.iq)
        except IqTimeout:
            print('Times Up! ⏳')
        print("\nUsers Connected:")
        for user in users:
            print(user)
        return users

    # Get the roster (contacts list) and search for contacts that match the jid
    def get_contact_by_jid(self, jid):
        self.update_roster()
        groups = self.client_roster.groups()
        contacts = []
        for group in groups:
            for user in groups[group]:
                contact = userDetails(jid=user)
                # if user string icludes jid
                if user.find(jid) != -1:
                    user_roster = self.client_roster[user]
                    contact.set_info('Name', user_roster['name'])
                    contact.set_info(
                        'Subscription', user_roster['subscription'])
                    contact.set_info('Groups', user_roster['groups'])
                    connected_roster = self.client_roster.presence(user)
                    # Presence info set (show, status)
                    if connected_roster.items():
                        for _, state in connected_roster.items():
                            for k, v in state.items():
                                contact.set_info(k, v)
                    contacts.append(contact)
        print("\nFriends List 👥:")
        for contact in contacts:
            print(contact)
        return contacts

    # Search in the contact list and in the server
    def searchU(self, jid):
        self.update_contacts(self.get_contact_by_jid(jid))
        self.gettingC(jid)

    # Creates an Iq with the specific attributes
    def create_iq(self, **kwargs):
        iq = self.Iq()
        iq.set_from(self.boundjid.full)
        for k, v in kwargs.items():
            iq[k] = v
        return iq

    # Custom Iq for search users
    def get_search_iq(self, search_value='*'):
        iq = self.create_iq(type="set", id="search_result",
                            to="search." + self.boundjid.domain)
        form = Form()
        form.set_type("submit")
        form.add_field(
            var='FORM_TYPE',
            type='hidden',
            value='jabber:iq:search'
        )
        form.add_field(
            var='Username',
            type='boolean',
            value=1
        )
        form.add_field(
            var='search',
            type='text-single',
            value=search_value
        )
        query = ET.Element('{jabber:iq:search}query')
        query.append(form.xml)
        iq.append(query)
        return iq

    # Receive a new list of contacts and update the self.contacts list, adding new contacts and updating existing ones.
    def update_contacts(self, contacts):
        for contact in self.contacts:
            for new_contact in contacts:
                if contact.jid == new_contact.jid:
                    contact.update(new_contact)
                    break
                else:
                    self.contacts.append(new_contact)

    # Register a new user in the server
    def on_register(self, event):
        if self.registering:
            iq = self.Iq()
            iq['type'] = 'set'
            iq['register']['username'] = self.boundjid.user
            iq['register']['password'] = self.password
            iq['register']['name'] = self.Name
            iq['register']['email'] = self.Email
            try:
                iq.send(now=True)
            except IqError as e:
                print(e.iq)
            except IqTimeout:
                print('Times Up! ⏳')

    # Create a group chat room
    def createGrupo(self, room):
        # Combine the room name with the server to form the complete room JID
        room_with_server = room + ROOM_SERVER
        
        # Join the group chat room with the bound user as the owner
        self.plugin['xep_0045'].joinMUC(room_with_server, self.boundjid.user, wait=True)
        
        # Set the affiliation of the bound user to 'owner' in the room
        self.plugin['xep_0045'].setAffiliation(room_with_server, self.boundjid.full, affiliation='owner')
        
        # Configure the room settings, possibly with options like who can join
        self.plugin['xep_0045'].configureRoom(room_with_server, ifrom=self.boundjid.full)
        
        # Initialize an empty list to store messages for this room
        self.rooms[room] = []

    # Join an existing group chat room
    def joinGroup(self, room):
        # Combine the room name with the server to form the complete room JID
        room_with_server = room + ROOM_SERVER
        
        # Join the group chat room with the bound user
        self.plugin['xep_0045'].joinMUC(room_with_server, self.boundjid.user)
        
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
            self.rooms[room].append(f'[{room}] {self.boundjid.user}: {message}')

    # A notification will pop up when someone's in the room now
    def muc_online(self, presence):
        # If user joined is not the current user
        if presence['muc']['nick'] != self.boundjid.user:
            print(f'{presence["muc"]["nick"]} is now in the room 🟢')
            self.rooms[presence['muc']['room']].append(f'{presence["muc"]["nick"]} is now in the room 🟢')

    # A notification will pop up when you're invited to a new eoom
    def muc_invite(self, inv):
        print('\nRoom Invitation 👾')

    # Remove contacts
    def deleteFriend(self, jid):
        jid_to_delete = jid + SERVER
        
        # Delete the roster item for the specified JID
        self.del_roster_item(jid_to_delete)
        
        # Use a list comprehension to filter out the contact to delete
        self.contacts = [contact for contact in self.contacts if contact.jid != jid]

    # Remove accounts
    def deleteAccount(self):
        iq = self.Iq()
        iq['type'] = 'set'
        iq['from'] = self.boundjid.bare
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
