################################################
##          Imports, Constants
################################################
from time import *                              
from SocketServer import ThreadingTCPServer, BaseRequestHandler
endl            = '\r\n'
backspace       = '\b'
creturn         = '\r'
tab             = '\t'
space           = ' '
maxname         = 8
packet          = 1024                   
HOST            = 'localhost'                       
PORT            = 65438                    
ADDRESS         = (HOST, PORT)          
connections     = {}                
roomlist        = {}                   
#################################################
##################################################
##          Big Strings
##################################################
## This stuff is self-explanatory. Any one of these
## can be changed to whatever you want. The 'artwork'
## variable is fun to play with.
artwork = """          ,--.!,\r
       __/   -*-\r
     ,d08b.  '|`         HNCS version 2.0\r
     0088MM              (c)2007 J.Graff\r
     `9MMP'\r
"""
info = '''\r\n
---------------------------------------------------\r
                    INFO\r
---------------------------------------------------\r
Home Network Chat Server (HNCS) is an open source\r
and freely distributable chatserver written and\r
maintained by John M. Graff in the Python scripting\r
language ([url]http://www.python.org[/url]) and licensed under\r
the GPL (see [url]http://www.gnu.com[/url] for details).\r
\r\n
Source code is available upon request. E-mail the\r
author at [email]jmgraff@student.ysu.edu[/email] for more informa-\r
tion.\r
----------------------------------------------------\r\n'''
clientHelp = '''\r
-----------------------------------------------------\r
                  COMMANDS\r
-----------------------------------------------------\r\n
'c'          clear screen\r
'w'          print userlist\r
'i'          info about this program\r
'l'          list of rooms\r
'r'          list of people in current room\r
'q'          disconnect\r
'?'          show this menu\r
<Enter>      type & send a message\r\n
NOTE: Windows users only need to press \r
the key. UNIX/Linux/BSD users must press\r
<Enter> after the key.\r
-----------------------------------------------------\r'''

gpl = '''HNCS 2.0, Copyright (C) 2007 John M. Graff\r
HNCS comes with ABSOLUTELY NO WARRANTY; This is free\r
software,and you are welcome to redistribute it under\r
the terms and conditions of the GPL.\r\n
See [url]http://www.gnu.com[/url] for details.;\r'''

login = '''\r\nWelcome to the server!\r\n
Before you start, choose a Nickname.(Max 8 characters)\r
If it's too long or already in use, you'll have to try\r
again.\r\n
Nickname: '''
##################################################
###################################################
##          The HNCS Class
###################################################
class HNCS(ThreadingTCPServer):
    def verify_request(self, request, client_address):
        for key in connections:
            if connections[key].client_address[0] == client_address[0]:
                if client_address[0] != '127.0.0.1':
                    return False
        return True
    def welcome(self):
        return '''______________________________________________________
------------------------------------------------------
%s
______________________________________________________
------------------------------------------------------
* Server started %s
* Waiting for connections on port %i
''' % (gpl, ctime(), PORT)
##################################################
##################################################
##          The Room Class
##################################################
class Room:
    def __init__(self, name, starter):
        self.listeners = []
        self.name = name
        roomlist[self.name] = self
        self.listeners.append(starter)      
    def cleanup(self, connection):
        self.listeners.remove(connection)
        if len(self.listeners) == 0:
            del roomlist[self.name]   
    def whoHere(self):
        container = ''
        for listener in self.listeners:
            container += listener.__str__()
        format =  '[ %s ]' % (container)
        return endl + format + endl
    def listRooms(self):
        container = ''
        for key in roomlist:
            container += (roomlist[key].__str__() + endl)
        format = '''\r
-----------------------------------------------------\r
                  ROOMS\r
-----------------------------------------------------\r\n
%s\r
-----------------------------------------------------\r'''% container
        return format
    def welcome(self):
        return endl + '\t*  You are now in :: %s ::  *\r\n %s\r\n' % (self.name, self.whoHere())
    def __str__(self):
        return ':: %s ::\t\t|\t\t%i user(s)' % (self.name, len(self.listeners))
