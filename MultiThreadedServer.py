import socket
import time
import argparse
from MultithreadedServer.Peer import *
from MultithreadedServer.Index import *
from _thread import *
import threading

lock = allocate_lock()


class Server:
    def __init__(self, port):
        self.portNo = port
        self.peerList = []
        self.indexList = []

    # thread function
    def tcpServer(self, c, addr):

        # lock acquired by client
        print('Connected to :', addr[0], ':', addr[1])

        # Until the socket is not closed

        while True:
            # data received from client
            bdata = c.recv(1024)
            data = bdata.decode()
            # print data send from client
            print(data)

            # parse the data to read the approciate command and do the necessary action
            client_message = data.split()
            print(client_message)


            # ADD
            if client_message[0] == "ADD":
                print("Acquiring lock")
                lock.acquire()
                print("Acquired lock")

                time.sleep(10)
                # Do the operation for add
                # Add RFC to index list and send success message

                # Create New Peer
                peer = Peer(addr[0], client_message[6])

                # Update PeerList
                self.peerList.append(peer)

                # List all Peers
                for peer in self.peerList:
                    print("Peer 1 Hostname = ", peer.hostname(), "Port No : ", peer.portno())

                # Create New Index
                index = Index(client_message[2], client_message[7], peer)
                self.indexList.append(index)
                msg2client = ""
                # send success response back to client
                msg2client = "P2P CI/1 200 OK" + "\n" + "RFC " + index.rfcNo + " " + index.rfcName
                c.sendall(msg2client.encode('ascii'))
                print(" Add Msg sent to Client \n", msg2client)
                lock.release()

            # LIST

            if client_message[0] == "LIST":
                msg2client = ""
                # if index is not empty send success else failure
                if len(self.indexList) != 0:
                    # c.send(status2client.encode('ascii'))

                    # List all Index
                    for index in self.indexList:
                        msg2client = msg2client + "Index RFC : " + index.rfcNo + " Title: " + index.rfcName + \
                                     " Host : " + index.peer.hostname() + " Port No : " + index.peer.portno() + "\n"
                    msg2client = msg2client + "P2P CI/1 200 OK"
                    c.sendall(msg2client.encode("ascii"))
                    # print(msg2client)

                else:
                    msg2client = "P2P CI/1 404 Not Found"
                    c.send(msg2client.encode("ascii"))

                print("List Msg sent to Client : \n", msg2client)

            # QUIT
            if client_message[0] == "QUIT":
                print("Deleting peer related entries ")
                '''
                # List all Peers
                for peer in self.peerList:
                    print("Peer : ", peer, " Hostname = ", peer.hostname(), " Port No : ", peer.portno())
                '''
                # Update PeerList : By removing this peer
                for peer in reversed(self.peerList):
                    if peer.hostname() == addr[0]:
                        print("removing peer ", peer)
                        self.peerList.remove(peer)

                # Update Index List : By removing all the RFC's associated with this peer
                for index in reversed(self.indexList):
                    if index.peer.hostname() == addr[0]:
                        print("Removing RFC : ", index.rfcNo," ", index.rfcName, "from Centralized Server")
                        self.indexList.remove(index)
                c.close()
                break

        # connection closed
        c.close()

def main():

    # Hostname and Port No. where Centralized Server is waiting for connections
    host = ""
    serverPort = args.listen

    mainServer = Server(serverPort)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, mainServer.portNo))
    print("socket binded to port", mainServer.portNo)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()

        # Start a new thread and return its identifier
        start_new_thread(mainServer.tcpServer, (c, addr))
    s.close()

main()