#  coding: utf-8 
from queue import Empty
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
        self.data = self.data.decode().split("\r\n")
        # Break it down into individual pieces, HTTP portion is unused
        if self.data[0] != "":
            method, page, unused = self.data[0].split()
            
            # Make full request path
            full_path = ROOT + page
            self.request_path = page            
            
            # Validate request
            if not self.validateMethod(method) or not self.validatePage(full_path):
                return
            else:
                self.chooseType(full_path)

    def chooseType(self, page):
        # Decide if we are dealing with a directory or file path
        if os.path.isdir(page):
            self.serveDirectory(page)
        elif os.path.isfile(page):
            self.serveFile(page)

    def serveFile(self, page):
        # Serve a given file
        file_type = os.path.splitext(page)[1]
        with open(page, "r") as file:
            content = file.read()

        # CSS Type
        if file_type == ".css":
            message = f"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\nContent-Length: {len(content)}\r\n\r\n"
            self.sendMessage(message, content)
        
        # HTML Type
        elif file_type == ".html":
            message = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\n\r\n"
            self.sendMessage(message, content)

    def sendMessage(self, message, content):
        # Send out a given message and its content
        data = message + content
        self.request.sendall(bytearray(data, "utf-8"))

    def serveDirectory(self, page):   
        # Redirect if not ending in /
        # Must scan through data because Host is not always in the same spot
        if page[-1] != "/":
            for segment in self.data:
                if "Host:" in segment:
                    hostname = segment[5:].strip()

            content = "Moved Permanently"
            error = f"HTTP/1.1 301 {content}\r\nLocation: http://{hostname}{self.request_path}/\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\n\r\n"
            self.sendMessage(error, content)

        # Serve index file of directory (ensure an index.html exists)
        curr_page =  os.path.join(page, "index.html")
        if self.validatePage(curr_page):
            self.serveFile(curr_page)
        
    def validateMethod(self, method):
        # Only accept GET method
        if method != "GET":
            content = "Method Not Allowed"
            error = f"HTTP/1.1 405 {content}\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\n\r\n"
            self.sendMessage(error, content)
            return False
        
        return True
    
    def validatePage(self, page):
        # Path must exist and must not be outside ./www directory
        if not os.path.exists(page) or 'www' not in os.path.abspath(page):
            content = "Not Found"
            error = f"HTTP/1.1 404 {content}\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\n\r\n"
            self.sendMessage(error, content)
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
