import socket
import time
import sys
import os
import math
import pickle

# serverName = '127.0.0.1'
# serverPort = 12000
# serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# serverSocket.bind((serverName, serverPort))     # explicitly assign port number to socket
# print ("The server is ready to receive")

# while 1:
#     message, clientAddress = serverSocket.recvfrom(2048)    # clientAddress is a tuple (IP addr, port number)
#     print('addr',clientAddress)
#     message = message.decode('utf-8')
#     modifiedMessage = message.upper()
#     serverSocket.sendto(modifiedMessage.encode('utf-8'), clientAddress)

# exit()

###########################################

class ServerSession:
    def __init__(self, serverName, server_UDPPort, server_TCPPort, transrate):
        self.serverName = serverName
        self.server_UDPPort = server_UDPPort
        self.server_TCPPort = server_TCPPort
        self.buffer_size = 1024
        # self.sleeptime = 1/((float(transrate)*1000000/8)/(self.buffer_size+2)) + 0.0001 # 0.0001 to account for transmission time
        self.sleeptime = 1/((float(transrate)*1000000/8)/(self.buffer_size+2)) # without transmission time
        self.initializeConnection()

    def initializeConnection(self):
        # wait for TCP connection from client
        self.server_TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_TCPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow reuse of port number
        self.server_TCPSocket.bind((self.serverName, self.server_TCPPort))
        self.server_TCPSocket.listen(1)
        print('Server: Listening for connections')
        
        while True:
            self.connection_TCPSocket, addr = self.server_TCPSocket.accept()
            print("Server: Connection accepted")
            # self.clientName = self.connection_TCPSocket.recv(1024)
            # self.clientName = self.clientName.decode('utf-8')
            # self.client_UDPPort = self.connection_TCPSocket.recv(1024)
            # self.client_UDPPort = int(self.client_UDPPort.decode('utf-8'))
            clientaddr = self.connection_TCPSocket.recv(1024)
            self.clientName, self.client_UDPPort = pickle.loads(clientaddr)

            # send over number of blocks
            # self.filename = 'test2.JPG' # TODO: to be changed
            # filesize = os.path.getsize(self.filename)
            # blocks = math.ceil(filesize/1024)
            # self.connection_TCPSocket.send(str(blocks).encode('utf-8'))

            # TODO: start a UDP session to send packets over
            self.server_UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_UDPSocket.bind((serverName, server_UDPPort))
            break
    
    def closeConnection(self):
        self.server_UDPSocket.close()
        self.server_TCPSocket.close()
        self.connection_TCPSocket.close()

    def sendData(self):
        print("Sleep time",self.sleeptime)

        print("Server: Awaiting filename from client")
        while True:
            self.filename = self.connection_TCPSocket.recv(1024)
            # check whether file exists in current directory
            if os.path.isfile(self.filename):
                self.connection_TCPSocket.send('1'.encode('utf-8'))
                break
            else:
                self.connection_TCPSocket.send('0'.encode('utf-8'))
                print("Server: File does not exist. Continue waiting for filename")

        # TODO: might need a time.sleep() to delay two consecutive send()
        filesize = os.path.getsize(self.filename)
        blocks = math.ceil(filesize/1024)
        self.connection_TCPSocket.send(str(blocks).encode('utf-8'))

        with open(self.filename, 'rb') as f:
            print("Server: Sending data over...")
            bytesarray = b''   # a bytearray for temporary storage of bytes from file for retrieval
            data = f.read(self.buffer_size)
            segment_id = 0 # use 16 bits to range from 0 to 65535
            while(data):
                
                segment_id_bytes = segment_id.to_bytes(2,byteorder='big')
                
                data = segment_id_bytes + data  # sending over 2 bytes of segment id + 1024 bytes of data 
                
                bytesarray += data # this code shows a substantial increase in time taken 
                starttime = time.time()
                self.server_UDPSocket.sendto(data, (self.clientName, self.client_UDPPort)) # this code shows a subtantial increase in time taken. might be due to client side taking time as well
                if segment_id%100==0:
                    print("Time taken for 1 transmission: {}".format(time.time()-starttime))
                time.sleep(self.sleeptime)
                data = f.read(self.buffer_size)
                segment_id+=1


            
            while True:
                # time.sleep(1) # wait for client for a while
                # once done, send a DONE signal and wait for next message
                self.connection_TCPSocket.send('DONE'.encode('utf-8'))
                missingbytes = self.connection_TCPSocket.recv(1024)
                missing = [int.from_bytes(missingbytes[i:i+2], byteorder='big') for i in range(0,len(missingbytes),2)]

                if len(missing)==0:
                    break
                else:
                    for idx in missing:
                        self.server_UDPSocket.sendto(bytesarray[idx*1026:(idx+1)*1026], (self.clientName, self.client_UDPPort))
                        time.sleep(self.sleeptime)

