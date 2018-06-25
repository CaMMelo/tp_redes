import socket
import pickle
import sys
import globals
import time
import threading

class Client:

    def __init__(self, host='127.0.0.1', port=globals.PORT, buffersize=1024):

        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect(self.addr)

        self.buffersize = 1024

    def output(self, buffer):
        ''' thread para imprimir um buffer na saida padrão '''
        for x in buffer:
            sys.stdout.buffer.write(x[1])

    def request_file(self, filename):
        ''' faz a requisição via TCP e recebe o arquivo via UDP '''

        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('', 0)) # abre em uma porta aleatoria

        data = (globals.FILE_REQUEST, udp_sock.getsockname(), filename)
        self.sock.send(pickle.dumps(data))

        # combinar: tamanho_do_pacote, tamanho_do_buffer, tempo_de_reenvio

        self.sock.recv(self.buffersize)
        self.sock.send(b'0'*self.buffersize)

        data = self.sock.recv(self.buffersize)
        tamanho_do_pacote, buffer_inicial, buffer_leitura = pickle.loads(data)
        buffersize = buffer_inicial

        # começa a receber o vídeo

        video = [] # o video começa vazio

        while True:

            buffer = []

            while len(buffer) < buffersize:

                pacote, _ = udp_sock.recvfrom(tamanho_do_pacote + 100)
                pacote = pickle.loads(pacote)

                if not pacote:
                    break

                buffer.append(pacote)

                buffer.sort(key=lambda x: x[0])
                video += buffer

                if len(buffer) == buffer_inicial:
                    buffersize = buffer_leitura

            t = threading.Thread(target=self.output, args=(buffer,))
            t.start()
            t.join()

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
