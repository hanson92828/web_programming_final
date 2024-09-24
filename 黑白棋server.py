import socket

HOST = '127.0.0.1'
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)

print('server start at: %s:%s' % (HOST, PORT))
print('wait for connection...')

conn1, addr1 = s.accept()
print('connected by ' + str(addr1))

conn2, addr2 = s.accept()
print('connected by ' + str(addr2))
s.setblocking(False)
while True:
    try:
        indata1 = conn1.recv(1024)
        conn2.send(indata1)
        print('recvfrom client1: '+indata1.decode())

        indata2 = conn2.recv(1024)
        conn1.send(indata2)
        print('recvfrom client2: '+indata2.decode())
    except:
        pass
s.close()
