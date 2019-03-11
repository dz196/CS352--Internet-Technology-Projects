#Project by Group 25 David Zhang, Nikul Patel
import binascii
import socket as syssock
import struct
import sys
import numpy as np
import struct
import threading
import time
import random
# these functions are global to the class and

sendaddr = None
rcvaddr = None

sendno = 25
rcvno = 10
PACKET_LIST = []
MAX_PACKET_SIZE = 63*1024
sock = None
sock2 = None
size_of_file = 0

SOCK352_SYN = 1
SOCK352_FIN = 2
SOCK352_ACK = 4
SOCK352_RESET = 8
SOCK352_HAS_OPT = 16
header_format = '!BBHQQL'

thread_lock = threading.Lock()
thread_state = False

# define the UDP ports all messages are sent and received from
def init(UDPportTx,UDPportRx):   # initialize your UDP socket here 
    global sendaddr
    global rcvaddr
    sendaddr = ('',int(UDPportTx))
    rcvaddr = ('localhost', int(UDPportRx))
    pass 

#This method checks that the packets are being sent in the right order using sequence numbers.
#If the in order packet isn't found, the packet isn't removed from the list
def lookForPacketNorm(target_packet):
    global PACKET_LIST
    #print('SIZE OF QUEUE BEFORE LOOKING: ' + str(PACKET_LIST))
    if len(PACKET_LIST) < 0:
        print('PACKET LIST EMPTY ERROR')
        return
    packet = PACKET_LIST[0]
    #print('Sent SequenceNo: ' + str(packet.sequence_no))
    #print('Received SequenceNo: ' + str(target_packet.sequence_no))
    if (packet.sequence_no == target_packet.sequence_no):
        PACKET_LIST.remove(packet)
        #print('PACKET REMOVED')
    #print('SIZE OF QUEUE AFTER LOOKING: ' + str(PACKET_LIST))

def checkACK(delay):
    global PACKET_LIST
    global thread_lock
    global sock

    #Stall until packets are being sent
    while thread_state == False:
        time.sleep(delay)
    
    #Receive all ACKS
    while PACKET_LIST:
        bytes, address = sock.recvfrom(MAX_PACKET_SIZE)
        #Create blank packet
        rcvpacket = Packet()
        #Flood packet with received info
        thread_lock.acquire()
        Packet.unpack(rcvpacket, bytes)
        
        lookForPacketNorm(rcvpacket)
        thread_lock.release()
    #print(PACKET_LIST)
    #print('ACKS ALL ACKNOWLEDGED')

def checkForTimeouts(delay):
    global PACKET_LIST
    global thread_lock
    global sock
    #Stall until packets are being sent
    while thread_state == False:
        time.sleep(delay)
    
    while PACKET_LIST:
        thread_lock.acquire()
        if PACKET_LIST:
            timeout = float(time.time()) - float(PACKET_LIST[0].timesent)
            if timeout > delay:
                sentpacket=Packet()
                sentpacket=PACKET_LIST[0]
                sentpacket.timesent = time.time()
                sock.sendto(sentpacket.pack(), rcvaddr)
                PACKET_LIST.pop(0)
                PACKET_LIST.insert(0, Packet(sentpacket.version, sentpacket.flags,sentpacket.header_len, sentpacket.sequence_no, sentpacket.ack_no, sentpacket.payload_len, sentpacket.data, sentpacket.timesent ))
                #print('RETRANSMITTED: ')
                #print(PACKET_LIST[0].sequence_no)
                #for packet in PACKET_LIST:
                    #print('IN LIST:' + str(packet.sequence_no))
        thread_lock.release()
    
