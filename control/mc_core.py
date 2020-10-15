from collections import namedtuple
import socket
import threading

Server = namedtuple("Server", ["name", "ip_and_port"])

class ControlCore:
    __instance = None
    __login_thread = None
    __connected_servers = [Server(name="test123", ip_and_port=("192.168.1.78", 52555))]
    __last_response = None
    message_ending_string = "_-_@MSG_END"

    def __init__(self):
        if ControlCore.__instance == None:
            ControlCore.__instance = self
        else:
            raise Exception("Instance already made.")
    
    @staticmethod
    def get_instance():
        if ControlCore.__instance == None:
            ControlCore()
        
        return ControlCore.__instance
    
    def print_something(self):
        print("Something")
    
    def send_to(self, server, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server.ip_and_port)
        if not message.endswith("\n"):
            message = message + "\n"
        response = ""
        s.sendall(message.encode("ascii"))
        
        while not ControlCore.message_ending_string in response:
        #while not response.endswith(ControlCore.message_ending_string):
            response = response + s.recv(2048).decode("ascii")
        
        s.close()

        response = response.replace(ControlCore.message_ending_string, "")
        self.__last_response = response

        return response
    
    def send_to_all(self, line):
        if(line.startswith("!")):
            line = line[1:]
        if not line.endswith("\n"):
            line = line + "\n"
        message = line.encode("ascii")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        for serv in self.__connected_servers:
            print("Sending to:", serv)
            s.connect(serv.ip_and_port)
            s.sendall(message)
            s.close()
        
        print("Sent to all")
    
    def get_server_by_index(self, index):
        return self.__connected_servers[index]
    
    def get_server_by_name(self, name):
        for s in self.__connected_servers:
            if s.name == name:
                return s
        
        return None
    
    def listen_to_login(self, line):
        listen_to_login_port()

def listen_to_login_port():
    host_ip = "192.168.0.115"
    login_port = 51423
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((host_ip, login_port))
    while True:
        data = serversocket.listen(5)
        if(data != None):
            print(data)
