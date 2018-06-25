import socket
import threading
import pickle
import time
import globals
import os
import ffprobe3

class Server:

    clients = {
        # (host, port): (tcp_socket, udp_socket, [])
    }

    def __init__(self, port=globals.PORT, buffersize=1024):

        self.addr = ('', port)
        # self.addr = ('', port)
        self.buffersize = buffersize

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.addr)

    # requisições do canal de controle

    def sendto_client(self, client, client_udp_sock_addr, filename, tamanho_do_pacote, atraso):
        ''' thread para enviar um arquivo de vídeo para um cliente '''

        # tcp_sock = self.clients[client][0]
        udp_sock = self.clients[client][1]

        tamanho_do_pacote = int(tamanho_do_pacote)

        with open(filename, 'rb') as infile:

            buffer = {}

            payload = infile.read(tamanho_do_pacote)
            i = 0

            while payload:

                buffer[i] = payload

                udp_sock.sendto( pickle.dumps((i, payload)), client_udp_sock_addr)
                time.sleep(atraso)

                i += 1
                payload = infile.read(tamanho_do_pacote)

            udp_sock.sendto(b'', client_udp_sock_addr)

        print('finalizado')


    def handle_client(self, client):

        ''' Trata as requisições TCP de um determinado cliente '''

        cli = self.clients[client][0]

        while True:

            data = cli.recv(self.buffersize)


            if data:

                request = pickle.loads(data)

                if request[0] == globals.FILE_REQUEST:

                    start = time.time()
                    cli.send(b'0'*self.buffersize)
                    cli.recv(self.buffersize)
                    rtt = self.buffersize / ((time.time() - start) / 2) # quantos bytes por segundo

                    metadata = ffprobe3.FFProbe(request[2]).video[0]

                    # filesize = os.stat(request[2]).st_size  # em bytes

                    bit_rate = int(metadata.bit_rate) / 8   # em bytes por segundo
                    # duration = metadata.duration_seconds()  # em segundos

                    tamanho_do_pacote = int(bit_rate // 1024) # tamanho do pacote
                    atraso = 0 if ((rtt - tamanho_do_pacote) <= 0) else ((rtt - tamanho_do_pacote) / rtt / 1000)

                    buffer_inicial = 1024
                    buffer_leitura = 200

                    print(buffer_inicial, buffer_leitura)

                    cli.send(pickle.dumps((tamanho_do_pacote, buffer_inicial, buffer_leitura)))

                    t = threading.Thread(target=self.sendto_client, args=(client, request[1], request[2], tamanho_do_pacote, atraso))
                    t.start()


    def accept(self):
        ''' aceita uma conexão TCP e envia delega uma thread para manipular o usuário '''

        self.sock.listen(100)

        while True:

            tcp_sock, addr = self.sock.accept()

            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.clients[addr] = [tcp_sock, udp_sock, None]

            t = threading.Thread(target=self.handle_client, args=(addr, ))
            t.start()
