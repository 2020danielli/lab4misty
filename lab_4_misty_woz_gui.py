#How to run this file: python3 lab_4_misty_woz_gui.py [misty ip address]
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import websocket
import sys, os, time
###This part could be different for everyone###
sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'Python-SDK'))
# sys.path.append(os.path.join(os.path.dirname(__file__), 'Python-SDK'))
###This part could be different for everyone###
from mistyPy.Robot import Robot
from mistyPy.Events import Events

class MistyGUI:
    def __init__(self):

        # Creates the window for the tkinter interface
        self.root = tk.Tk()
        self.root.geometry("900x900")
        self.root.title("Misty GUI")

        # Section 1: Timer

        # Creates a stopwatch at the top of the screen
        self.label = tk.Label(self.root, text="Timer", font=("Ariel",20))
        self.label.pack(padx=20,pady=0)

        # Time variables
        self.time_elapsed = 0
        self.running = False

        self.time_display = tk.Label(self.root, text="0:00", font=("Ariel", 18))
        self.time_display.pack()

        self.timer_frame = tk.Frame(self.root)
        self.timer_frame.pack(padx=10, pady=5)

        self.starttimer_button = tk.Button(self.timer_frame, text="Start", command=self.start)
        self.starttimer_button.grid(row=0, column=0, padx=5, pady=0)

        self.stoptimer_button = tk.Button(self.timer_frame, text="Stop", command=self.stop)
        self.stoptimer_button.grid(row=0, column=2, padx=5, pady=0)

        self.reset_button = tk.Button(self.timer_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=3, padx=5, pady=0)

        self.update_time()

        # Add a line separator
        self.separator = ttk.Separator(self.root, orient='horizontal')
        self.separator.pack(fill='x', pady=20)

        # Section 2: Speech Control
        self.label = tk.Label(self.root, text="Speech Control Panel", font=("Ariel",18))
        self.label.pack(padx=20,pady=0)

        # Add text entry box
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(padx=10, pady=5)

        self.textbox = tk.Entry(self.text_frame, width=100, font=("Ariel",10))
        self.textbox.grid(row=0, column=0, padx=5, pady=0)

        # Add speak button
        self.speak_button = tk.Button(self.text_frame, wraplength=300, text="Speak", font=("Ariel",10), command=lambda: self.speak(self.textbox.get()))
        self.speak_button.grid(row=0, column=1, padx=5, pady=0)

        # Add clear button to clear the text in text entry box
        self.erase_button = tk.Button(self.text_frame, wraplength=300, text="Clear", font=("Ariel",10), command=self.text_erase)
        self.erase_button.grid(row=0, column=2, padx=5, pady=0)

        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)

        # Pre-scripted Message 1
        self.message1a = tk.Button(self.buttonframe, wraplength=300, text="Hi I am Misty!", font=("Ariel",10), bg="yellow", command=lambda m="Hi I am Misty!": self.speech_button(m))
        self.message1a.grid(row=1, column=0, sticky=tk.W+tk.E)

        # Pre-scripted Message 2
        self.message2a = tk.Button(self.buttonframe, wraplength=300, text="How are you doing today?", font=("Ariel",10), bg="yellow", command=lambda m="How are you doing today?": self.speech_button(m))
        self.message2a.grid(row=1, column=1, sticky=tk.W+tk.E)

        #TODO: Add more pre-scripted message buttons or other customized buttons for speech control panel

        self.buttonframe.pack(fill='x')

        # Add a line separator
        self.separator = ttk.Separator(self.root, orient='horizontal')
        self.separator.pack(fill='x', pady=20)

        # Section 3: Action Control
        self.label = tk.Label(self.root, text="Action Control Panel", font=("Ariel",18))
        self.label.pack(padx=20,pady=0)

        self.topbutton_frame = tk.Frame(self.root)
        self.topbutton_frame.pack(padx=10, pady=0)

        self.move_head_button = tk.Button(self.topbutton_frame, wraplength=300, text="Move Head 1", font=("Ariel",10), command=lambda m="move_head_1": self.action(m))
        self.move_head_button.grid(row=0, column=0, padx=5, pady=0)

        #TODO: Add more customized buttons to drive misty, play audio, move arms, change led lights, change displayed image, and etc.

        # Add a line separator
        self.separator = ttk.Separator(self.root, orient='horizontal')
        self.separator.pack(fill='x', pady=20)

        # Section 4: Video Stream
        self.label = tk.Label(self.root, text="Live Video Stream (No Audio)", font=("Ariel", 18))
        self.label.pack(padx=20, pady=10)

        # Add a placeholder for video streaming
        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        # Start stream
        self.start_video_stream()

        self.root.mainloop()

    def speak(self, phrase):
        print(f"Speak: {phrase}")
        # refer to robot commands in RobotCommands.py - https://github.com/MistyCommunity/Python-SDK/blob/main/mistyPy/RobotCommands.py
        # or in the Misty API documentation - https://lessons.mistyrobotics.com/python-elements/misty-python-api
        misty.speak(phrase)

    def action(self, phrase):
        print(f"Action: {phrase}")
        # refer to robot commands in RobotCommands.py - https://github.com/MistyCommunity/Python-SDK/blob/main/mistyPy/RobotCommands.py
        # or in the Misty API documentation - https://lessons.mistyrobotics.com/python-elements/misty-python-api

        # TODO: edit the following action and add 3 more to handle your customized nonverbal behaviors and robot reactions (e.g., surprise)
        if phrase == "move_head_1":
            misty.move_head(-15, 0, 0, 80)

            
    def speech_button(self, phrase):
        self.textbox.insert(0, phrase)

    def text_box(self):
        print(f"Text: {self.textbox.get()}")
        self.textbox.delete(0, tk.END)
        self.reset()

    def text_erase(self):
        self.textbox.delete(0, tk.END)

    def update_time(self):
        if self.running:
            self.time_elapsed += 1
            self.update_display()
            self.root.after(1000, self.update_time)

    def update_display(self):
        minutes = (self.time_elapsed % 3600) // 60
        seconds = self.time_elapsed % 60
        self.time_display.config(text=f"{minutes:01}:{seconds:02}")

    def start(self):
        if not self.running:
            self.running = True
            self.update_time()

    def stop(self):
        self.running = False

    def reset(self):
        self.running = False
        self.time_elapsed = 0
        self.update_display()

    def start_video_stream(self):
        # Make sure misty's camera service is enabled
        response = misty.enable_camera_service()
        print("misty.enable_camera_service response code:", response.status_code) # this should show 200

        # Configure the preferred video stream settings
        # Notice: This port number can be changed video live stream is crashed
        # This port number must be between 1024 and 65535, default is 5678.
        self.video_port = 5680
        try:
            # Start video streaming
            response = misty.start_video_streaming(
                port=self.video_port, 
                rotation=90, 
                width=640, 
                height=480, 
                quality=60, 
                overlay=False
            )
            
            print("misty.start_video_streaming response code:", response.status_code) # this should show 200

        except Exception as e:
            print(f"Error starting video stream: {e}")
        
        # Establish WebSocket connection to stream video data
        video_ws_url = f"ws://{ip_address}:{self.video_port}"
        print(video_ws_url)

        def on_message(ws, message):
            try:
                # Process the incoming message (video frame)
                image = Image.open(BytesIO(message))
                image = image.resize((320, 240))  # Resize as needed
                photo = ImageTk.PhotoImage(image)
                self.video_label.configure(image=photo)
                self.video_label.image = photo  # Keep a reference to the image
            except Exception as e:
                print(f"Error processing video frame: {e}")

        def on_error(ws, error):
            print(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("WebSocket closed")

        def on_open(ws):
            print("WebSocket connection opened")

        # Create a WebSocket app and set up event handlers
        ws_app = websocket.WebSocketApp(
            video_ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # Run the WebSocket app in a separate thread
        ws_thread = threading.Thread(target=ws_app.run_forever, daemon=True)
        ws_thread.start()


# Run the GUI
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python misty_introduction.py <Misty's IP Address>")
        sys.exit(1)

    ip_address = sys.argv[1]
    misty = Robot(ip_address)

    MistyGUI()
