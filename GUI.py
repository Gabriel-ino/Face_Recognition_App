import io

import cv2
from PySimpleGUI import PySimpleGUI as sg
from functools import lru_cache
from typing import Final
from client import Client
from my_utils import convert_to_json_binary
from pathlib import Path
from os import mkdir, path, execl
from database import User
from facial_recognition import send_photo
from PIL import Image
from time import sleep
import sys

APP_THEME: Final = sg.theme('DarkPurple1')
DIR = '/user_images'
PATH = Path(__file__).parent.resolve()


@lru_cache
def options_window():
    APP_THEME
    layout = [
        [sg.Button("Login"), sg.Button("Register")]
    ]

    return sg.Window("Initial menu", layout=layout, finalize=True)


@lru_cache
def login_window():
    APP_THEME
    layout = [
        [sg.Text('Username\t\t\t\t\t'), sg.Text("Password")],
        [sg.Input(key="user"), sg.Input(key="password", password_char="*")],
        [sg.Button("Continue")]
    ]
    return sg.Window("Login", layout=layout, finalize=True)


@lru_cache
def register_window():
    APP_THEME
    layout = [
        [sg.Text('Username\t\t\t\t\t'), sg.Text("Password")],
        [sg.Input(key="user"), sg.Input(key="password", password_char="*")],
        [sg.Button("Continue")]
    ]
    return sg.Window("Register", layout=layout, finalize=True)


@lru_cache
def add_photo():
    APP_THEME
    layout = [
        [sg.Image(key="IMAGE")],
        [sg.Text("Choose a image file"),
         sg.Input(size=(25, 1), key="FILE"),
         sg.FileBrowse(),
         sg.Button("Load Image")
         ],
    ]

    return sg.Window("Loading image", layout=layout, finalize=True)


@lru_cache
def run_gui():
    try:
        mkdir(str(PATH) + DIR)
    except:
        pass

    win1, win2, win3, win4 = options_window(), None, None, None
    client = Client()
    while True:
        window, event, val = sg.read_all_windows()

        """
        
        OPTION WINDOW
        
        """

        if window == win1:
            if event == sg.WIN_CLOSED:
                break
            if event == "Register":
                win2 = register_window()
                win1.close()

            if event == "Login":
                win3 = login_window()
                win1.close()

        """
        
        REGISTER WINDOW
        
        """

        if window == win2:
            if event == sg.WIN_CLOSED:
                break
            if event == "Continue":
                if val['user'] == "" or val['password'] == "":
                    sg.popup("You leave blank options", keep_on_top=True)
                    continue
                user_dict = {'username': val['user'],
                             'password': val['password'],
                             'login': False}

                user = User(user_dict["username"], user_dict["password"], user_dict["login"])
                data = convert_to_json_binary(user_dict)
                client.send(data[0])

                if client.receive_answer() == 'Ok':
                    sg.popup_auto_close("Prepare to take a photo for facial recognition\nTime:5s", keep_on_top=True)
                    byte_photo = send_photo(user.name)
                    client.send(byte_photo)

        if window == win3:
            if event == sg.WIN_CLOSED:
                break
            if event == "Continue":
                if val['user'] == "" or val['password'] == "":
                    sg.popup("You leave blank options", keep_on_top=True)
                    continue
                user_dict = {'username': val['user'],
                             'password': val['password'],
                             'login': True}
                user = User(user_dict["username"], user_dict["password"], user_dict["login"])
                data = convert_to_json_binary(user_dict)
                client.send(data[0])
                feedback = client.receive_answer()
                if feedback == "invalid":   # Receive feedback from server for the credentials
                    sg.popup("Invalid credentials", keep_on_top=True)
                    sleep(2)
                    execl(sys.executable, sys.executable, *sys.argv)  # Reinitialize app

                elif feedback == "ok":
                    sg.popup_auto_close("Prepare for face recognition...", keep_on_top=True)
                    byte_photo = send_photo(user.name)
                    client.send(byte_photo)
                    sg.popup_auto_close("Processing, please wait...", keep_on_top=True)
                    face_feedback = client.receive_answer()
                    if face_feedback == "Authorized":
                        sg.popup_auto_close(f"Welcome, {user.name}!", keep_on_top=True)
                        sleep(2)
                        win4 = add_photo()
                        win3.close()
                    else:
                        sg.popup_auto_close("You cannot access this area", keep_on_top=True)
                        execl(sys.executable, sys.executable, *sys.argv)

        if window == win4:
            if event == sg.WIN_CLOSED:
                break
            if event == "Load Image":
                photo_file = val["FILE"]
                if path.exists(photo_file):
                    image = Image.open(val["FILE"])
                    image.thumbnail((400, 400))
                    bio = io.BytesIO()
                    image.save(bio, format="JPG")
                    window["IMAGE"].update()
                    client.send(bio.read())



