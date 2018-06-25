import server
from sys import argv

s = server.Server(int(argv[1]))
s.accept()
