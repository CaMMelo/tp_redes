import socket
import pickle
import sys
import globals

class Client:

    def __init__(self, host='127.0.0.1', port=globals.PORT):

        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect(self.addr)

    def request_file(self, filename):

        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('192.168.43.12', 0)) # abre em uma porta aleatoria

        data = (globals.FILE_REQUEST, udp_sock.getsockname(), filename)

        self.sock.send(pickle.dumps(data))

        # começa a receber o vídeo

        video_pack = []
        ack_n = -1
        last_ack = 0
        pos = 0

        rec = 600

        while True:

            n = 0

            while n < rec:

                pacote, server_addr = udp_sock.recvfrom( 2048 )
                pacote = pickle.loads(pacote)

                n += 1

                if pacote not in video_pack:
                    video_pack.append(pacote)

            video_pack.sort(key=lambda x: x[0])

            for x in video_pack[last_ack:]:

                if ack_n + 1 != x[0]:
                    break

                last_ack = ack_n
                ack_n += 1

            for x in video_pack[pos:]:
                sys.stdout.buffer.write(x[1])
            pos = len(video_pack)

            udp_sock.sendto(pickle.dumps((ack_n,)), server_addr)

        udp_sock.close()

    # tcp
    def request_available_files(self):
        pass

    # comandos de controle de fluxo
    def pause_transmistion(self):
        pass

    def continue_transmission(self):
        pass

    def stop_transmission(self):
        pass

    def advance_transmission(self):
        pass

    def regress_transmission(self):
        pass

c = Client(host='192.168.43.56')
c.request_file('futurama.avi')
