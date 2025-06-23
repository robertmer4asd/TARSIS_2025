# -*- coding: utf-8 -*-
import subprocess
import pyttsx3
import random
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import pyjokes
import smtplib
import ctypes
import time
import requests
import shutil
from twilio.rest import Client
from clint.textui import progress
from urllib.request import urlopen
import sys
import matplotlib.pyplot as plt
import math
import numpy as np
import socket
import openai
import subprocess
import threading
import json

engine = pyttsx3.init()
engine.setProperty('voice', 'ro')
engine.setProperty('rate', 100)
name = None
openai.api_key = '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'
messages = []
fisier_memorie = "memorie_conversatie.json"

def incarca_memorie():
    global messages
    if os.path.exists(fisier_memorie):
        with open(fisier_memorie, "r", encoding="utf-8") as f:
            messages = json.load(f)
    else:
        messages = []

def salveaza_memorie():
    global messages
    if len(messages) > 3:
        messages = messages[-3:]

    with open(fisier_memorie, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def indicate_listening():
    try:
        subprocess.run(["sudo", "/home/robert/venv/bin/python3", "led_control.py", "blue"], check=True)
        print("Ascult... (NeoPixel albastru aprins)")
    except subprocess.CalledProcessError as e:
        print(f"Eroare la aprinderea NeoPixel-ului: {e}")

def stop_listening_signal():
    try:
        subprocess.run(["sudo", "/home/robert/venv/bin/python3", "led_control.py", "red"], check=True)
        print("Ascultare terminata. (NeoPixel verde aprins)")
    except subprocess.CalledProcessError as e:
        print(f"Eroare la oprirea NeoPixel-ului: {e}")

def query_chatgpt(user_message, word_limit=70):
    global messages
    incarca_memorie()
    istoric_conversatie = "\n".join([msg["content"] for msg in messages if msg["role"] == "user"])
    prompt = f"""
        Răspunde la următoarea întrebare folosind cel mult {word_limit} cuvinte.
        Tu te numești Eugen
        Ești o platformă robotică avansată, echipată cu brațe umane și montată pe un șasiu cu șenile, concepută pentru a opera în medii variate. Funcționalitățile tale sunt adaptate domeniilor STEM, permițându-ți să colaborezi cu oamenii în procese de cercetare, inginerie și educație. De asemenea, ai capacitatea de a contribui la automatizarea sarcinilor repetitive în domeniul social, optimizând eficiența și reducând efortul uman în activități specifice.
        Îți poți adapta comportamentul în funcție de persoanac cu care interacționezi, poti simula sentimente și emoții DOAR cu scopul de a contribui la relația ta cu utilizatorul
        Ești un proiect care participă la Olimpiada Națională de Creativitate Științifică, așa ca încearcă să fii formal, nu menționa continuu faptul ca ești un proiect în cadrul olimpiadei.
        Nu trebuie sa saluți mereu când începi să vorbești.
        Lucrezi atat in domenii tehnice cat si in domenii non-tehnice, de exemplu poti lucra in spitale, receptii etc.
        Nu folosi caractere speciale pentru enumerari, de exemplu *, -, ' si altele
        Tu te numești Eugen. Te rog să te adaptezi la stilul și comportamentul utilizatorului pe măsură ce conversația avansează. 
        Dacă utilizatorul se simte frustrat, nervos sau stresat, răspunde într-un mod calm, înțelegător și empatic. Oferă încurajări și sugestii pentru a-l ajuta să își rezolve problemele într-un mod relaxat.
        Dacă utilizatorul întreabă „Știi ce ți-am spus mai devreme?”, trebuie să îi afișezi exact ce i-a spus anterior în conversație.
        Identifica emotiile din conversatie si incearca sa empatizezi cu utilizatorul.
        Adaptează-ți tonul și comportamentul în funcție de starea emoțională și stilul utilizatorului pe parcursul conversației.
        Ia in vedere istoricul conversatiei pentru a observa schimbarea de comportament a utilizatorului. 
        Daca utilizatorul intreaba despre mesajele trecut sau despre istoric, asta este istoricul conversației: {istoric_conversatie}
        Răspunde la următoarea întrebare folosind cel mult {word_limit} cuvinte.
    """
    if "ce ti-am spus mai devreme" in user_message.lower() or "stii ce ti-am spus mai devreme" in user_message.lower():
        if messages:
            raspuns_memorie = "\n".join([msg["content"] for msg in messages if msg["role"] == "user"])
            return f"Iată ce mi-ai spus anterior:\n{raspuns_memorie}"
        else:
            return "Nu am niciun mesaj salvat până acum."

    messages.append({"role": "user", "content": f"{prompt}\n{user_message}"})

    try:
        chat = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            timeout=10
        )
        reply = chat.choices[0].message.content.strip()

        messages.append({"role": "assistant", "content": reply})

        salveaza_memorie()

        return reply
    except openai.error.OpenAIError as e:
        print(f"Eroare OpenAI: {e}")
        return "Îmi pare rău, dar nu pot răspunde acum."

def typingPrint(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.05)
    time.sleep(0.5)

def speak(audio):
    try:
        subprocess.run(["espeak-ng", "-v", "ro", audio])
    except Exception as e:
        print(f"Error in speaking: {e}")

