#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import os
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        if (url.find(':') != -1):
            host, port = url.split(':')
        else:
            host, port = url, 80
        return host, port

    def connect(self, host, port):
        # use sockets!
        s = socket.create_connection((host,port))
        return s

    def get_code(self, data):
        code = data.split()[1]
        return int(code)

    def get_headers(self,data):
        content = data.partition('\r\n\r\n')
        return content[0]

    def get_body(self, data):
        content = data.partition('\r\n\r\n')
        return content[2]

    def get_request(self, url):
        req = url.partition('//')[2]
        req = req.partition('/')[2]
        return req

    # read everything from the socket
    def recvall(self, sock):
        response = [sock.recv(4096)]
        while response[-1]:
            response.append(sock.recv(4096))
        return ''.join(response)

    def GET(self, url, args=None):
        urlParts = url.split('/')
        host, port = self.get_host_port(urlParts[2])
        sock = self.connect(host, port)

        request = '/'
        request += self.get_request(url)
        get = 'GET {0} HTTP/1.0\r\nHost: {1}\r\n\r\n'.format(request,
                                                             urlParts[2])
        sock.sendall(get)

        response = self.recvall(sock)
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        urlParts = url.split('/')
        host, port = self.get_host_port(urlParts[2])
        sock = self.connect(host, port)

        request = '/'
        request += self.get_request(url)

        post = 'POST %s HTTP/1.0\r\n' % request
        if args is None:
            post += "\r\n"
        else:
            postInfo = urllib.urlencode(args)
            post += 'Content-Length: ' + str(len(postInfo)) + '\r\n\r\n'
            post += postInfo

        sock.sendall(post)
        response = self.recvall(sock)
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )
