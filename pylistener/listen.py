import socket

host = "192.168.0.115"
port = 51423

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected by: ", addr)
        while True:
            data = conn.recv(1024)
            if data:
                print(data)