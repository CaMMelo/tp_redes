import client
from sys import argv


c = client.Client()
c.request_file(argv[1])
