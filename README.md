# P1-Redes

- Priscilla González Sandoval - 20689
- Universidad del Valle de Guatemala
- Catedrático: Jorge Yass
- Redes | Sección 20

## Objectives

- Implement a standards-based protocol.
- Understand the purpose of the XMPP protocol.
- Understand how XMPP protocol services work.
- Understand the asynchronous programming basics required for some of the development needs of network development needs.

## Project requirements

    ╔═══════════════╗
    ║      Menu     ║
    ╠═══════════════╣
    ║  1. Login     ║
    ║  2. Register  ║
    ║  3. Log Out   ║
    ╚═══════════════╝

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

‼️ Add `@alumchat.xyz` to the registration email so it works correctly

## How to run the project

- Run `main.py` to see the `MAIN MENU`
- Option 1 -> Login
    - Write username, password and instantly will head you to the menu
- Option 2 -> Register
    - Write username, password, name and email (‼️) and instantly will head you to the menu
- Option 3 -> Log Out

- `MAIN MENU`
- Option 1 -> Show Connected Users 
    - Automatically displays all users on the server 
- Option 2 -> Add User               
    - It will ask for the username to add
- Option 3 -> Show User Details
    - It will ask for the username to query and will show whether it is in your contacts list or on the server
- Option 4 -> Send a Private Message
    - It will ask for the username to send a private message
- Option 5 -> Create Group
    - It will ask for the name of the group to be created
- Option 6 -> Join Group
    - It will ask for the name of the group to join
- Option 7 -> Send Message to Group
    - It will ask for the name of the group to send the message to
- Option 8 -> Send Presence
    - It will ask for the state you want to be in, followed by the message you want to write
- Option 9 -> Delete User
    - It only deletes users in your contact list
- Option 10 -> Delete Account
    - It will delete the account you are in
- Option 11 -> End
    - Log Out

## Library required

```
pip install sleekxmpp
```

## References

- The `client.py` file was based on this link: (https://sleekxmpp.readthedocs.io), a brief documentation of the library `sleekxmpp`

