import socket
import time

class Servidor:

    def __init__(self, port=5000, bufsiz=1024):

        self.bufsiz = bufsiz

        self.address = ('', port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.bind(self.address)

    def exec_(self):

        data, sender = self.sock.recvfrom(self.bufsiz)

        with open(data, 'r') as f:

            data = f.buffer.read(self.bufsiz)

            while data:

                time.sleep(0.005)

                self.sock.sendto(data, sender)
                data = f.buffer.read(self.bufsiz)

            self.sock.sendto(data, sender)
            # print('I last send a', data, 'to', sender)


if __name__ == '__main__':

    s = Servidor()
    s.exec_()
