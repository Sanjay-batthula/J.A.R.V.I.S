import os
import re
from shlex import quote
import sqlite3
import struct
import subprocess
import time
import webbrowser
import pyautogui as autogui
from playsound import playsound
import google.generativeai as genai

import eel
import pvporcupine
import pyaudio
import pywhatkit as kit

from engine.command import speak
from engine.config import ASSISTANT_NAME
from engine.helper import extract_yt_term, remove_words

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyCj2IrBCI4IPZqtsIkmdkH7PoM3Mq9Vs7g"
genai.configure(api_key=GOOGLE_API_KEY)

# Updated model name - gemini-pro is deprecated
model = genai.GenerativeModel('gemini-1.5-flash')

def chatbot(query):
    try:
        # Input validation
        if not query or not query.strip():
            raise ValueError("Empty input received")
            
        user_input = query.lower().strip()
        
        # Enhanced prompt with JARVIS personality and context
        system_prompt = (
            f"You are {ASSISTANT_NAME}, an advanced AI assistant created by Sanjay. "
            "Respond in a helpful, slightly witty manner while maintaining professionalism. "
            "Keep responses concise and practical. "
            "When discussing technical topics, provide clear explanations. "
            "User query: "
        )
        
        prompt = system_prompt + user_input
        
        # Generate response with custom parameters
        response = model.generate_content(
            contents=prompt,
            generation_config={
                "temperature": 0.8,  # Slightly more creative
                "max_output_tokens": 1024,
                "top_p": 0.9,
                "top_k": 40
            }
        )
        
        if response and hasattr(response, 'text') and response.text:
            response_text = response.text.strip()
            print("AI Response:", response_text)
            speak(response_text)
            return response_text
        else:
            raise Exception("No valid response generated")
            
    except ValueError as ve:
        error_msg = f"Input Error: {str(ve)}"
        print(error_msg)
        speak("Please provide a valid input")
        return ""
    except Exception as e:
        error_msg = f"AI Error: {str(e)}"
        print(error_msg)
        speak("Sorry, I couldn't process your request")
        return ""

# Function to list available models (for debugging)
def list_available_models():
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"Available model: {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

# Rest of your code remains the same...
con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playassistantsound():
    music_dir = "www/assets/audio/start_sound.mp3"
    playsound(music_dir)

OPENING_MESSAGE = "Opening "
def opencommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":
        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak(OPENING_MESSAGE+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak(OPENING_MESSAGE +query)
                    webbrowser.open(results[0][0])

                else:
                    speak(OPENING_MESSAGE +query)
                    try:
                        os.system(f'start {query}')  
                    except OSError:
                        speak("Application not found")
        except Exception as e:
            speak(f"Something went wrong: {str(e)}")

def playyoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        porcupine = pvporcupine.create(
            access_key="ZNIARtc5NLQpiily58Bta3MBl7kv3IM5hHYWXXNjBf6JNea/yGVQjw==",
            keywords=["jarvis", "alexa"]
        )
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
        
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)
            keyword_index=porcupine.process(keyword)

            if keyword_index>=0:
                print("hotword detected")
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except Exception as e:
        print(f"An error:{str(e)}")
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

def findcontact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    
    except Exception:
        speak('not exist in contacts')
        return 0, 0

def whatsapp(mobile_no, message, flag, name):
    if flag == 'message':
        target_tab = 9
        jarvis_message = "message send successfully to "+name
    elif flag == 'call':
        target_tab = 14
        message = ''
        jarvis_message = "calling to "+name
    else:
        target_tab = 13
        message = ''
        jarvis_message = "staring video call with "+name

    encoded_message = quote(message)
    print(encoded_message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'start "" "{whatsapp_url}"'

    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    autogui.hotkey('ctrl', 'f')

    for _ in range(1, target_tab):
        autogui.hotkey('tab')

    autogui.hotkey('enter')
    speak(jarvis_message)

def makecall(name, mobileno):
    mobileno = mobileno.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileno
    os.system(command)
