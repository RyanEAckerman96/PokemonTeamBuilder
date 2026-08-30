import threading
from threading import Thread

import signal

from websockets.sync.client import connect
import websockets

import os

import requests

import time

import json


class WebSocketClient():
    def __init__(self):
        self.url = "ws://localhost:8765"
        self.stop = False
        self.ws = connect(self.url, legacy=True)

    def start(self):
        try:
            while not self.stop:
                try:
                    message = self.ws.recv()
                    print(f"[Received] {message}")
                    global logged_on
                    global modified
                    if(logged_on == False):
                        logged_on = True
                    else:
                        modified = True
                except Exception as e:
                    print(e)
                    break
        except Exception as e:
            print(e)
        finally:
            if self.ws:
                self.ws.close()

    def send_message(self, message):
        self.ws.send(message)

    def shutdown(self):
        self.stop = True
        if self.ws:
            self.ws.close()


if __name__ == "__main__":

    global logged_on
    logged_on = False

    global modified
    modified = False
    
    try:
        _client = WebSocketClient()
        _client_thread = Thread(target = _client.start)
        _client_thread.daemon = True   


        def signal_handler(sig, frame):
            print("Client Shutting Down")
            _client.shutdown()
            _client_thread.join()
            logged_on = True


        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


        _client_thread.start()

        
        logon_msg = '{"action":"logon", "user":"admin", "pw":"admin"}'

        _client.send_message(logon_msg)



        while(not logged_on):
            time.sleep(0.1)

        #modify_msg = '{"action":"modify_pokemon", "user":"admin", "id":1024, "name":"Not Terapagos", "types":["rock"]}'
        modify_msg = '{"action":"modify_pokemon", "user":"admin", "id":1024, "name":"Terapagos", "types":["normal"]}'
        
        _client.send_message(modify_msg)

        while(not modified):
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        _client.shutdown()
        _client_thread.join()
    finally:
        print("[DONE]")
