
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
server_isn = 10
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
    def unpack(self, bytes):
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
        self.sock2 = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        self.sentpacket = Packet()
        self.rcvpacket = Packet()
        return
    
    def lookForPacket(self, target_packet):
        global PACKET_LIST
        print('SIZE OF QUEUE BEFORE LOOKING: ' + str(PACKET_LIST))
        for packet in PACKET_LIST:
            if (packet.sequence_no == target_packet.ack_no):
                PACKET_LIST.remove(packet)
                break
        print('SIZE OF QUEUE AFTER LOOKING: ' + str(PACKET_LIST))
        return

    def bind(self,address):
        #Bind socket sock to the given address
        self.sock.bind(address)
        print("Bind: " + str(address))
        return 

    def connect(self,address):  # fill in your code here 
        global client_isn
        global PACKET_LIST
        global destination
        global MAX_PACKET_SIZE

        destination = address

        #Bind client side receiving port - SOCK
        self.sock.bind(address)
        #Make UDP Connection and bind receiving socket
        
        self.sock2.connect(address)
        print('Connect: ' + str(address))

        #Client side handshake: initial client_isn sequence number and flag bit set as 1

        #Create connection packet and initialize variables
        self.sentpacket.version = self.sentpacket.SOCK352_SYN
        self.sentpacket.sequence_no = client_isn
        client_isn += 1
        #Pack the function
        packed_data = self.sentpacket.pack()

        #Send SYN packet
        self.sock2.sendto(packed_data, address)
        PACKET_LIST.append(Packet(self.sentpacket.version, self.sentpacket.flags, self.sentpacket.header_len, self.sentpacket.sequence_no, self.sentpacket.ack_no, self.sentpacket.payload_len, self.sentpacket.data))
        print("List after sending SYN packet: ")
        print(PACKET_LIST)
        
        #Wait for ACK packet from server
        bytes, destination = self.sock.recv(MAX_PACKET_SIZE)
        Packet.unpack(self.rcvpacket, bytes)

        self.lookForPacket(self.rcvpacket)
        
        #Send ACK of the SYNRCV packet
        self.sentpacket.ack_no = self.rcvpacket.sequence_no + 1 #server_isn + 1
        self.flags = 0
        bytes_sent = self.sock2.send(self.sentpacket.pack(), destination)


        return 
    
    def listen(self,backlog):
        #Don't have to do anything
        return

    def accept(self):
        global destination
        global MAX_PACKET_SIZE
        global server_isn
        global PACKET_LIST
        print('Accepting SYN packet')
        #(clientsocket, address) =  # change this to your code

        #Client side sock2 sends to serverside sock which is bound
        
        #Receive the SYN packet
        clientsocket, destination = self.sock.recv(MAX_PACKET_SIZE)

        #Unpack SYN packet
        Packet.unpack(self.rcvpacket, clientsocket)

        #Form SYNRCV packet
        self.sentpacket.flags = self.sentpacket.SOCK352_SYN
        self.sentpacket.ack_no = self.rcvpacket.sequence_no #clien_isn + 1
        self.sentpacket.sequence_no = server_isn
        server_isn += 1

        bytes_sent = self.sock2.send(self.sentpacket.pack(), destination)
        #Append packet to global array
        PACKET_LIST.append(Packet(self.sentpacket.version, self.sentpacket.flags, self.sentpacket.header_len, self.sentpacket.sequence_no, self.sentpacket.ack_no, self.sentpacket.payload_len, self.sentpacket.data))

        #Wait for an ACK from client 
        clientsocket, destination = self.sock.recv(MAX_PACKET_SIZE)

        Packet.unpack(self.rcvpacket, bytes)

        self.lookForPacket(self.rcvpacket)


        return (self.sock,address)
     
    def close(self):   # fill in your code here 
        self.sock.close()
        self.sock2.close()
        return 

    def send(self,buffer):
        global PACKET_LIST

        bytessent = 0     # fill in your code here 
        return bytessent 

    def recv(self,nbytes):
        global MAX_PACKET_SIZE
        global PACKET_LIST
        global destination

        bytesreceived = 0     # fill in your code here

        return bytesreceived 


    


