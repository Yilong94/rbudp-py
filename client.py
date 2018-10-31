import socket
import time
import sys
import os
import pickle

# serverName = '127.0.0.1' # IP address or hostname of server
# serverPort = 12000      # port number of server
# clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # dynamically create port number of client socket

# message = input('Input lowercase sentence:')
# # In python3, strings are Unicode, hence need to be converted to bytes. In python2, strings are already bytestrings
# clientSocket.sendto(message.encode('utf-8'),(serverName, serverPort))       # attaches the destination address (servername,serverport) to the message and sends packet to the socket
# modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
# modifiedMessage = modifiedMessage.decode('utf-8')
# print (modifiedMessage)

# clientSocket.close()

# exit()

###########################################

class ClientSession:
    def __init__(self, clientName, client_UDPPort, serverName, server_UDPPort, server_TCPPort):
        # initialize variables
        self.clientName = clientName
        self.client_UDPPort = client_UDPPort
        self.serverName = serverName
        self.server_UDPPort = server_UDPPort
        self.server_TCPPort = server_TCPPort
        self.segmentid_list = []
        self.bytesarray = b''
        self.initializeConnection()
    
    def closeConnection(self):
        self.client_TCPSocket.close()
        self.client_UDPSocket.close()

    def initializeConnection(self):
        # create UDP socket 
        self.client_UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_UDPSocket.bind((clientName, client_UDPPort))
        # create TCP socket
        self.client_TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # setup 3-way handshake
        self.client_TCPSocket.connect((serverName, server_TCPPort))
        # send over information about UDP socket
        # self.client_TCPSocket.send(clientName.encode('utf-8'))
        # time.sleep(0.0001)
        # self.client_TCPSocket.send(str(client_UDPPort).encode('utf-8'))
        self.client_TCPSocket.send(pickle.dumps((clientName, client_UDPPort)))
        print("Client: Successfully connected to server")

    def receiveData(self):
        while True:
            self.filename = input("Type filename here: ")
            # sending filename on server
            self.client_TCPSocket.send(self.filename.encode('utf-8'))
            fileexist = int(self.client_TCPSocket.recv(1024).decode('utf-8'))
            if fileexist == 1:
                break
            else:
                print("Client: File does not exist. Please try again :(")
        
        # get info about max file size from server
        self.blocks = int(self.client_TCPSocket.recv(1024).decode('utf-8'))
        print("Client: Receiving data...")
        # set TCP socket to non-blocking to allow fast check for DONE signal
        self.client_TCPSocket.setblocking(False) 
        self.client_UDPSocket.settimeout(0.001)

        starttime = time.time()
        packetloss = 0
        while True:
            while True:
                try:
                    if self.client_TCPSocket.recv(1024).decode('utf-8') == 'DONE':
                        print("Client: Transmission done..")
                        break
                except socket.error as e:
                    pass
                try:
                    data, addr = self.client_UDPSocket.recvfrom(1026)    
                    self.segmentid_list.append(int.from_bytes(data[0:2], byteorder='big'))
                    self.bytesarray += data[2:]
                except socket.error as e:
                    pass

            missing = self.missing_elements(sorted(self.segmentid_list), 0, self.blocks-1)
            print("Client: Missing packets:", missing)

            if len(missing)==0:
                print("Client: File is fully received. Yay!")
                break
            else:
                packetloss+=len(missing)
                missingbytes = b''
                for idx in missing:
                    missingbytes += idx.to_bytes(2,byteorder='big')
                self.client_TCPSocket.send(missingbytes)

        endtime = time.time()
        self.assembleData()
        print("***************************************")
        print("Total time taken: {}s".format(round(endtime-starttime,5)))
        print("Percentage packet loss: {}%".format(round(packetloss/self.blocks,10)*100))
        print("***************************************")
    
    def assembleData(self):
        sorted_segmentid_list = sorted(enumerate(self.segmentid_list),key=lambda x:x[1])
        split_filename = os.path.splitext(self.filename)
        new_filename = split_filename[0]+'_copy'+split_filename[1]
        with open(new_filename,'wb') as f:
            for original, correct in sorted_segmentid_list:
                f.write(self.bytesarray[original*1024:(original+1)*1024])
        print("Client: File is successfully downloaded")

    def missing_elements(self, L, start, end):
        return sorted(set(range(start, end + 1)).difference(L))

