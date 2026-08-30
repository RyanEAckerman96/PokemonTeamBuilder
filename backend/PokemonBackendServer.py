import threading
from threading import Thread

import signal

from websockets.sync.server import serve
import websockets

import pickle

import os

import requests

import time

import json

import copy

#####################
# GLOBALS
#####################
global _server
global user_db
pokemon_db = {}
interrupt_sleep = threading.Event()

weaknesses_def_to_atk = {
        "normal":   {"normal":1, "fire":1, "water":1, "electric":1, "grass":1, "ice":1, "fighting":2, "poison":1, "ground":1, "flying":1, "psychic":1, "bug":1, "rock":1, "ghost":0, "dragon":1, "dark":1, "steel":1, "fairy":1},      
        "fire":     {"normal":1, "fire":0.5, "water":0.5, "electric":2, "grass":0.5, "ice":0.5, "fighting":1, "poison":1, "ground":2, "flying":1, "psychic":1, "bug":0.5, "rock":1, "ghost":1, "dragon":1, "dark":1, "steel":0.5, "fairy":0.5},  
        "water":    {"normal":1, "fire":0.5, "water":0.5, "electric":2, "grass":2, "ice":0.5, "fighting":1, "poison":1, "ground":1, "flying":1, "psychic":1, "bug":1, "rock":1, "ghost":1, "dragon":1, "dark":1, "steel":0.5, "fairy":1},   
        "electric": {"normal":1, "fire":1, "water":1, "electric":0.5, "grass":1, "ice":1, "fighting":1, "poison":1, "ground":2, "flying":0.5, "psychic":1, "bug":1, "rock":1, "ghost":1, "dragon":1, "dark":1, "steel":0.5, "fairy":1},    
        "grass":    {"normal":1, "fire":2, "water":0.5, "electric":0.5, "grass":0.5, "ice":2, "fighting":1, "poison":2, "ground":0.5, "flying":2, "psychic":1, "bug":2, "rock":1, "ghost":1, "dragon":1, "dark":1, "steel":1, "fairy":1},     
        "ice":      {"normal":1, "fire":2, "water":1, "electric":1, "grass":1, "ice":0.5, "fighting":2, "poison":1, "ground":1, "flying":1, "psychic":1, "bug":1, "rock":2, "ghost":1, "dragon":1, "dark":1, "steel":2, "fairy":1},
        "fighting": {"normal":1, "fire":1, "water":1, "electric":1, "grass":1, "ice":1, "fighting":1, "poison":1, "ground":1, "flying":2, "psychic":2, "bug":0.5, "rock":0.5, "ghost":1, "dragon":1, "dark":0.5, "steel":1, "fairy":2},        
        "poison":   {"normal":1, "fire":1, "water":1, "electric":1, "grass":0.5, "ice":1, "fighting":0.5, "poison":0.5, "ground":2, "flying":1, "psychic":2, "bug":0.5, "rock":1, "ghost":1, "dragon":1, "dark":1, "steel":1, "fairy":0.5},       
        "ground":   {"normal":1, "fire":1, "water":2, "electric":0, "grass":2, "ice":2, "fighting":1, "poison":0.5, "ground":1, "flying":1, "psychic":1, "bug":1, "rock":0.5, "ghost":1, "dragon":1, "dark":1, "steel":1, "fairy":1},
        "flying":   {"normal":1, "fire":1, "water":1, "electric":2, "grass":0.5, "ice":2, "fighting":0.5, "poison":1, "ground":0, "flying":1, "psychic":1, "bug":0.5, "rock":2, "ghost":1, "dragon":1, "dark":1, "steel":1, "fairy":1},        
        "psychic":  {"normal":1, "fire":1, "water":1, "electric":1, "grass":1, "ice":1, "fighting":0.5, "poison":1, "ground":1, "flying":1, "psychic":0.5, "bug":2, "rock":1, "ghost":2, "dragon":1, "dark":2, "steel":1, "fairy":1},        
        "bug":      {"normal":1, "fire":2, "water":1, "electric":1, "grass":0.5, "ice":1, "fighting":0.5, "poison":1, "ground":0.5, "flying":2, "psychic":1, "bug":1, "rock":2, "ghost":1, "dragon":1, "dark":1, "steel":1, "fairy":1},        
        "rock":     {"normal":0.5, "fire":0.5, "water":2, "electric":1, "grass":2, "ice":1, "fighting":2, "poison":0.5, "ground":2, "flying":0.5, "psychic":1, "bug":1, "rock":1, "ghost":1, "dragon":1, "dark":1, "steel":1, "fairy":1},       
        "ghost":    {"normal":0, "fire":1, "water":1, "electric":1, "grass":1, "ice":1, "fighting":0, "poison":0.5, "ground":1, "flying":1, "psychic":1, "bug":0.5, "rock":1, "ghost":2, "dragon":1, "dark":2, "steel":1, "fairy":1},        
        "dragon":   {"normal":1, "fire":0.5, "water":0.5, "electric":0.5, "grass":0.5, "ice":2, "fighting":1, "poison":1, "ground":1, "flying":1, "psychic":1, "bug":1, "rock":1, "ghost":1, "dragon":2, "dark":1, "steel":1, "fairy":2},       
        "dark":     {"normal":1, "fire":1, "water":1, "electric":1, "grass":1, "ice":1, "fighting":2, "poison":1, "ground":1, "flying":1, "psychic":0, "bug":2, "rock":1, "ghost":0.5, "dragon":1, "dark":0.5, "steel":1, "fairy":2},       
        "steel":    {"normal":0.5, "fire":2, "water":1, "electric":1, "grass":0.5, "ice":0.5, "fighting":2, "poison":0, "ground":2, "flying":0.5, "psychic":0.5, "bug":0.5, "rock":0.5, "ghost":1, "dragon":0.5, "dark":1, "steel":0.5, "fairy":0.5},        
        "fairy":    {"normal":1, "fire":1, "water":1, "electric":1, "grass":1, "ice":1, "fighting":0.5, "poison":2, "ground":1, "flying":1, "psychic":1, "bug":0.5, "rock":1, "ghost":1, "dragon":0, "dark":0.5, "steel":2, "fairy":1},
    }

