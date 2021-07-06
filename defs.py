import sys
import requests
import fake_useragent
from PIL import Image
from mss import mss
import numpy as np
from time import sleep, time
import pyautogui, keyboard, cv2
import pytesseract
import win32api
import win32con
import telebot
from math import radians, cos, sin, asin, sqrt
from config import TOKEN


tb = telebot.TeleBot(TOKEN)
user_agent = fake_useragent.UserAgent()['google chrome']
headers = {'user-agent': user_agent, 'if-none-match': "2979-3kcziSj429jfGMhljZ/o5eCq/7E", 'referer': 'https://sgpokemap.com/', 'authority': 'sgpokemap.com', 'x-requested-with': 'XMLHttpRequest'}
url = 'https://sgpokemap.com/query2.php?mons=554&time=0&since=0'
needed, already = [24, 25, 12, 13, 16, 17], []
prev = None


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, (lon1, lat1, lon2, lat2))

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def get_attrs(global_time: int, latitude, longitude, distance=None):
    minutes = global_time // 60
    seconds = '0' + str(global_time % 60) if global_time % 60 < 10 else global_time % 60
    coordinates = f'pk.md/{latitude},{longitude}'
    if distance != None:
        distance = toFixed(distance, 2)
        return (minutes, seconds, coordinates, distance)
    
    return (minutes, seconds, coordinates)


def get_poke():
    global prev
    cords = []
    ans = []
    data = requests.get(url=url, headers=headers).json()
    
    for i in range(len(data['pokemons'])):
        despawn_time = int(data['pokemons'][i]['despawn'])
        current_time = data['meta']['inserted']
        latitude = data['pokemons'][i]['lat']
        longitude = data['pokemons'][i]['lng']

        if despawn_time - current_time > 300 and (latitude, longitude) not in already:
            cords.append((latitude, longitude, despawn_time - current_time))

    if prev == None:
        mins, secs, coordinates = get_attrs(cords[0][2], cords[0][0], cords[0][1])

        tb.send_message(-1001520242396, f'Start Point\nDarumaka✨✨✨\nDespawn in {mins}:{secs}\n{coordinates}', disable_web_page_preview=True)

        already.append((cords[0][0], cords[0][1]))
        prev = (float(cords[0][0]), float(cords[0][1]))
    else:
        for i in cords:
            dist = haversine(prev[0], prev[1], float(i[0]), float(i[1]))
            ans.append([dist, (i[0], i[1]), i[2]])
            
        ans.sort(key=lambda x: x[0])
        ans = ans[:1][0]

        mins, secs, coordinates, dist = get_attrs(ans[2], ans[1][0], ans[1][1], ans[0])

        already.append((ans[1][0], ans[1][1]))

        tb.send_message(-1001520242396, f'Darumaka✨✨✨\nDespawn in {mins}:{secs}\n{coordinates}\nDistance from previous pokemon - {dist}km', disable_web_page_preview=True)
        prev = (float(ans[1][0]), float(ans[1][1]))


def main():
    start = time()
    while True:
        end = time()
        if end - start > 20:
            get_poke()
            start = time()