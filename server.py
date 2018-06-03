import socket
import threading
import pickle
import time
import globals

class Server:

    clients = {
        # (host, port): (tcp_socket, udp_socket, [])
    }

    def __init__(self, port=globals.PORT, buffersize=1024):

        self.addr = ('', port)
        self.buffersize = buffersize

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.addr)

    # requisições do canal de controle

    def sendto_client(self, client, client_addr, file):

        window_size = 1000
        pack_size = 1024

        with open(file, 'rb') as ifile:

            udp_sock = self.clients[client][1]

            video_packs = []

            frame = ifile.read(pack_size)
            x = 0

            while frame:
                video_packs.append((x, frame))
                frame = ifile.read(pack_size)
                x += 1

            init = 0
            current = 0

            while True:

                # enviar pacotes
                n = 0

                while (n < window_size) and (current < len(video_packs)):
                    time.sleep(0.0009)
                    udp_sock.sendto(pickle.dumps(video_packs[current]), client_addr)
                    n += 1
                    current += 1

                # esperar acks
                udp_sock.settimeout(1)

                try:

                    data, _ = udp_sock.recvfrom(self.buffersize)

                    if data:
                        data = pickle.loads(data)
                        init = data[0] + 1

                except:

                    pass

                if init == len(video_packs):
                    break

                if current == len(video_packs):
                    print('finished')
                    current = init
                    break

            # enviar flag de fim de video

    def handle_client(self, client):

        print(client)

        while True:

            data = self.clients[client][0].recv(self.buffersize)

            if data:

                request = pickle.loads(data)

                if request[0] == globals.FILE_REQUEST:

                    t = threading.Thread(target=self.sendto_client, args=(client, request[1], request[2]))
                    t.start()


    def accept(self):

        self.sock.listen(100)

        while True:

            tcp_sock, addr = self.sock.accept()

            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.clients[addr] = [tcp_sock, udp_sock, None]

            t = threading.Thread(target=self.handle_client, args=(addr, ))
            t.start()




s = Server()
s.accept()
