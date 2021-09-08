import cv2
from typing import AnyStr, List

video = cv2.VideoCapture(0)


def send_photo(username: AnyStr) -> bytes:
    counter = 0
    while True:
        check, frame = video.read()
        cv2.imshow("Color Frame", frame)

        key = cv2.waitKey(1)

        if counter == 40:
            cv2.imwrite(f"{username}.jpg", frame)
            with open(f"{username}.jpg", "rb") as file:
                byte_file = file.read()
            video.release()
            cv2.destroyAllWindows()
            return byte_file

        counter += 1

