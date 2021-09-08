import os
import socket

import cv2

from database import DataBase, User
import json
import pathlib
from os import mkdir, listdir
from my_utils import encrypting_password
from typing import Final
import face_recognition

MY_PATH: Final = str(pathlib.Path(__file__).parent.resolve())

TOLERANCE: Final = 0.6
FRAME_THICKNESS: Final = 3
FONT_THICKNESS: Final = 2
MODEL: Final = "cnn"


class Server(DataBase):
    def __init__(self):
        super().__init__()
        self.SERVER = "IP ADDRESS HERE"
        self.PORT = 5555
        self.SERVER_PATH = MY_PATH
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind()
        self.communicate()

    def bind(self):
        print("Binding")
        try:
            self.sock.bind((self.SERVER, self.PORT))
        except socket.error as err:
            print(err)

        self.sock.listen()

    def communicate(self):
        while True:
            self.conn, self.addr = self.sock.accept()

            data = self.conn.recv(1024).decode()
            data = json.loads(data)
            if not data["login"]:
                try:
                    self.user = User(data["username"], data["password"], data["login"])
                    self.user.password = encrypting_password(self.user.password)
                    self.add_user(self.user.name, self.user.password)
                    try:
                        mkdir(self.SERVER_PATH + f'/{self.user.name}')
                    except OSError as err:
                        print("File already exists")

                except Exception as err:
                    print(err)
                    print("An error occurred, ignoring data...")
                    continue

                self.conn.send("Ok".encode())
                data = self.conn.recv(20000000)
                with open(self.SERVER_PATH + f"/{self.user.name}/{self.user.name}.jpg", "wb") as file:
                    file.write(data)

            elif data["login"]:

                self.user = User(data['username'], data['password'], data['login'])
                self.user.password = encrypting_password(self.user.password)
                if self.check_login(self.user.name, self.user.password):
                    self.conn.send("ok".encode())
                    recognition_data = self.conn.recv(20000000)
                    verify = self.face_recognition(self.user.name, recognition_data)
                    if verify:
                        self.conn.send("Authorized".encode())
                        data = self.conn.recv(20000000)
                        length_userdir = len(listdir(self.SERVER_PATH + f"/{self.user.name}"))
                        with open(self.SERVER_PATH + f"/{self.user.name}{length_userdir + 1}.jpg", "wb") as file:
                            file.write(data)
                    else:
                        self.conn.send("Unauthorized".encode())
                else:
                    self.conn.send("invalid".encode())

    def face_recognition(self, username: str, data: bytes) -> bool:
        faces_dir = []
        user = []
        print("Loading user's images...")
        print(os.listdir(self.SERVER_PATH + f"/{username}"))
        for file in os.listdir(self.SERVER_PATH + f"/{username}"):
            image = face_recognition.load_image_file(self.SERVER_PATH + f"/{username}" + f"/{file}")
            encoding = face_recognition.face_encodings(image)[0]
            faces_dir.append(encoding)
            user.append(file)
        with open(f"{username}recognition.jpg", "wb") as file:
            file.write(data)

        image = face_recognition.load_image_file(f"{username}recognition.jpg")
        locate_face = face_recognition.face_locations(image, model=MODEL)
        encoding_processing_image = face_recognition.face_encodings(image, locate_face)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        for face_encoding, face_location in zip(encoding_processing_image, locate_face):
            comparing = face_recognition.compare_faces(faces_dir, face_encoding, TOLERANCE)

            if True in comparing:
                match = faces_dir[comparing.index(True)]
                print(f"Match found: {match}")
                return True

        print("Match not found!")
        return False


if __name__ == "__main__":
    server = Server()
