import socket
import sys
import asyncore
import logging

class BackendList:
    def __init__(self):
        self.servers = [
            ('127.0.0.1', 8000),
            ('127.0.0.1', 8001),
            ('127.0.0.1', 8002),
            ('127.0.0.1', 8003),
            ('127.0.0.1', 8004)
        ]
        self.current = 0

    def getserver(self):
        s = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return s

class Backend(asyncore.dispatcher_with_send):
    def __init__(self, targetaddress):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(targetaddress)
        self.client_socket = None

    def handle_read(self):
        try:
            if self.client_socket:
                self.client_socket.send(self.recv(8192))
        except:
            pass

    def handle_close(self):
        try:
            self.close()
            if self.client_socket:
                self.client_socket.close()
        except:
            pass

class ProcessTheClient(asyncore.dispatcher_with_send):
    def __init__(self, sock, backend):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.backend = backend
        self.backend.client_socket = self

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.backend.send(data)

    def handle_close(self):
        self.close()

class Server(asyncore.dispatcher):
    def __init__(self, portnumber):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', portnumber))
        self.listen(5)
        self.bservers = BackendList()

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            backend_address = self.bservers.getserver()
            backend = Backend(backend_address)
            handler = ProcessTheClient(sock, backend)

def main():
    portnumber = 55555
    try:
        portnumber = int(sys.argv[1])
    except:
        pass
    svr = Server(portnumber)
    asyncore.loop()

if __name__ == "__main__":
    main()
