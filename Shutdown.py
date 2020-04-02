import os
import platform
import subprocess
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

class ShutdownClient():
    def __init__(self):
        self.currentOS = platform.system()
        self.port = 7980
        self.serverIP = "192.168.1.145" # address of BigRed
        self. shutdownCommandLookUp = { 'Linux': ['systemctl', 'poweroff'],
                                        'Darwin': ['osascript', '-e','tell app "System Events" to shut down'],
                                        'Windows': ['shutdown']}

    def connectToServerSocket(self):
        s = socket(AF_INET, SOCK_STREAM)
        print("Attempting to connect to Server")
        s.settimeout(None)# so that the clients won't timeout waiting for a server (if I forget to turn on the windows machine)
        s.connect((self.serverIP, self.port))
        print("Connected to Server!")
        return s

    def listenForShutdown(self, s: socket):
        try:
            data = s.recv(1)
            if not data:
                command = self.shutdownCommandLookUp[self.currentOS]
                subprocess.call(command)
        except ConnectionResetError:
            print("Server is gone")
            command = self.shutdownCommandLookUp[self.currentOS]
            subprocess.call(command)
            print("running shutdown")


class ShutdownServer():
    def __init__(self):
        self.currentOS = platform.system()
        self.port = 7980
        self.ip = '192.168.1.145'

    def createServerSocket(self):
        print(f"Creating socket server for {self.currentOS} server on {self.ip}")
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((self.ip, self.port))
        print("Server Listening...")
        s.listen()
        while True:
            conn, addr = s.accept()
            print(f"Connection Accepted: Client {addr} connected!")
            t = Thread(target=self.handleClient, args=(conn,))


def runClient():
    sc = ShutdownClient()
    s = sc.connectToServerSocket()
    sc.listenForShutdown(s)

def runServer():
    ss = ShutdownServer();
    ss.createServerSocket()


if __name__ == '__main__':
    if platform.system() != 'Windows': # currently my main PC is windows so windows is the server
        runClient()
    else:
        runServer()