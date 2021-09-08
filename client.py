import socket
from typing import Final
from facial_recognition import send_photo


class Client:
    def __init__(self):
        print("Initializing client...")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server: Final = "SERVER'S IP ADDRESS HERE"
        self.port: Final = 5555
        self.addr = (self.server, self.port)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            print("connected")
        except Exception as err:
            print(err)

    def send(self, data: bytes):
        try:
            self.client.send(data)
        except socket.error as err:
            print(err)

    def receive_answer(self) -> str:
        return self.client.recv(1024).decode()


