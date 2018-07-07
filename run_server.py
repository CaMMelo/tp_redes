import server
from sys import argv

s = server.Server(argv[1], int(argv[2]))
s.accept()