if __name__=='__main__':
    # filename = sys.argv[1]
    clientName = sys.argv[1]
    client_UDPPort = 60000
    serverName = sys.argv[2]
    server_UDPPort = 12000
    server_TCPPort = 12001
    clientSession = ClientSession(clientName, client_UDPPort, serverName, server_UDPPort, server_TCPPort)
    clientSession.receiveData()
    clientSession.closeConnection()

# serverName = '127.0.0.1'
# server_UDPPort = 12000
# server_TCPPort = 12001

# clientName = '127.0.0.1'
# client_UDPPort = 60000

# # TODO: setup a UDP socket to prepare for UDP packets
# client_UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# client_UDPSocket.bind((clientName,client_UDPPort))
# #print(client_UDPSocket)
# #exit()

# # TODO: setup a TCP connection from client to server first
# client_TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_TCPSocket.connect((serverName, server_TCPPort)) # 3-way handshake is initiated
# client_TCPSocket.send(clientName.encode('utf-8'))
# time.sleep(0.001)
# client_TCPSocket.send(str(client_UDPPort).encode('utf-8'))
# time.sleep(0.001)
# blocks = int(client_TCPSocket.recv(1024).decode('utf-8'))

# client_TCPSocket.setblocking(False)     # set TCP socket to non-blocking to allow fast check for DONE signal
# # TODO: keeps track of packets received
# #f = open('a.jpg','wb')

# segmentid_list = []
# bytesarray = b''
# print('Receiving data...')
# while True:
#     try:
#         if client_TCPSocket.recv(1024).decode('utf-8') == 'DONE':
#             print("Transmission done..")
#             break
#     except socket.error as e:
#         pass
#     try:
#         data, addr = client_UDPSocket.recvfrom(1026)    
#         #print(int.from_bytes(data[0:2], byteorder='big'))
#         segmentid_list.append(int.from_bytes(data[0:2], byteorder='big'))
#         bytesarray += data[2:]
#     except socket.error as e:
#         pass

# # print(segmentid_list)
# # TODO: acknowledge DONE signal and reply with missing packets for retransmission
# missing = missing_elements(sorted(segmentid_list), 0, blocks-1)
# print("Missing packets:", missing)

# # if there are missing bytes
# while len(missing)!=0:
#     missingbytes = b''
#     for idx in missing:
#         missingbytes += idx.to_bytes(2,byteorder='big')
#     client_TCPSocket.send(missingbytes)  

#     while True:
#         try:
#             if client_TCPSocket.recv(1024).decode('utf-8') == 'DONE':
#                 print("Transmission done..")
#                 break
#         except socket.error as e:
#             pass
#         try:
#             data, addr = client_UDPSocket.recvfrom(1026)    
#             #print(int.from_bytes(data[0:2], byteorder='big'))
#             segmentid_list.append(int.from_bytes(data[0:2], byteorder='big'))
#             bytesarray += data[2:]
#         except socket.error as e:
#             pass
#     missing = missing_elements(sorted(segmentid_list), 0, blocks-1)
#     print("Missing packets:",missing)

# print("File is fully sent. Yay!")


# # reassemble the messages 
# #zipped = zip(segmentid_list, bytesarray)
# #sorted_bytearray = sorted(, key=)
# sorted_segmentid_list = sorted(enumerate(segmentid_list),key=lambda x:x[1])
# with open('a.pdf','wb') as f:
#     for original, correct in sorted_segmentid_list:
#         f.write(bytesarray[original*1024:(original+1)*1024])

# client_TCPSocket.close()
# client_UDPSocket.close()

