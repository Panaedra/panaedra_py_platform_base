import struct

class c_socket_packedmessage(object):
  '''
  FREF@bc4c1880d: A small wrapper for _TERM_UNDISCLOSED_ing with socket connections as a client. Facilitates "PackedMessage" (Prefix each message with a 4-byte length (network byte order, big endian)). Implemented in java (panaedra_javacommon), python (panaedra_python) and python (py-_CLOUD_rollforward). Keep changes to the independent source code locations in sync. 
  '''

  def PackedMessageSend(self, cMessageIP):
    ''' Prefix each message with a 4-byte length (network byte order, big endian) '''
    
    cMessage = struct.pack('>I', len(cMessageIP)) + cMessageIP
    self.oSocket.sendall(cMessage)

  def PackedMessageRcv(self):
    ''' Read message length and unpack it into an integer '''
    
    cRawMessageLength = self._ReceiveAll(4)
    if not cRawMessageLength:
        return None
    iMessageLength = struct.unpack('>I', cRawMessageLength)[0]
    # Read the message data
    return self._ReceiveAll(iMessageLength)

  def _ReceiveAll(self, iBytesIP):
    ''' Helper function to recv n bytes or return None if EOF is hit '''
      
    cData = ''
    while len(cData) < iBytesIP:
      cPacket = self.oSocket.recv(iBytesIP - len(cData))
      if not cPacket:
        return None
      cData += cPacket
    return cData

#EOF
