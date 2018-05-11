import socket
import sys

class Cliente:

    def __init__(self, host='localhost', port=5000, bufsiz=1024):

        self.bufsiz = bufsiz
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def exec_(self, filename):

        self.sock.sendto(filename.encode(), self.address)

        data, _= self.sock.recvfrom(self.bufsiz)

        while data:

            sys.stdout.buffer.write(data)
            data, _ = self.sock.recvfrom(self.bufsiz)


if __name__ == '__main__':

    c = Cliente()
    c.exec_(sys.argv[1])
