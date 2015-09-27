""" Bare-bones Parrot Jumping Sumo control.
"""
import json
import socket
import struct


class SumoController(object):
    """ Parrot Jumping Sumo controller.
    """
    def __init__(self, ip='192.168.2.1', init_port=44444):
        self._ip = ip
        self._init_port = init_port
        self._c2d_port = None
        self._connected = False

    def connect(self):
        self._c2d_port = self._get_c2dport()
        self._connected = True

    def _get_c2dport(self, d2c_port=54321):
        """ Return the ports we need to connect to for control.
        """
        init_msg = {
            'controller_name': 'SumoPy',
            'controller_type': 'Python',
            'd2c_port': d2c_port,
        }
        init_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        init_sock.connect((self._ip, self._init_port))
        init_sock.sendall(json.dumps(init_msg))

        # Strip trailing \x00.
        init_resp = init_sock.recv(1024)[:-1]

        return json.loads(init_resp)['c2d_port']


class SumoMarshaller:
    """ From JumpingSumo Client Library

        Copyright(C) 2015, Isao Hara, AIST
        Release under the MIT License.
    """
    def __init__(self, buffer=''):
        self.buffer = buffer
        self.bufsize = len(buffer)

        self.offset = 0

        self.header_size = self.calcsize('BBBHH')
        self.encbuf = None
        self.encpos = 0

    #
    #    for buffer
    #
    def setBuffer(self, buffer):
        if self.buffer:
            del self.buffer
        self.buffer = buffer
        self.bufsize = len(buffer)
        self.offset = 0

    def clearBuffer(self):
        self.setBuffer("")

    def appendBuffer(self, buffer):
        self.buffer += buffer
        self.bufsize = len(self.buffer)

    #
    #    check message format...
    #
    def checkMsgFormat(self, buffer, offset=0):
        bufsize = len(buffer)

        if bufsize - offset >= self.header_size:
            self.buffer = buffer
            self.offset = offset
            (cmd, func, seq, size, fid) = self.unmarshal('bbbHH')

            if cmd in (0x01, 0x02, 0x03, 0x04):
                if size <= bufsize - offset:
                    return size
                else:
                    print "Short Packet %d/%d" % (bufsize, size)
                    return 0

            else:
                print "Error in checkMsgFormat"
                return -1

        return 0

    #
    # extract message from buffer
    #
    def getMessage(self, buffer=None, offset=0):
        if buffer:
            self.buffer = buffer
        res = self.checkMsgFormat(self.buffer, offset)

        if res > 0:
            start = offset
            end = offset + res
            cmd = self.buffer[start:end]
            self.buffer = self.buffer[end:]
            self.offset = 0
            return cmd

        elif res == 0:
            return ''

        else:
            self.skipBuffer()
            return None

    #
    #    skip buffer, but not implemented....
    #
    def skipBuffer(self):
            print "call skipBuffer"
            return
    #
    #    print buffer for debug
    #
    def printPacket(self, data):
        for x in data:
            print "0x%02x" % ord(x),
        print

    #
    #    dencoding data
    #
    def unmarshalString(self, offset=-1):
        if offset < 0: offset=self.offset
        try:
            endpos = self.buffer.index('\x00', offset)
            size = endpos - offset
            if(size > 0):
                (str_res,) = struct.unpack_from('!%ds' % (size), self.buffer, offset)
                self.offset += size + 1
                return str_res
            else:
                return ""
        except:
            print "Error in parseCommand"
            return None

    def unmarshalNum(self, fmt, offset=-1):
        if offset < 0:
            offset = self.offset
        try:
            (res,) = struct.unpack_from(fmt, self.buffer, offset)
            self.offset = offset + struct.calcsize(fmt)
            return res
        except:
            print "Error in unmarshalNum"
            return None

    def unmarshalUShort(self, offset=-1):
        return self.unmarshalNum('<H', offset)

    def unmarshalUInt(self, offset=-1):
        return self.unmarshalNum('<I', offset)

    def unmarshalDouble(self, offset=-1):
        return self.unmarshalNum('d', offset)

    def unmarshalBool(self, offset=-1):
        return self.unmarshalNum('B', offset)

    def unmarshalByte(self, offset=-1):
        return self.unmarshalNum('b', offset)

    def unmarshalChar(self, offset=-1):
        return self.unmarshalNum('c', offset)

    def unmarshal(self, fmt):
        res = []
        for x in fmt:
            if x in ('i', 'h', 'I', 'H'):
                res.append(self.unmarshalNum('<'+x))
            elif x in ('d', 'B', 'c', 'b'):
                res.append(self.unmarshalNum(x))
            elif x == 'S':
                res.append(self.unmarshalString())
        return res

    #    generate command
    #
    def createCommand(self):
        self.encbuf = bytearray()
        self.encpos = 0

    def initCommand(self, cmd):
        self.encbuf = bytearray(cmd)
        self.encpos = len(cmd)

    def appendCommand(self, cmd):
        self.encbuf = self.encbuf + bytearray(cmd)
        self.encpos += len(cmd)

    def setCommandSize(self):
        size = len(self.encbuf)
        struct.pack_into('<H', self.encbuf, 3, size)

    def setSeqId(self, sid):
        sid = sid % 256
        struct.pack_into('B', self.encbuf, 2, sid)

    def getEncodedCommand(self):
        self.setCommandSize()
        return str(self.encbuf)

    def getEncodedDataCommand(self):
        return str(self.encbuf)

    def clearEncodedCommand(self):
        if self.encbuf:
            del self.encbuf
        self.encbuf = None
        return
    #
    #    encoding data
    #
    def marshalNumericData(self, fmt, s):
        enc_code = bytearray(struct.calcsize(fmt))
        struct.pack_into(fmt, enc_code, 0, s)
        self.encbuf = self.encbuf+enc_code
        self.encpos += struct.calcsize(fmt)

    def marshalChar(self, s):
        if type(s) == int:
            self.marshalNumericData('c', chr(s))
        else:
            self.marshalNumericData('c', s)

    def marshalUShort(self, s):
        self.marshalNumericData('>H', s)

    def marshalUInt(self, s):
        self.marshalNumericData('>I', s)

    def marshalDouble(self, d):
        self.marshalNumericData('>d', d)

    def marshalBool(self, d):
        if d:
            self.marshalNumericData('B', 1)
        else:
            self.marshalNumericData('B', 0)

    def marshalByte(self, d):
            self.marshalNumericData('b', d)

    def marshalString(self, str):
        size = len(str)
        enc_size = size + 1
        enc_code = bytearray(size)

        if size > 0:
            struct.pack_into('%ds' % (size,), enc_code, 0, str)

        self.encbuf = self.encbuf+enc_code+'\x00'
        self.encpos += enc_size

    def marshal(self, fmt, *data):
        pos = 0
        for x in fmt:
            if x in ('i', 'h', 'I', 'H', 'd'):
                self.marshalNumericData('<'+x, data[pos])
            elif x == 'b':
                self.marshalByte(data[pos])
            elif x == 'B':
                self.marshalBool(data[pos])
            elif x == 'c':
                self.marshalChar(data[pos])
            elif x == 'S':
                self.marshalString(data[pos])
            elif x == 's':
                self.marshalString(data[pos], 0)
            pos += 1
        return

    def calcsize(self, fmt):
        res = 0
        for x in fmt:
            if x in ('i', 'h', 'I', 'H', 'd', 'B'):
                res += struct.calcsize(x)
            else:
                print "Unsupported format:", x
        return res




if __name__ == '__main__':
    controller = SumoController()
    controller.connect()

    c2d_port = controller._c2d_port

    print c2d_port





    move_seq = 0
    speed = 50
    turn = 0
    cmd = '\x02\x0a\x00\x0e\x00\x00\x00\x03\x00\x00\x00'
    marshaller = SumoMarshaller()
    marshaller.initCommand(cmd)
    if speed == 0 and turn == 0:
        marshaller.marshal('bbb', 0, 0, 0)
    else:
        marshaller.marshal('bbb', 1, speed, turn)
    marshaller.setSeqId(move_seq)
    move_seq = (move_seq + 1) % 256
    data = marshaller.getEncodedCommand()

    print repr(data)

    c2d_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c2d_sock.connect(('192.168.2.1', 54321))
    c2d_sock.sendall(data)
