import re
import md5
import base64
import httplib
import socket

class Camera(object):
    R320_240 = 8
    R640_480 = 32
    ptz_type = 0    
    PTZ_STOP = 1
    TILT_UP = 0
    TILT_UP_STOP = 1
    TILT_DOWN = 2
    TILT_DOWN_STOP = 3
    PAN_LEFT = 6
    PAN_LEFT_STOP = 5
    PAN_RIGHT = 4
    PAN_RIGHT_STOP = 7
    PTZ_LEFT_UP = 91
    PTZ_RIGHT_UP = 90
    PTZ_LEFT_DOWN = 93
    PTZ_RIGHT_DOWN = 92
    PTZ_CENTER = 25
    PTZ_VPATROL = 26
    PTZ_VPATROL_STOP = 27
    PTZ_HPATROL = 28
    PTZ_HPATROL_STOP = 29
    PTZ_PELCO_D_HPATROL = 20
    PTZ_PELCO_D_HPATROL_STOP = 21
    IO_ON = 95
    IO_OFF = 94
    timeout = 5
    
    def __init__(self, username, password, host):
        self.username = username
        self.password = password
        self.host = host
        self.path = '/decoder_control.cgi?command='
        self.stop_cmd = -1

    def exec_command(self, dpad):
        cmd = -1
        if dpad[0] == 0 and dpad[1] == 0:
            # Stop all movement
            cmd = self.stop_cmd
        elif dpad[0] == 1 and dpad[1] == 0:
            cmd = self.PAN_RIGHT
            self.stop_cmd = self.PAN_RIGHT_STOP
        elif dpad[0] == -1 and dpad[1] == 0:
            cmd = self.PAN_LEFT
            self.stop_cmd = self.PAN_LEFT_STOP
        elif dpad[0] == 0 and dpad[1] == -1:
            cmd = self.TILT_UP
            self.stop_cmd = self.TILT_UP_STOP
        elif dpad[0] == 0 and dpad[1] == 1:
            cmd = self.TILT_DOWN
            self.stop_cmd = self.TILT_DOWN_STOP
        if cmd > -1:
            self._send(cmd)
            
    def _setup_auth(self, path):
        realm = None
        conn = httplib.HTTPConnection(self.host, 80, timeout=self.timeout)
        try:
            conn.request('GET', self.path)
            httpresp = conn.getresponse()
            if httpresp.status != 401:
                return
            wwwauth = httpresp.getheader('WWW-Authenticate')
            realm, snonce = [x.split('=')[1].replace('"', '') for x in re.split(',| ', wwwauth) if 'realm' in x or 'nonce' in x]
        except socket.error as e:
            print(e)
        ha1 = md5.md5('%s:%s:%s' % (self.username, realm, self.password)).hexdigest()
        ha2 = md5.md5('GET:%s' % path).hexdigest()
        cnonce = '01234567'
        nc = '00000001'
        response = md5.md5('%s:%s:%s:%s:%s:%s' % (ha1, snonce, nc, cnonce, 'auth', ha2)).hexdigest()
        auth = 'Digest username="%s", realm="%s", nonce="%s", uri="%s", response="%s", qop=auth, nc=%s, cnonce="%s", algorithm="MD5"'
        auth = auth % (self.username, realm, snonce, path, response, nc, cnonce)
#         print ha1
#         print ha2
#         print auth
        return {'Authorization' : auth}
    
    def _send(self, cmd):
        send_path = self.path + str(cmd)
        headers = self._setup_auth(send_path)
        if not headers:
            return
        try:
            conn = httplib.HTTPConnection(self.host, 80, timeout=self.timeout)
            conn.request('GET', send_path, headers=headers)
            resp = conn.getresponse().read()
        except socket.error as e:
            print(e)