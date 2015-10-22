""" Simple test client of the XMLRPC server.
"""
import xmlrpclib

server = xmlrpclib.ServerProxy('http://127.0.0.1:8000')

server.move(20, 0, 0.2)

with open('xmlrpcsumo_testclient.jpg', 'wb') as f:
    f.write(server.pic().data)
