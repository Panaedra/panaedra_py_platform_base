"""
A small Panaedra Python wrapper for _TERM_UNDISCLOSED_ing with socket connections as a client.
"""

import socket

SOCKET_RECEIVE_BLOCKSIZE = 4096

class c_socketclientraw(object):
  '''
  FREF@bc4c1880d++: A small wrapper for _TERM_UNDISCLOSED_ing with socket connections as a client. Facilitates "PackedMessage" (Prefix each message with a 4-byte length (network byte order, big endian)). Implemented in java (panaedra_javacommon), python (panaedra_python) and python (py-_CLOUD_rollforward). Keep changes to the independent source code locations in sync.
  Note: this 'raw' version does *NOT* support PackedMessage, and is used for (a.o.) tray-server testing. Use the normal 'c_socketclient.py' for normal (PackedMessage) TCP traffic.  
  '''
  
  def __init__(self, cHostIP, iPortIP, bBlockingIP = True):
    '''Initialize the TCP/IP socket'''
    
    self.oSocket         = None
    self.tServerAddress  = (cHostIP, iPortIP)
    self.bIsConnected    = False
    self.iMaxSendAttemps = 2 
    self.bBlocking       = bBlockingIP
    
  def ClientConnectToServer(self):
    '''Establish a connection with a server'''

    self.oSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.oSocket.setblocking(self.bBlocking)
    try:
      self.oSocket.connect(self.tServerAddress)
      self.bIsConnected = True
    except:
      self.bIsConnected = False
      self.Close()
  
  def ClientDisconnectFromServer(self):
    self.Close() 
  
  def Close(self):
    self.oSocket.close()
  
  def Send(self, cMessageIP): 
    self.oSocket.sendall(cMessageIP)
    
  def ReceiveAll(self):
    ''' Helper function to recv n bytes or return None if EOF is hit '''
      
    cData = ''
    while True:
      cPacket = self.oSocket.recv(SOCKET_RECEIVE_BLOCKSIZE)
      cData  += cPacket
      if len(cPacket) < SOCKET_RECEIVE_BLOCKSIZE:
        break
    return cData    
  
#EOF
  