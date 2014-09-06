#!/usr/bin/env python

import BaseHTTPServer
import logging
import socket
from SocketServer import ThreadingMixIn
from threading import Thread

log = logging.getLogger()

class KeyRequestHandlerBase(BaseHTTPServer.BaseHTTPRequestHandler):
    '''This is the "base class" which needs to be given access
    to the key to be served. So you will not use this class,
    but create a use one inheriting from this class. The subclass
    must also define a keydata field.
    '''
    server_version = 'Geysign/' + 'FIXME-Version'
    
    ctype = 'application/openpgpkey' # FIXME: What the mimetype of an OpenPGP key?

    def do_GET(self):
        f = self.send_head(self.keydata)
        self.wfile.write(self.keydata)
    
    def send_head(self, keydata=None):
        kd = keydata if keydata else self.keydata
        self.send_response(200)
        self.send_header('Content-Type', self.ctype)
        self.send_header('Content-Length', len(kd))
        self.end_headers()
        return kd

class ThreadedKeyserver(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    '''The keyserver in a threaded fashion'''
    address_family = socket.AF_INET6
    
    def __init__(self, server_address, *args, **kwargs):
        if issubclass(self.__class__, object):
            super(ThreadedKeyserver, self).__init__(*args, **kwargs)
        else:
            BaseHTTPServer.HTTPServer.__init__(self, server_address, *args, **kwargs)
            # WTF? There is no __init__..?
            # ThreadingMixIn.__init__(self, server_address, *args, **kwargs)

        def server_bind(self):
            # Override this method to be sure v6only is false: we want to
            # listen to both IPv4 and IPv6!
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)
            BaseHTTPServer.HTTPServer.server_bind(self)



class ServeKeyThread(Thread):
    '''Serves requests and manages the server in separates threads.
    You can create an object and call start() to let it run.
    If you want to stop serving, call shutdown().
    '''
    
    def __init__(self, data, port=9001, *args, **kwargs):
        '''Initializes the server to serve the data'''
        self.keydata = data
        self.port = port
        super(ServeKeyThread, self).__init__(*args, **kwargs)
        self.daemon = True
        self.httpd = None

        
    def serve_key(self, data=None, port=None, **kwargs):
        '''Starts serving the data either from the argument
        or from the field of the object.
        An HTTPd is started and being put to serve_forever.
        You need to call shutdown() in order to stop
        serving.
        '''
        
        port = port or self.port or 9001
        
        tries = 10
    
        kd = data if data else self.keydata
        class KeyRequestHandler(KeyRequestHandlerBase):
            '''You will need to create this during runtime'''
            keydata = kd
        HandlerClass = KeyRequestHandler
        
        for port_i in (port + p for p in range(tries)):
            try:
                log.info('Trying port %d', port_i)
                server_address = ('', port_i)
                self.httpd = ThreadedKeyserver(server_address, HandlerClass, **kwargs)
                sa = self.httpd.socket.getsockname()
                try:
                    log.info('Serving now, this is probably blocking...')
                    self.httpd.serve_forever()
                finally:
                    log.info('finished serving')
                    #httpd.dispose()
                    break
    
            except socket.error, value:
                errno = value.errno
                if errno == 10054 or errno == 32:
                    # This seems to be harmless
                    break
            finally:
                pass
    

    def run(self):
        '''This is being run by Thread in a separate thread
        after you call start()'''
        self.serve_key(self.keydata)

    def shutdown(self):
        '''Sends shutdown to the underlying httpd'''
        log.info("Shutting down httpd %r", self.httpd)
        self.httpd.shutdown()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    KEYDATA = 'Example data'
    serve_key(KEYDATA)
    log.warn('Last line')
