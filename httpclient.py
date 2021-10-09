#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, Matthew Mullen, and https://github.com/treedust
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

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    def get_host_port(self, url):
        parsedUrl = urllib.parse.urlparse(url)
        host = parsedUrl.hostname
        port = 80
        path = parsedUrl.path
        try:
            if parsedUrl.port:
                port = int(parsedUrl.port)
            if path == '':
                path = '/'
        except:
            print("there was some issue in parsing the url or some info was missing so resorting to some default")
        finally:
            return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        try:
            responseCode = data[0]
            responseCode = responseCode.split()
            statusCode = responseCode[1]
            return int(statusCode)
        except:
            return 404

    def get_headers(self, data):
        try:

            headersWithData = data[:len(data) - 2]
            headers=[]
            for header in headersWithData[1:]:
                justHeader=header.split()[0]
                headers.append(justHeader[:len(justHeader)-1])
            return headers
        except:
            return "parsing headers failed"

    def get_body(self, data):
        try:
            #print("body IS HERE")

            body = data[-1]
            return body
        except:
            return "Invalid body"

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = self.get_host_port(url)
        self.connect(host, port)
        payload = "GET " + path + " HTTP/1.1\r\n" + "Host: " + host + '\r\n\r\n'
        self.sendall(payload)
        response = self.recvall(self.socket)
        self.close()
        data = response.split('\r\n')
        code, body, headers = self.get_code(data), self.get_body(data), self.get_headers(data)
        #print("BODY IS RIGHT HERE")
        #print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host,port,path=self.get_host_port(url)
        self.connect(host,port)
        contentType = "application/x-www-form-urlencoded"
        contentLength = 0
        postArgs = ""
        if args:
            postArgs=urllib.parse.urlencode(args)
            contentLength=len(postArgs)
        payload = """POST {} HTTP/1.1\r\nHost: {}
                    \r\nContent-Type: application/x-www-form-urlencoded
                    \r\nContent-Length: {}\r\n\r\n{}
                        """.format(path, host, contentLength, postArgs)
        #payload="POST %s HTTP/1.1\r\nHost: %s" \
        #        "\r\nContent-Type: %s" \
        #        "\r\nContent-Length: %d" % (path,host,contentType,contentLength)
        self.sendall(payload)
        response=self.recvall(self.socket)
        self.close()
        response=response.split('\r\n')
        code,header,body=self.get_code(response),self.get_headers(response),self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
