# Import socket module
import socket
import sys
from _thread import *


class Client:
    def __init__(self, name, portNo):
        self.hostname = name
        self.severPort = portNo

    def peerServer(self, ):
        peerServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peerServerSocket.bind((self.hostname, self.severPort))
        print("peer Server listening on port", self.severPort)
        # put the socket into listening mode
        peerServerSocket.listen(5)
        while True:
            c, addr = peerServerSocket.accept()
            # lock acquired by client
            print('Peer is Connected to another peer with IP address and port :', addr[0], ':', addr[1])

            # request received from peer
            bdata = c.recv(1024)
            data = bdata.decode()
            # print data send from client
            print(data)

            peerMessage = data.split()
            print(peerMessage)
            try:
                # Open file, read content and send contents over socket to the peer
                filename = peerMessage[2]
                with open(filename, "rb") as f:
                    success = "Sending Metadata"
                    c.sendall(success.encode())
                    data = f.read()
                c.sendall(data)
                print("File Transfer Complete !!!")
            except IOError as e:
                print("Caught the I/O error.")
                data = "Error 404 Not Found. RFC not found. Check RFC name"
                c.sendall(data.encode())
            finally:
                c.close()


def Main():

    # clientIP - IP address of this client
    # uploadServerPort : Port no on which client will communicate with other peers/client
    # ---------------------------------------------------------------------------------

    uploadServerPort = 8888
    clientIP = ""
    client = Client(clientIP, uploadServerPort)
    # ---------------------------------------------------------------------------------

    # Connection to Centralized Server
    # serverIP : IP address on which Centralized Server is Listening for Clients/Peers
    # serverPort : Port No. on which Centralized Server is Listening for Clients/Peers
    # ---------------------------------------------------------------------------------
    serverIP = '127.0.0.1'
    # serverIP = '152.7.99.49'
    version = "P2P CI/1"
    # Define the port on which you want to connect
    serverPort = 7734

    # Creating a socket to connect to Centralized Server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    client_socket.connect((serverIP, serverPort))
    # ---------------------------------------------------------------------------------

    # ---------------------Establishing PeerServer-------------------------------------
    # New thread to listen to peer connections
    # establish connection with client
    # Start a new thread and return its identifier
    start_new_thread(client.peerServer, ( ))
    # ----------------------------------------------------------------------------------

    while True:

        print("1. To ADD RFC information to Centralized Server")
        print("2. To DISPLAY all RFC information stored in Centralized Server")
        print("3. To GET RFC information to Centralized Server")
        print("0. To exit")

        choice = input("Enter your choice")

        if choice == '1':
            # ADD

            # Get RFC No
            rfcNo = input("Get RFC No.")

            # Get RFC Title
            rfcTitle = input("Get RFC Title")

            # Send to Server
            # make string to send to server
            msg2server = "ADD" + " " + "RFC" + " " + str(rfcNo) + " " + version + " " + 'localhost' + " " + \
                         str(uploadServerPort) + " " + rfcTitle
            client_socket.send(msg2server.encode('ascii'))
            print("Msg sent to server")
            bdata = client_socket.recv(1024)
            data = bdata.decode()
            print(data)

        elif choice == '2':
            # DISPLAY
            msg2server = "LIST ALL" + " " + version + " " + 'localhost' + " " + str(serverPort) + "\n"
            client_socket.send(msg2server.encode('ascii'))
            data = ""
            while True:
                part = client_socket.recv(1024)
                data = data + part.decode()
                # if "200 OK" in data or "P2P CI/1 404 Not Found" in data:
                if len(part.decode()) < 1024:
                    break
            print(data)

        elif choice == '3':
            # GET
            print("Get RFC")
            # Get RFC No
            rfcNo = input("Enter RFC No.")

            # Enter Peer IP
            peerIP = input("Enter Peer IP")

            # Enter Peer PortNo.
            peerPortNo = input("Enter Peer port No.")

            # Send get request to peer
            msg2peer = "GET" + " " + "RFC" + " " + str(rfcNo) + " " + version + " " + 'localhost'
            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                peerSocket.connect((peerIP, int(peerPortNo)))
                peerSocket.send(msg2peer.encode('ascii'))

                print("Msg sent to peer")
                datab = peerSocket.recv(1024)
                data = datab.decode()
                if "404 Not Found" in data:
                    print(data)
                else:
                    # Open a file and write to it
                    filename = rfcNo
                    with open(filename, "wb") as f:
                        while True:
                            part = peerSocket.recv(1024)
                            datab = datab + part
                            if len(part) == 0:
                                break
                        f.write(datab)
                        print("File Received !!!")
            except socket.error:
                # write error code to file
                print("400 Bad Request")
                print("Error in socket connection. Check IP address and Peer Port No.")
            finally:
                peerSocket.close()

        elif choice == '0':
            # Quit
            msg2server = "QUIT" + " " + version + " " + 'localhost' + " " + str(serverPort) + "\n"
            client_socket.send(msg2server.encode('ascii'))
            client_socket.close()
            sys.exit(0)

        else:
            print("400 Bad Request")
            print("Check Menu")

    # close the connection
    client_socket.close()


if __name__ == '__main__':
    Main()