class RCVThread(threading.Thread):

    def __init__(self, threadID, name, delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = float(delay)
        
    def run(self):
        checkACK(self.delay)
class TimeoutThread(threading.Thread):

    def __init__(self, threadID, name, delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = float(delay)
        
    def run(self):
        checkForTimeouts(self.delay)
        return 

class Packet:
    
    def __init__(self, version = 0, flags = 0, header_len = 0, sequence_no = 0, ack_no = 0, payload_len = 0, data = b'', timesent = 0):
        self.version = version
        self.flags = flags
        self.header_len = header_len
        self.sequence_no = sequence_no
        self.ack_no = ack_no
        self.payload_len = payload_len
        self.data = data
        self.timesent = timesent

    def pack(self):
        global header_format
        if self.data == None:
            datalen = 0
            bindata = struct.pack(header_format, self.version, self.flags,self.header_len, self.sequence_no, self.ack_no, self.payload_len)
        else:
            datalen = len(self.data)
            new_header_format = header_format + str(datalen) + 's'
            bindata = struct.pack(new_header_format, self.version, self.flags, self.header_len, self.sequence_no, self.ack_no, self.payload_len, self.data)
        return bindata

    def unpack(self, bindata):
        global header_format
        datalen = (len(bindata) - struct.calcsize(header_format))
        if datalen >= 0:
            new_header_format = header_format + str(datalen) + 's'
            packet_fields = struct.unpack(new_header_format, bindata)
            self.version = packet_fields[0]
            self.flags = packet_fields[1]
            self.header_len = packet_fields[2]
            self.sequence_no = packet_fields[3]
            self.ack_no = packet_fields[4]
            self.payload_len = packet_fields[5]
            self.data = packet_fields[6]
class socket:

    def __init__(self):  # fill in your code here 
        global sock
        global sock2
        sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        sock2 = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        self.sentpacket = Packet()
        self.rcvpacket = Packet()
        return
    #Specific function to check if the correct packets are being exchanged in Three way Handshake
    #Using the sequence & ack numbers
    def lookForPacketHandshake(self, target_packet):
        global PACKET_LIST
        #print('SIZE OF QUEUE BEFORE LOOKING: ' + str(PACKET_LIST))
        if len(PACKET_LIST) < 0:
            print('PACKET LIST EMPTY ERROR')
            return
        packet = PACKET_LIST[0]
        #print('Sent SequenceNo: ' + str(packet.sequence_no))
        #print('Received ACKNo: ' + str(target_packet.ack_no))
        if (packet.sequence_no == target_packet.ack_no-1):
            PACKET_LIST.remove(packet)
            #print('PACKET REMOVED')
        #print('SIZE OF QUEUE AFTER LOOKING: ' + str(PACKET_LIST))
        return

    def bind(self,address):
        #Bind socket sock to the given address
        global sendaddr
        global sock
        sock.bind(sendaddr)
        #print("Bind: " + str(sendaddr))
        return 

    def connect(self,address):  # fill in your code here 
        global PACKET_LIST
        global sendaddr
        global rcvaddr
        global sock
        global sock2
        global sendno
        global rcvno

        #Bind client side receiving port - SOCK
        sock.bind(sendaddr)
        #print('Bind: ' + str(sendaddr))
        #Make UDP Connection and bind receiving socket
        #print(str(rcvaddr))
        sock2.connect(rcvaddr)
        #print('Connect: ' + str(rcvaddr))

        #Client side handshake: initial client_isn sequence number and flag bit set as 1

        #Create connection packet and initialize variables
        self.sentpacket.version = SOCK352_SYN
        self.sentpacket.sequence_no = sendno

        #Send SYN packet
        sock.sendto(self.sentpacket.pack(), rcvaddr)
        #print('SYN PACKET SENT: ' + str(self.sentpacket.sequence_no))
        PACKET_LIST.append(Packet(self.sentpacket.version, self.sentpacket.flags, self.sentpacket.header_len, self.sentpacket.sequence_no, self.sentpacket.ack_no, self.sentpacket.payload_len, self.sentpacket.data))
        #print("List after sending SYN packet: ")
        #print(PACKET_LIST)
        
        #Wait for ACK packet from server
        bytes, address = sock.recvfrom(MAX_PACKET_SIZE)
        #print('CLIENT RECEIVED ACK PACKET')
        Packet.unpack(self.rcvpacket, bytes)
        rcvno = self.rcvpacket.sequence_no + 1
        
        self.lookForPacketHandshake(self.rcvpacket)
        
        #Send ACK of the SYNRCV packet to server
        self.sentpacket = Packet(version = 1, flags = SOCK352_ACK, header_len = struct.calcsize(header_format), sequence_no = sendno, ack_no = rcvno)

        sock.sendto(self.sentpacket.pack(), rcvaddr)

        #print('Client Side Handshake Complete')
        return 
    
    def listen(self,backlog):
        #Don't have to do anything
        return

    def accept(self):
        global PACKET_LIST
        global sendaddr
        global rcvaddr
        global sock
        global sock2
        global sendno
        global rcvno

        #print('Accepting SYN packet')
        #(clientsocket, address) =  # change this to your code

        #Client side sock2 sends to serverside sock which is bound
        
        #Receive the SYN packet
        bytes, sendaddr = sock.recvfrom(MAX_PACKET_SIZE)

        #Unpack SYN packet
        Packet.unpack(self.rcvpacket, bytes)

        #Form SYNRCV packet
        self.sentpacket = Packet(version = 1, flags = SOCK352_ACK, header_len = struct.calcsize(header_format), sequence_no = rcvno, ack_no = self.rcvpacket.sequence_no + 1)
        """self.sentpacket.version = 1
        self.sentpacket.flags = SOCK352_ACK
        self.sentpacket.header_len=struct.calcsize(header_format)
        self.sentpacket.sequence_no = rcvno
        self.sentpacket.ack_no = self.rcvpacket.sequence_no + 1
        self.sentpacket.payload_len = 0
        self.sentpacket.data= b''"""

        #print('SENDADDRESS + ' + str(sendaddr))
        #Send packet
        sock2.sendto(self.sentpacket.pack(), sendaddr)
        #print('SERVER ACK SENT TO CLIENT')
        #Append packet to global array
        PACKET_LIST.append(Packet(self.sentpacket.version, self.sentpacket.flags, self.sentpacket.header_len, self.sentpacket.sequence_no, self.sentpacket.ack_no, self.sentpacket.payload_len, self.sentpacket.data))

        #Receive final ACK from client
        bytes, address = sock.recvfrom(MAX_PACKET_SIZE)
        Packet.unpack(self.rcvpacket, bytes)

        self.lookForPacketHandshake(self.rcvpacket)

        #print('Server Side Handshake Complete')
        return (self,sendaddr)
     
    def close(self):   # fill in your code here 
        global sock
        global sock2
        global thread_lock
        global PACKET_LIST
        #print('REACHED CLOSE')
        while True:
            thread_lock.acquire()
            if len(PACKET_LIST) == 0:
                sock.close()
                sock2.close()
                break
            thread_lock.release()
        return 

    def send(self,buffer):
        global PACKET_LIST
        global size_of_file
        global sock
        global sock2
        global thread_state
        bytessent = 0
        if len(buffer) == 4:
            sock.sendto(buffer, rcvaddr)
            head_format = struct.Struct('!L')    #Long is 32 bits = 4 bytes
            tups = head_format.unpack(buffer)
            size_of_file = tups[0]
            #print('SIZE OF FILE: ' + str(size_of_file))
            bytessent = 4
        else:
            startindices = range(0, size_of_file, MAX_PACKET_SIZE - struct.calcsize(header_format))
            while startindices:
                startbyte = startindices[0]
                self.sentpacket.verison = 1
                self.sentpacket.flags = 0
                self.sentpacket.header_len = struct.calcsize(header_format)
                self.sentpacket.sequence_no = startindices[0]
                self.sentpacket.ack_no = 0
                self.sentpacket.payload_len = 0
                if startbyte != startindices[len(startindices) - 1]:
                    self.sentpacket.data = buffer[startbyte:startbyte + MAX_PACKET_SIZE-struct.calcsize(header_format)]
                else:
                    self.sentpacket.data = buffer[startbyte:]
                
                if startbyte != 0:
                    sock.sendto(self.sentpacket.pack(), rcvaddr)
                
                drop_chance = random.random()
                prob = .5
                if drop_chance < prob:
                #if startbyte != 64488:
                    sock.sendto(self.sentpacket.pack(), rcvaddr)
                #sock.sendto(self.sentpacket.pack(), rcvaddr)
                startindices.pop(0)

                thread_lock.acquire()
                PACKET_LIST.append(Packet(version = self.sentpacket.version, flags = self.sentpacket.flags, header_len = self.sentpacket.header_len, sequence_no = self.sentpacket.sequence_no, ack_no = self.sentpacket.ack_no, payload_len = self.sentpacket.payload_len, data = self.sentpacket.data, timesent = time.time()))
                #print('APPENDED : ' + str(self.sentpacket.sequence_no))
                thread_lock.release()

                #Begin checking for delays after first packet is sent & appended
                thread_state = 1
            bytessent = len(buffer)

        #print('AFTER SENDING: ')
        #print(len(PACKET_LIST))
        #print(PACKET_LIST)
        """
        #Receive all ACKS
        while PACKET_LIST:
            bytes, address = sock.recvfrom(MAX_PACKET_SIZE)
            Packet.unpack(self.rcvpacket, bytes)
            
            lookForPacketNorm(self.rcvpacket)"""
        return bytessent 

    def recv(self,nbytes):
        global PACKET_LIST
        global size_of_file
        global sock2

        bytesreceived = 0
        if nbytes == 4:
            bytes, address = sock.recvfrom(MAX_PACKET_SIZE)
            head_format = struct.Struct('!L')  
            tups = head_format.unpack(bytes)
            size_of_file = tups[0]
            #print('SIZE OF FILE: ' + str(size_of_file))
            bytesreceived = bytes
        else:
            startindices = range(0, size_of_file, MAX_PACKET_SIZE - struct.calcsize(header_format))
            bytesreceived = ''
            #print('BEFORE LOOP')
            while startindices:
                startbyte = startindices[0]
                #print('STARTBYTE: '  + str(startbyte))
                bytes, address = sock.recvfrom(MAX_PACKET_SIZE)
                Packet.unpack(self.rcvpacket, bytes)

                if int(self.rcvpacket.sequence_no) == int(startbyte):
                    bytesreceived += self.rcvpacket.data

                    self.sentpacket.verison = 1
                    self.sentpacket.flags = SOCK352_ACK
                    self.sentpacket.header_len = struct.calcsize(header_format)
                    self.sentpacket.sequence_no = self.rcvpacket.sequence_no
                    self.sentpacket.ack_no = startbyte + (MAX_PACKET_SIZE - struct.calcsize(header_format))
                    self.sentpacket.payload_len = 0
                    self.sentpacket.data = b''

                    sock2.sendto(self.sentpacket.pack(), sendaddr)
                    #print('ACK of Sequence No: ' + str(startbyte))

                    startindices.pop(0)
                #print('END OF LOOP')
        #print('AFTER RECEIVING: ')
        #print(len(PACKET_LIST))
        #print(PACKET_LIST)
        return bytesreceived 

thr1 = RCVThread(1, 'Thread1', 0.2)
thr2 = TimeoutThread(2, 'Thread2', 0.2)

thr1.daemon = True
thr2.daemon = True

thr1.start()
thr2.start()
