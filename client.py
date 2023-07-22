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

    