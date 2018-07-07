#!/usr/bin/python3

from tkinter import *
import socket
import pickle
import sys
import globals
import time
import threading
import os
import io
from math import ceil

class ControlWindow(Frame):

    def __init__(self, client=None, master=None):
        Frame.__init__(self, master)

        self.master = master

        botao = Button(master, text="Pause", command = client.pause_transmistion)
        botao.pack()

        botao = Button(master, text="Continue", command = client.continue_transmission)
        botao.pack()

class Client:

    def __init__(self, host='127.0.0.1', port=globals.PORT, buffersize=1024):

        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect(self.addr)

        self.buffersize = 1024

    def output(self, consume):
        ''' thread para imprimir um buffer na saida padrão '''

        self.lock.acquire()

        pos = self.video.tell()
        self.video.seek(self.ptr, 0)
        buffer = self.video.read(ceil(consume))
        self.video.seek(pos)

        if buffer and not self.paused:
            sys.stdout.buffer.write(buffer)
            self.ptr += ceil(consume)

        self.lock.release()

        time.sleep(1)
        t = threading.Thread(target=self.output, args=(consume, ))
        t.start()
        t.join()

    def append_to_file(self, buffer):

        self.lock.acquire()

        for pct in buffer:
            self.video.write(pct[1])

        self.lock.release()

    def recv_file(self, udp_sock, tamanho_do_pacote, buffer_inicial, buffer_leitura, bit_rate):

        buffersize = buffer_inicial

        # começa a receber o vídeo

        self.video = io.BytesIO()
        self.ptr = 0
        self.paused = False
        self.lock = threading.Lock()

        while True:

            buffer = []

            while len(buffer) < buffersize:

                pacote, _ = udp_sock.recvfrom(tamanho_do_pacote + 100)
                pacote = pickle.loads(pacote)

                if not pacote:
                    break

                buffer.append(pacote)

            buffer.sort(key=lambda x: x[0])

            t = threading.Thread(target=self.append_to_file, args=(buffer,))
            t.start()
            t.join()

            if len(buffer) == buffer_inicial:
                buffersize = buffer_leitura

                t = threading.Thread(target=self.output, args=(bit_rate, ))
                t.start()

        udp_sock.close()

    # tcp
    def request_file(self, filename):
        ''' faz a requisição via TCP e recebe o arquivo via UDP '''

        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('192.168.43.12', 0)) # abre em uma porta aleatoria

        data = (globals.FILE_REQUEST, udp_sock.getsockname(), filename)
        self.sock.send(pickle.dumps(data))

        # combinar: tamanho_do_pacote, tamanho_do_buffer, tempo_de_reenvio

        self.sock.recv(self.buffersize)
        self.sock.send(b'0'*self.buffersize)

        data = self.sock.recv(self.buffersize)
        tamanho_do_pacote, buffer_inicial, buffer_leitura, bit_rate = pickle.loads(data)

        t = threading.Thread(target=self.recv_file, args=(udp_sock, tamanho_do_pacote, buffer_inicial, buffer_leitura, bit_rate))
        t.start()

        root = Tk()
        app = ControlWindow(self, root)
        root.mainloop()

    # comandos de controle de fluxo
    def pause_transmistion(self):
        self.paused = True

    def continue_transmission(self):
        self.paused = False

    def stop_transmission(self):
        pass

    def advance_transmission(self, nbytes):
        pass

    def regress_transmission(self, nbytes):
        self.ptr -= nbytes
