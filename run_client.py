import client
from sys import argv


c = client.Client(argv[1], int(argv[2]))
c.request_file(argv[3])
