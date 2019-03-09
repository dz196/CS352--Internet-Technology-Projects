
import binascii
import socket as syssock
import struct
import sys
import numpy as np
import struct
# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from

sender_port = 0
receiver_port = 0
destination = 0
client_isn = 25

PACKET_LIST = []
MAX_PACKET_SIZE = 64*1024
class Packet:
    
    def __init__(self, version = 0, flags = 0, header_len = 0, sequence_no = 0, ack_no = 0, payload_len = 0, data = 0):
        self.version = version
        self.flags = flags
        self.header_len = header_len
        self.sequence_no = sequence_no
        self.ack_no = ack_no
        self.payload_len = payload_len
        self.data = data
        self.SOCK352_SYN = 1
        self.SOCK352_FIN = 2
        self.SOCK352_ACK = 4
        self.SOCK352_RESET = 8
        self.SOCK352_HAS_OPT = 16
        self.packet_format = '!BBHQQLQ'


    def pack(self):
        bindata = struct.pack(self.packet_format, self.version, self.flags, self.header_len, self.sequence_no, self.ack_no, self.payload_len, self.data)
        return bindata
    def unpack(self, bytes ):
        packet_fields = struct.unpack(self.packet_format, bytes)
        self.version = packet_fields[0]
        self.flags = packet_fields[1]
        self.header_len = packet_fields[2]
        self.sequence_no = packet_fields[3]
        self.ack_no = packet_fields[4]
        self.payload_len = packet_fields[5]
        self.data = packet_fields[6]

def init(UDPportTx,UDPportRx):   # initialize your UDP socket here 
    global sender_port
    global receiver_port
    sender_port = UDPportTx
    receiver_port = UDPportRx
    pass 
    
class socket:

    def __init__(self):  # fill in your code here 

        self.sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        #self.sock2 = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        self.packet = Packet()
        return
    
    def bind(self,address):
        #Bind socket sock to the given address
        self.sock.bind(address)
        print('Bind: ' + str(address[1]))
        return 

    def connect(self,address):  # fill in your code here 
        global client_isn
        global PACKET_LIST
        global destination 
        destination = address
        #Make UDP Connection and bind receiving socket
        #self.sock.bind(1112)
        self.sock.connect(address)
        print('Connect: ' + str(address))
        #Create connection packet and initialize variables
        #self.packet.version = self.packet.SOCK352_SYN
        #self.packet.sequence_no = client_isn
        #Pack the function
        #packed_data = self.packet.pack()

        #Send packet
        #self.sock2.sendto(packed_data, address)
        #PACKET_LIST.append(Packet(self.packet.version, self.packet.flags, self.packet.header_len, self.packet.sequence_no, self.packet.ack_no, self.packet.payload_len, self.packet.data))


        #print(PACKET_LIST)

        return 
    
    def listen(self,backlog):
        #Don't have to do anything
        return

    def accept(self):
        global destination
        (clientsocket, address) = (self,destination) # change this to your code
        print('Accept: ' + str(self))
        return (clientsocket,address)
     
    def close(self):   # fill in your code here 
        self.sock.close()
        #self.sock2.close()
        return 

    def send(self,buffer):
        global PACKET_LIST
        global client_isn
        global destination
        print('sending...')
        self.packet.version = self.packet.SOCK352_SYN
        self.packet.sequence_no = client_isn
        packed_data = self.packet.pack()
        bytessent = 10     # fill in your code here
        #buff = self.packet.pack(buffer)
        #PACKET_LIST.append(buff)
        self.sock.send(packed_data)
        PACKET_LIST.append(Packet(self.packet.version, self.packet.flags, self.packet.header_len, self.packet.sequence_no, self.packet.ack_no, self.packet.payload_len, self.packet.data))
        return bytessent 

    def recv(self,nbytes):
        global MAX_PACKET_SIZE

        bytesreceived = self.sock.recv(nbytes)
        print('bytes received at server: ' + bytesreceived)
        return bytesreceived 


    


