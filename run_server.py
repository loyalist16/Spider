import os
from http.server import HTTPServer,SimpleHTTPRequestHandler
import settings

BASE_PATH = settings.BASE_PATH
port = 8080
host = ('0.0.0.0', port)

if __name__ == "__main__":
    os.chdir(BASE_PATH + "/result_file/")
    server = HTTPServer(host, SimpleHTTPRequestHandler)
    print('Starting server, listen at: %s:%s' % host)
    server.serve_forever()