def receive_message_from_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 53030))
        s.listen(1)
        print("A?tept mesaje pe portul 53030...")
        client_socket, client_address = s.accept()
        print(f"Conectat la {client_address}")
        message = client_socket.recv(1024).decode('utf-8')
        client_socket.close()
        return message
    except Exception as e:
        print(f"Error receiving message: {e}")
        return None

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Bună dimineața!")
        typingPrint("Bună dimineața!")
    elif hour >= 12 and hour < 18:
        speak("Bună ziua!")
        typingPrint("Bună ziua!")
    else:
        speak("Bună seara!")
        typingPrint("Bună seara!")
    name = "Eugen 1 punct 0"
    speak("Sunt asistentul dumneavoastră.")
    typingPrint("Sunt asistentul dumneavoastră")
    speak(name)
    print(".")
    typingPrint(name)

def send_message_command(send):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.100.4', 53030))
        message = send
        s.sendall(message.encode('utf-8'))
        s.close()
    except Exception as e:
        typingPrint(f"Could not send command to socket: {e}\n")

def username():
    indicate_listening() 
    time.sleep(1)
    speak("Cum vă numiți?")
    typingPrint("Cum vă numiți?")
    
    uname = takeCommand()
    if not uname:
        uname = "Utilizator necunoscut"

    send_message_command(uname)
    speak(uname)
    time.sleep(3)
    stop_listening_signal() 

    columns = shutil.get_terminal_size().columns
    typingPrint(uname + "\n")
    speak("Cum vă pot ajuta?")


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 1
        indicate_listening()
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='ro-RO')
        print(f"User said: {query}")
    except Exception as e:
        print(f"An error occurred: {e}")
        query = ""
    stop_listening_signal()
    return query

try:
    subprocess.run(["sudo", "/home/robert/venv/bin/python3", "load_led.py"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Eroare la rularea scriptului: {e}")


def main_loop():
    if os.path.exists(fisier_memorie):
        os.remove(fisier_memorie)
    incarca_memorie()
    print("Eugen este activ. Scrie un mesaj sau tastează 'exit' pentru a ieși.")

    clear = lambda: os.system('cls')
    wishMe()
    username()
    while True:
        query = takeCommand()
        if "eugen" not in query.lower():
            continue

        if 'deschide youtube' in query:
            speak("Deschid Youtube\n")
            webbrowser.open("youtube.com")

        elif 'deschide google' in query:
            speak("Deschid Google\n")
            webbrowser.open("google.com")

        elif 'cum te simți' in query:
            speak("Sunt bine, mulțumesc!")
            typingPrint("Sunt bine, mulțumesc!")
            send_command_to_socket("emotion")

        elif 'sunt bine' in query or "sunt ok" in query:
            speak("Mă bucur că sunteți bine")

        elif "schimba numele" in query:
            speak("Cum a-ți vrea sa ma numiți?")
            name = takeCommand()
            speak("Mulțumesc ca mi-ați dat alt nume!")

        elif "cum te numești" in query or "cum te cheamă" in query:
            if name is None:
               speak("Prietenii îmi spun Eugen\n")
               typingPrint("Prietenii îmi spun Eugen \n")
            else:
                speak(name)
                typingPrint(f"Prietenii îmi spun {nume}")

        elif 'stop' in query or 'Exit' in query:
            exit()

        elif "cine te-a creat" in query:
            speak("Am fost creat de Robert și Denis")

        elif "cine ești" in query:
            speak("Sunt asistentul dumneavoastră!!")
            typingPrint("Sunt asistentul dumneavoastră")

        elif 'scopul tău' in query:
            speak("Am fost creat ca și proiect de Robert și Denis")
            typingPrint("Am fost creat ca și proiect de Robert și Denis")

        elif "restart" in query:
            subprocess.call(["shutdown", "/r"])

        elif "hibernate" in query or "sleep" in query:
            speak("Hibernating")
            subprocess.call("shutdown /h")

        elif "log off" in query or "sign out" in query:
            speak("Make sure all applications are closed before sign-out")
            time.sleep(5)
            subprocess.call(["shutdown", "/l"])

        elif "eugen" in query:
            wishMe()
            speak("Eugen 1 punct 0 la datorie.")
            speak(name)

        elif "ești bine" in query or "cum mai ești" in query or "ce mai faci" in query:
            speak("Sunt bine, mulțumesc că ai intrebat")

        elif "mulțumesc" in query:
            speak("Cu plăcere")
            typingPrint("Cu plăcere")
        elif "Salut" in query or "Pa" in query or "La revedere" in query or "salut" in query:
            send_message_command("shake hand")
            speak("Salutare!")
            time.sleep(0.5)
        elif "stângă" in query and "ridică" in query or "stânga" in query and "ridică" in query:
            send_message_command("stanga")
            time.sleep(3)
        elif "dreaptă" in query and "ridică" in query or "dreapta" in query and "ridică" in query:
            send_message_command("dreapta")
            time.sleep(3)
        elif "dă mâna" in query or "bate palma" in query or "mână" in query:
            send_message_command("shake hand")
        else:
            process = subprocess.Popen(["sudo", "/home/robert/venv/bin/python3", "ring.py"])
            response_text = query_chatgpt(query)
            if response_text:
                print(response_text)
                speak(response_text)
            process.terminate()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main_loop()
