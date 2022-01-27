#  coding: utf-8 
import socketserver
import os

# Copyright 2022 Tyler Bach
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# Get the root directory for server
# Inspiration provided by Russell Dias and Mark Amery
# https://stackoverflow.com/a/5137509

dir_path = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.join(dir_path, "www")

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.data = self.data.decode().split("\n")[0]
        # Break it down into individual pieces
        method, page, unused = self.data.split()
        
        full_path = ROOT + page
        
        # Validate
        if self.validate(method, full_path):
            self.chooseType(full_path)
        else:
            print("error found in call")
            return

    def chooseType(self, page):
        if os.path.isdir(page):
            self.serveDirectory(page)
        elif os.path.isfile(page):
            self.serveFile(page)

    def serveFile(self, page):
        print("wooo serving file")

    def serveDirectory(self, page):
        print("wooo serving directory")
        
    def validate(self, method, page):
        if method != "GET":
            error = f"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\nContent-Length: 18\r\n\r\n"
            self.request.sendall(bytearray(error, "utf-8"))
            return False
        
        if not os.path.exists(page) or 'www' not in os.path.abspath(page):
            error = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: 9\r\n\r\n"
            self.request.sendall(bytearray(error, "utf-8"))
            return False
        
        return True
    
  

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
