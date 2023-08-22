# This class contains the main details of a user (create an account or log in)
class userDetails():
    def __init__(self, jid, Email=None, Username=None, Name=None):
        self.jid = jid
        self.Email = Email
        self.Username = Username
        self.Name = Name
        self.messages = []

    def set_info(self, key, value):
        self.__setattr__(key, value)

    # Update fields
    def update(self, userC):
        for key in userC.__dict__.keys():
            if userC.__getattribute__(key) != None:
                self.__setattr__(key, userC.__getattribute__(key))
        return self

    def add_message(self, message):
        self.messages.append(message)

    def __str__(self) -> str:
        return str(self.__dict__)