class PokemonData:
    def __init__(self, id_num, name, types, sprite_url, create_time):
        self.id_num = id_num
        self.name = name
        self.types = types
        self.sprite_url = sprite_url
        self.create_time = create_time

    def __str__(self):
        return f"{self.id_num}:{self.name}:{self.types}:{self.sprite_url}:{self.create_time}"

    def __eq__(self, other):
        return self.id_num == other.id_num and self.name == other.name and sorted(self.types) == sorted(other.types)


class TeamData:
    def __init__(self,team_id, pokemon1:PokemonData, pokemon2:PokemonData, pokemon3:PokemonData, pokemon4:PokemonData, pokemon5:PokemonData, pokemon6:PokemonData):
        self.team_id = team_id
        self.team = [pokemon1, pokemon2, pokemon3, pokemon4, pokemon5, pokemon6]

class UserData:
    def __init__(self, username, pw):
        self.username = username
        self.password = pw
        self.teams = {}

    def __str__(self):
        to_print = self.username + ":"

        for val in self.teams:
            to_print += val + "{"
            for pkm in self.teams[val]:
                to_print += str(pkm) + ","
            to_print +="},"
        return to_print


class PokemonScraper:
    def __init__(self, pokemon_db_filename):
        self.pokemon_db_filename = pokemon_db_filename
        self.stop = False

        global pokemon_db
        
        if(os.path.isfile(self.pokemon_db_filename)):
            with open(self.pokemon_db_filename, 'rb') as file:
                pokemon_db = pickle.load(file)
                #for val in pokemon_db:
                #    print (pokemon_db[val])
                print("[LOADED] " + str(len(pokemon_db)) + " pokemon")
        
    def start(self):
        print("[RETREIVING POKEMON DATA]")
        self.api_url = "https://pokeapi.co/api/v2/pokemon/"
        pokemon_id = 1

        global pokemon_db
        global interrupt_sleep
        
        while not self.stop:
            url = self.api_url + str(pokemon_id)

            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                print("[CONNECTION ERROR] ", url)
                time.sleep(1)
                continue
            except requests.exceptions.Timeout:
                print("[TIMEOUT]")
                time.sleep(1)
                continue

            if(response.status_code == 200):
                data = response.json()
                #print(str(data["id"]) + " : " + data["name"] + " : " + str(data["types"]))

                types = []
                for val in data["types"]:
                    types.append(val["type"]["name"])
                dt = PokemonData(data["id"], data["name"],types, data["sprites"]["front_default"], time.time())
                if(pokemon_id in pokemon_db):
                    if(not dt == pokemon_db[pokemon_id]):
                        print("[UPDATED POKEMON]")
                        pokemon_db[pokemon_id] = dt
                    else:
                        #print("[EXISTING POKEMON ALREADY IN DB]")
                        pass
                else:
                    print("[NEW POKEMON]")
                    pokemon_db[pokemon_id] = dt
                #print(dt)
                             
                pokemon_id+=1
                time.sleep(0.5)
            elif(response.status_code == 404):
                print("[DONE REQUESTING POKEMON]")
                pokemon_id=1
                interrupt_sleep.wait(timeout=1800)
            else:
                print("[UNKNOWN ISSUE]")
                time.sleep(1)
                
    def shutdown(self):
        self.stop = True
        global interrupt_sleep
        interrupt_sleep.set()
        with open(self.pokemon_db_filename, "wb") as file:
            pickle.dump(pokemon_db, file)

        
  
