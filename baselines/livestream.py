from pathlib import Path
import pylivestream.fglob as pls
import matplotlib.pyplot as plt
from multiprocessing import shared_memory
import numpy as np
import threading

from multiprocessing.connection import Listener, Client
import socket
import pickle
import time

FRAME_WIDTH = 640
FRAME_HEIGHT = 540

VERTICAL_FRAME_COUNT = 3
HORIZONTAL_FRAME_COUNT = 2

class Livestream_Server():

    def __init__(self, s_path) -> None:
        self.s_path = s_path

        self.framemap = {}
        self.scoremap = {}
        self.lock = threading.Lock()
        pass


    def update_stream_frame(self):
        stream_frame = np.ndarray((1080,1920,3), dtype="uint8")

        i=0
        for index, _ in dict(sorted(self.scoremap.items(), key=lambda item: item[1], reverse=True)).items():
            row, col = divmod(i,VERTICAL_FRAME_COUNT)
            if row >= HORIZONTAL_FRAME_COUNT:
                break
            i+=1

            render_row = row * FRAME_HEIGHT
            render_col = col * FRAME_WIDTH

            stream_frame[render_row:render_row+self.framemap[index].shape[0],render_col:render_col+self.framemap[index].shape[1]] = self.framemap[index]


        self.lock.acquire()
        try:
            print("updating frame")
            plt.imsave( self.s_path / Path(f'livestream.jpeg'),stream_frame)
        except Exception as e:
                print(f"Error during framegen: {e}")
        self.lock.release()

    def start_server(self):
        with socket.socket() as s:
            s.bind(('localhost', 40555))
            s.listen()
            while True:
                client, addr = s.accept()
                # print(f'{addr}: connected')
                with client, client.makefile('rb') as rfile:
                    while True:
                        try:
                            data = pickle.load(rfile)
                        except EOFError:  # Throws exception if incomplete or socket closed
                            break
                        # print(data)
                        # print(f'index ({data[0]}), score ({data[1]})')
                        self.framemap[data[0]] = data[2]
                        self.scoremap[data[0]] = data[1]
                # print(f'{addr}: disconnected')


class Livesteam_Client():
        def __init__(self) -> None:
            pass

        def send_frame(self,index, score, frame):
            with socket.socket() as s:
                s.connect(('localhost', 40555))
                self.transmit(s,[index,score,frame])
                s.close()

        def transmit(self, sock, data):
            serial_data = pickle.dumps(data)
            sock.sendall(serial_data)