###################################################
##          The Connection Class
###################################################
# This is where it all goes down. Upon connection,
# this class automatically runs the self.setup()
# function which sets up a self.username and appends
# a unique instance of the User class to the 'connec-
# tions' list. self.getPress is an infinite loop and
# is where the majority of the action takes place.
class Connection(BaseRequestHandler):    
    def setup(self):
        print '[!] %s %s' % (self.client_address[0], ctime())
        self.room = 0
        self.login()
        self.joinRoom('lobby')
        print '- %s logged in as "%s"' % (self.client_address[0], self.name)
        self.broadcast('\r\n\t*  %s connected %s  *\r\n' % (self, ctime()))
        connections[self.name] = self
        self.request.send('You are now logged in as "%s".\r\n' % self.name)        
    def login(self):
        self.request.send(login)
        string = self.getString()
        while len(string) > maxname or connections.has_key(string):
            self.request.send('\r\nSorry, try again: ')
            string = self.getString()
        if len(string) < maxname:
            string = (space * (maxname - len(string))) + string
        self.name = string       
    def handle(self):
        sleep(2)
        self.request.send(self.welcome())           # send the welcome note
        self.getPress()                             # wait for commands until session is terminated        
    def finish(self):
        self.broadcast('\r\n\t*  %s has disconnected  *\r\n' % self)
        print '[x] %s %s (%s)' % (self.client_address, self.name, ctime(), )
        del connections[self.name]
        self.leaveRoom()
        self.request.close()
    def getPress(self):
        while True:
            try:
                press = self.request.recv(packet)
                self.request.send('\b ')                    # keep the cursor from moving
                self.request.send('\b')                     #           "
                if press in ('?', '?\r\n'):                 # print the help menu
                    self.request.send(clientHelp)
                elif press in ('w', 'w\r\n'):               # print who is online
                    self.request.send(self.who())
                elif press in ('r', 'r\r\n'):               # print users in room
                    self.request.send(self.room.whoHere())
                elif press == endl:                         # go to the message prompt
                    self.message()
                elif press in ('c', 'c\r\n'):               # clear the screen (kind of a primative way, eh?)
                    self.request.send(endl * 100)
                elif press in ('i', 'i\r\n'):               # print the info string
                    self.request.send(info)
                elif press in ('j', 'j\r\n'):
                    self.changeRoom()
                elif press in ('l', 'l\r\n'):
                    self.request.send(self.room.listRooms())
                elif press in ('q', 'q\r\n'):               # leave the loop and terminate the session
                    break
                else:
                    self.request.send('\r\n\t*  Dude, no. Type ? for'
                                      ' a list of commands.  *\r\n')
            except: 
                break                                                                           
    def getString(self):
        string      = ''
        keypress    = []
        press       = self.request.recv(packet)                 # get a keypress
        if len(press) <= 1:                                     # IF CLIENT IS IN CHAR MODE... (WINDOWS)
            while press != endl:                                    # while user isn't finished,
                if press == '\b':                                       # if it was a backspace,
                    if (len(keypress) > 0):                                     # and the keypress array isn't empty,
                        self.request.send(' \b')                                    # send a coverup so it looks like a backspace
                        keypress.pop()                                              # and remove last char
                    else:                                                       # if array is empty
                        while press == '\b':                                        # while still pressing backspace
                            self.request.send(' ')                                      # send blank
                            press = self.request.recv(packet)                           # get and test a new press
                        if press == endl: break
                        keypress.append(press)
                else:
                    keypress.append(press)                            # if it wasn't a backspace, append it to array
                press = self.request.recv(packet)                       # get a new press
            for key in keypress:                                    # for each key held in keypress
                string += key                                           # add it to the string

        else:                                               # IF THE CLIENT IS IN LINE MODE (*NIX), 
            string = press                                      # the press is the string.
        if endl in string:                                  # if an end-of-line is in the string,
            string = string.strip(endl)                         # remove it.
        return string                                       # return the string
    def message(self):
        self.request.send('> %s: ' % self.name)
        string = self.getString()
        if len(string) == 0:
            self.request.send('\t<no message sent>\r\n')
        else:
            msg = '\r\n> %s: %s\r\n' % (self.name, string)
            self.roomcast(msg)                        
    def broadcast(self, data):
        for key in connections:
            if connections[key] != self:
                connections[key].request.send(data)
    def roomcast(self, data):
        for listener in self.room.listeners:
            if listener != self:
                listener.request.send(data)
    def leaveRoom(self):
        if self.room:
            self.room.cleanup(self)
    def changeRoom(self):
        self.request.send('\r\njoin room: ')
        string = self.getString()
        if len(string) == 0:
               self.request.send('\t<aborted>\r\n')
        else:
               self.joinRoom(string)              
    def joinRoom(self, roomname):
        if self.room:                                                                  
            if self.room.name == roomname:                                                   
                self.request.send('\r\n\t*  You are already in ::%s::  *\r\n' % self.room.name)        
            else:
                self.room.cleanup(self)
                if roomlist.has_key(roomname):
                    self.room = roomlist[roomname]
                    self.room.listeners.append(self)
                    self.request.send(self.room.welcome())
                else:
                    self.room = Room(roomname, self)
                    self.request.send(self.room.welcome())
        else:                                                                          
            if roomlist.has_key(roomname):
                self.room = roomlist[roomname]
                self.room.listeners.append(self)
            else:
                self.room = Room(roomname, self)     
    def who(self):
        container = ''
        for user in connections:
            container += user.__str__()
        format = '[%s]' % container
        return endl + format + endl
    def welcome(self):
        return '''\r\n
%s
_______________________________________________________\r
-------------------------------------------------------\r
%s\r
\t\tType '?' for help.\r
_______________________________________________________\r
-------------------------------------------------------\r
Local time is %s\r
%s
''' % (gpl, artwork, ctime(), self.room.welcome())


    def __str__(self):
        return ' %s ' % self.name
###################################################

server = HNCS(ADDRESS, Connection)

if __name__ == '__main__':
    print server.welcome()
    server.serve_forever()