if __name__=='__main__':
    serverName = sys.argv[1]
    server_UDPPort = 12000
    server_TCPPort = 12001
    transrate = sys.argv[2] # user-defined rate in megabits per second (Mbps)
    serverSession = ServerSession(serverName, server_UDPPort, server_TCPPort, transrate)
    serverSession.sendData()
    serverSession.closeConnection()


# filename = 'test.pdf'
# buffer_size = 1024
# rate = sys.argv[1] # some user-defined rate in megabits per second (Mbps). should be below the bandwidth in 
# sleeptime = 1/((float(rate)*1000000/8)/(buffer_size+2)) + 0.0001 # 0.0001 to account for transmission time

# serverName = '127.0.0.1'
# server_UDPPort = 12000
# server_TCPPort = 12001

# # TODO: accept a TCP connection from client
# server_TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_TCPSocket.bind((serverName, server_TCPPort))
# server_TCPSocket.listen(1)
# print('The server is ready to listen for connections')
# while True:
#     connection_TCPSocket, addr = server_TCPSocket.accept()
#     clientName = connection_TCPSocket.recv(1024)
#     clientName = clientName.decode('utf-8')
#     client_UDPPort = connection_TCPSocket.recv(1024)
#     client_UDPPort = int(client_UDPPort.decode('utf-8'))

#     # send over number of blocks
#     filesize = os.path.getsize(filename)
#     blocks = math.ceil(filesize/1024)
#     connection_TCPSocket.send(str(blocks).encode('utf-8'))

#     #print(client_TCPPort)
#     #print(int(client_TCPPort.decode('utf-8')))

#     # TODO: allow client to choose which file to send over 
#     # filename = connection_TCPSocket.recv(1024)

#     # TODO: start a UDP session to send packets over
#     server_UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     server_UDPSocket.bind((serverName, server_UDPPort))

#     #f = open(filename, 'rb')
#     with open(filename, 'rb') as f:
#         bytesarray = b''   # a bytearray for temporary storage of bytes from file for retrieval
#         data = f.read(buffer_size)
#         segment_id = 0 # use 16 bits to range from 0 to 65535
#         while(data):
#             segment_id_bytes = segment_id.to_bytes(2,byteorder='big')
#             data = segment_id_bytes + data  # sending over 2 bytes of segment id + 1024 bytes of data 
#             #print(data)
#             #print(len(data))
#             #print(type(data))

#             bytesarray += data

#             server_UDPSocket.sendto(data, (clientName, client_UDPPort))
#             time.sleep(sleeptime)

#             data = f.read(buffer_size)
#             segment_id+=1
        
#         # once done, send a DONE signal and wait for next message
#         connection_TCPSocket.send('DONE'.encode('utf-8'))
#         missingbytes = connection_TCPSocket.recv(1024)
#         missing = [int.from_bytes(missingbytes[i:i+2], byteorder='big') for i in range(0,len(missingbytes),2)]

#         # resend the blocks that are missing
#         while len(missing)!=0:
#             for idx in missing:
#                 server_UDPSocket.sendto(bytesarray[idx*1026:(idx+1)*1026], (clientName, client_UDPPort))
#                 time.sleep(sleeptime)
#             # wait for done signal again
#             connection_TCPSocket.send('DONE'.encode('utf-8'))
#             missingbytes = connection_TCPSocket.recv(1024)
#             missing = [int.from_bytes(missingbytes[i:i+2]) for i in range(0,len(missingbytes),2)]
#         break

# server_TCPSocket.close()
# server_UDPSocket.close()





