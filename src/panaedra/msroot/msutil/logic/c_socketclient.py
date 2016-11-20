import socket

from panaedra.msroot.msutil.logic.c_socket_packedmessage import c_socket_packedmessage

class c_socketclient(c_socket_packedmessage):
  '''
  FREF@bc4c1880d++: A small wrapper for _TERM_UNDISCLOSED_ing with socket connections as a client. Facilitates "PackedMessage" (Prefix each message with a 4-byte length (network byte order, big endian)). Implemented in java (panaedra_javacommon), python (panaedra_python) and python (py-_CLOUD_rollforward). Keep changes to the independent source code locations in sync. 
  '''
  
  def __init__(self, cHostIP, iPortIP):
    '''Initialize the TCP/IP socket'''
    
    self.oSocket         = None
    self.tServerAddress   = (cHostIP, iPortIP)
    self.bIsConnected    = False
    self.iMaxSendAttemps = 2 
    
  def ClientConnectToServer(self):
    '''Establish a connection with a server'''

    self.oSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.oSocket.setblocking(True)
    try:
      self.oSocket.connect(self.tServerAddress)
      self.bIsConnected = True
    except:
      self.bIsConnected = False
      self.Close()
  
  def Close(self):
    self.oSocket.close()
  
  def ClientSocketClose(self):
    
    if not self.oSocket is None: 
      self.SendStopConnectionRequest()  
      
  def SendStopConnectionRequest(self):
    self.PackedMessageSend('stop_connection')    

  def ClientSocketSendToServer(self, cSendDataIP): # FREF@7b08b89b1 
    
    iTransmissionAttempt = 0  
    cResponseMessage     = ''
    bPartOkay            = False

    while (not bPartOkay) and (iTransmissionAttempt < self.iMaxSendAttemps): 
      try:
        if not self.bIsConnected:  
          self.ClientConnectToServer()
        self.PackedMessageSend(cSendDataIP)
        # Receive response
        cResponseMessage = self.PackedMessageRcv()
        bPartOkay        = cResponseMessage == 'part_okay'
        if not bPartOkay: 
          iTransmissionAttempt += 1
      except socket.error as oError:
        self.bIsConnected = False
        iTransmissionAttempt += 1 
        '''Send or receive data was disallowed because the socket is not connected and no address was supplied, OR
             - An existing connection forcibly closed by the remote host'''
        if (oError.errno == 10057) or (oError.errno == 10054): 
          break
      except:  
        # Unexpected error: try sending the message again
        iTransmissionAttempt += 1
    
    return bPartOkay, cResponseMessage

#EOF