class APIServer:
    global pokemon_db
    
    def client_handler(self, ws):
        print(f"[SERVER] Client connected from: {ws.remote_address}")
        remote_addr = ws.remote_address
        try:
            # Keep listening for incoming messages from this client

            for message in ws:
                print(f"[SERVER] Received: {message}")
                try:
                    msg = json.loads(message)
                    if("action" in msg):
                        if(msg["action"] == "register"):
                            if(msg["user"] not in self.user_db):
                               if(msg["pw1"] == msg["pw2"]):
                                   self.user_db[msg["user"]] = UserData(msg["user"], msg["pw1"])
                                   ws.send('{"status":200, "responding":"register", "info":{"text":"REGISTERED"}}')
                                   print("[REGISTERED USER] : " + msg["user"])
                               else:
                                   ws.send('{"status":404, "responding":"register", "info":{"text":"Passwords do not match"}}')
                            else:
                                ws.send('{"status":404, "responding":"register", "info":{"text":"User Already Exists"}}')
                                print("[USER Already Exists] : " + msg["user"])
                        elif(msg["action"] == "logon"):
                            if(msg["user"] in self.user_db):
                                if(msg["pw"] == self.user_db[msg["user"]].password):
                                    print("[USER Logged in]: " + msg["user"])
                                    ws.send('{"status":200, "responding":"logon", "info":{"text":"Logged in"}}')
                                    self.logged_in_users[ws] = msg["user"]
                                else:
                                    ws.send('{"status":404, "responding":"logon", "info":{"text":"Password incorrect"}}')
                            else:
                                ws.send('{"status":404, "responding":"logon", "info":{"text":"Unkown User"}}')
                        elif(msg["action"] == "get_pokemon"):
                            pos = msg["pos"]
                            pok_id = msg["id"]
                            if(pok_id in pokemon_db):
                                pokemon = pokemon_db[pok_id]
                                data = f'{{"id_num":{pokemon.id_num}, "name":"{pokemon.name}", "types":{pokemon.types}, "sprite_url":"{pokemon.sprite_url}", "create_time":{pokemon.create_time} }}'

                                to_send = '{"status":200, "responding":"get_pokemon", "info":{ "pos":'+ str(pos) +', "pokemon":'+data +'}}'
                                to_send = to_send.replace("'",'"')
                                print("[SENDING] " + to_send)
                                ws.send(to_send)
                            else:
                                ws.send('{"status":404, "responding":"get_pokemon", "info":{"text":"Unknown Pokemon"}}')
                        elif(msg["action"] == "load_teams"):
                            user = msg["user"]
                            if(ws in self.logged_in_users):
                                if(self.logged_in_users[ws] == user):
                                    if(user not in self.user_db):
                                        ws.send('{"status":404, "responding":"load_teams", "info":{"text":"Unregister User"}}')
                                    else:
                                        if("name" not in msg):
                                            print("[LOADING TEAM NAMES]")

                                            teams = self.user_db[user].teams
                                            print(teams)
                                            str_teams = '['
                                            for val in teams:
                                                print (val)
                                                str_teams += '"' + val + '"' + ','
                                            str_teams = str_teams[0:-1]
                                            str_teams += ']'
                                        

                                            ws.send('{"status":200, "responding":"load_teams_names", "info":{ "teams":'+str_teams+'}}')
                                                
                                        else:
                                            name = msg["name"]
                                            print("[LOADING TEAM]: " + name)


                                            if name in self.user_db[user].teams:
                                                team = self.user_db[user].teams[name]

                                                saved_team = '['
                                                db_team = '['
                                                added = False
                                                for val in team:
                                                    
                                                    pk_dat = team[val]

                                                    db_dat = pokemon_db[val]

                                                    saved_team += f'{{ "id":"{val}", "name":"{pk_dat.name}","types":{pk_dat.types},"sprite_url":"{pk_dat.sprite_url}", "create_time":{pk_dat.create_time} }},'
                                                    db_team += f'{{ "id":"{val}", "name":"{db_dat.name}","types":{db_dat.types},"sprite_url":"{db_dat.sprite_url}", "create_time":{db_dat.create_time} }},'
                                                    added = True

                                                if(added):
                                                    saved_team = saved_team[0:-1]
                                                    db_team = db_team[0:-1]

                                                saved_team += "]"
                                                db_team += "]"
                                                saved_team = saved_team.replace("'",'"')
                                                db_team = db_team.replace("'",'"')
                                                ws.send(f'{{ "status":200, "responding":"load_teams", "info":{{"name":"{name}", "team":{saved_team}, "db_team":{db_team} }} }}')
                                                
                                                    
                                            else:
                                                ws.send('{"status":404, "responding":"load_teams", "info":{"text":"Unkown Team"}}')
                                
                        elif(msg["action"] == "save_team"):
                            user = msg["user"]
                            if(ws in self.logged_in_users):
                                if(self.logged_in_users[ws] == user):
                                    print("[SAVE TEAM]")
                                    if(user not in self.user_db):
                                        ws.send('{"status":404, "responding":"save_team", "info":{"text":"Unregister User"}}')
                                            
                                    else:
                                        team = {}
                                        failed = False
                                        for val in msg["pokemon"]:
                                            if val in pokemon_db:
                                                team[val] = copy.deepcopy(pokemon_db[val])
                                            else:
                                                ws.send('{"status":404, "responding":"save_team", "info":{"text":"Unknown Pokemon"}}')
                                                failed = True
                                                break
                                            if(failed):
                                                break
                                            self.user_db[user].teams[msg["name"]] = team
                                            ws.send('{"status":200, "responding":"save_team", "info":{"text":"success"}}')
                                        
                                else:
                                    ws.send('{"status":404, "responding":"save_team", "info":{"text":"Cannot save team under differen user"}}')
                            else:
                                ws.send('{"status":404, "responding":"save_team", "info":{"text":"Not logged in"}}')
                        elif(msg["action"] == "delete_team"):
                            user = msg["user"]
                            if(ws in self.logged_in_users):
                                if(self.logged_in_users[ws] == user):
                                    print("[DELETE TEAM]")
                                    if(user not in self.user_db):
                                        ws.send('{"status":404, "responding":"delete_team", "info":{"text":"Unregister User"}}')
                                    else:
                                        self.user_db[user].teams.pop(msg["name"])
                                        ws.send('{"status":200, "responding":"delete_team", "info":{"text":"success"}}')

                        elif(msg["action"] == "modify_pokemon"):
                            user = msg["user"]
                            if(ws in self.logged_in_users):
                                if(self.logged_in_users[ws] == user):
                                    if(user == "admin"):
                                        print("[MODIFY POKEMON]")
                                        pokemon_db[msg["id"]].name = msg["name"]
                                        pokemon_db[msg["id"]].types = msg["types"]
                                        pokemon_db[msg["id"]].create_time = time.time()
                                        ws.send('{"status":200, "responding":"modify_pokemon", "info":{"text":"success"}}')
                                    else:
                                        ws.send('{"status":404, "responding":"modify_pokemon", "info":{"text":"Can only Modify as Admin"}}')

                                                                
                        elif(msg["action"] == "counter_team"):
                            user = msg["user"]
                            if(ws in self.logged_in_users):
                                if(self.logged_in_users[ws] == user):
                                    if(msg["name"] in self.user_db[user].teams):
                                        team = self.user_db[user].teams[msg["name"]]
                                        global weaknesses_def_to_atk
                                        counter_team = '['
                                        added = False
                                        counters_ids = []
                                        for val in team:
                                            types = team[val].types

                                            current_counter_id = 1
                                            current_counter_mod = 0
                                            found_max = False
                                            for pk in pokemon_db:
                                                pokemon_dat = pokemon_db[pk]
                                                counter_types = pokemon_dat.types
                                                
                                                for atk_type in counter_types:
                                                    atk_mod = 1
                                                    for defense_type in types:
                                                        weak = weaknesses_def_to_atk[defense_type]
                                                        atk_mod = weak[atk_type] * atk_mod
                                                        
                                                    if(atk_mod >= 4 and pokemon_dat.id_num not in counters_ids):
                                                        current_counter_id = pokemon_dat.id_num
                                                        current_counter_mod = atk_mod
                                                        found_max = True
                                                        break
                                                    elif(atk_mod > current_counter_id and pokemon_dat.id_num not in counters_ids):
                                                        current_counter_id = pokemon_dat.id_num
                                                        current_counter_mod = atk_mod
                                                        
                                                if(found_max):
                                                    break

                                            db_dat = pokemon_db[current_counter_id]
                                            counter_team += f'{{ "id":"{current_counter_id}", "name":"{db_dat.name}","types":{db_dat.types},"sprite_url":"{db_dat.sprite_url}", "create_time":{db_dat.create_time} }},'
                                            added = True
                                            counters_ids.append(current_counter_id)
                                            
                                        if(added):
                                            counter_team = counter_team[0:-1]
                                        counter_team += "]"
                                        counter_team = counter_team.replace("'",'"')
                                        ws.send(f'{{ "status":200, "responding":"counter_team", "info":{{ "team":{counter_team} }} }}')
                                                             
                                                    
                                                    
                                                        
                                                
                                                                 
                                    else:
                                        ws.send('{"status":404, "responding":"counter_team", "info":{"text":"Team does not exist"}}')
                                else:
                                    ws.send('{"status":404, "responding":"counter_team", "info":{"text":"User not currently logged in"}}')
                            else:
                                ws.send('{"status":404, "responding":"counter_team", "info":{"text":"Not Logged In"}}')
                                    
                        else:
                            print("[UNKNOWN ACTION]" + msg["action"])
                            
                except Exception as e:
                    print(f"[INVALID MESSAGE] {e}")
                
        except Exception as e:
            print(f"[SERVER] Error: {e}")
        finally:
            print(f"[SERVER] Connection closed {remote_addr}")

    def start(self):
        print("[SERVER] Starting WebSocket server on ws://localhost:8765...")
        self.server.serve_forever()

    def __init__(self, user_db):
        self.stop = False
        self.user_db_filename = user_db
        self.user_db = {}
        self.logged_in_users = {}
 
        if(os.path.isfile(self.user_db_filename)):
            with open(self.user_db_filename, 'rb') as file:
                self.user_db = pickle.load(file)

        print("[LOADED] " + str(len(self.user_db)) + " users") 
        for val in self.user_db:
            print(self.user_db[val])
        
        self.server = serve(self.client_handler, "localhost", 8765)

    def shutdown(self):
        self.stop = True
        self.server.shutdown()
        with open(self.user_db_filename, "wb") as file:
            pickle.dump(self.user_db, file)



if __name__ == "__main__":
    config = {
        "pokemon_db":"pokemon.pkl",
        "user_data_db":"users.pkl"
    }


    
    try:
        _server = APIServer( config["user_data_db"])
        _server_thread = Thread(target = _server.start)
        _server_thread.daemon = True

        _scraper = PokemonScraper(config["pokemon_db"])
        _scraper_thread = Thread(target = _scraper.start)
        _scraper_thread.daemon = True

        def signal_handler(sig, frame):
            print("Server Shutting Down")
            _server.shutdown()
            _server_thread.join()
            _scraper.shutdown()
            _scraper_thread.join()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


        _scraper_thread.start()
        time.sleep(0.5)        
        _server_thread.start()

        

        
        while True:
            _scraper_thread.join(0.1)
            _server_thread.join(0.1)

            if(not _server_thread.is_alive() and not _scraper_thread.is_alive()):
                break
            
    except KeyboardInterrupt:
        _scraper.shutdown()
        _scraper_thread.join()
        _server.shutdown()
        _server_thread.join()
    finally:
        print("[INTERRUPT]")
    
