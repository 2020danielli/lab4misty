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

        self.textbox = tk.Entry(self.text_frame, width=50, font=("Ariel",10))
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
        msg1_text = "Hi I am Misty!"
        self.message1a = tk.Button(self.buttonframe, wraplength=300, text=msg1_text, font=("Ariel",10), bg="yellow", 
                                  command=lambda m=msg1_text: self.speech_button(m))
        self.message1a.grid(row=1, column=0, sticky=tk.W+tk.E)

        # Pre-scripted Message 2
        msg2_text = "How are you doing today?"
        self.message2a = tk.Button(self.buttonframe, wraplength=300, text=msg2_text, font=("Ariel",10), bg="yellow", 
                                  command=lambda m=msg2_text: self.speech_button(m))
        self.message2a.grid(row=1, column=1, sticky=tk.W+tk.E)

        # Three Good Things Introduction
        intro_text = "Today we're going to do the Three Good Things exercise where we'll take turns sharing things we're grateful for."
        self.intro_msg = tk.Button(self.buttonframe, wraplength=300, text=intro_text, font=("Ariel",10), bg="lightblue", 
                                  command=lambda m=intro_text: self.speech_button(m))
        self.intro_msg.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E)
        
        # Robot Disclosure 1
        disclosure1_text = "My first good thing is that it is a sunny day. What's your first good thing?"
        self.disclosure1 = tk.Button(self.buttonframe, wraplength=300, text=disclosure1_text, font=("Ariel",10), bg="lightgreen", 
                                   command=lambda m=disclosure1_text: self.speech_button(m))
        self.disclosure1.grid(row=3, column=0, sticky=tk.W+tk.E)
        
        # Robot Disclosure 2
        disclosure2_text = "My second good thing is that I get to study at UChicago. What's your second good thing?"
        self.disclosure2 = tk.Button(self.buttonframe, wraplength=300, text=disclosure2_text, font=("Ariel",10), bg="lightgreen", 
                                   command=lambda m=disclosure2_text: self.speech_button(m))
        self.disclosure2.grid(row=3, column=1, sticky=tk.W+tk.E)
        
        # Robot Disclosure 3
        disclosure3_text = "My third good thing is that I get to escape the confines of my locker and get to work with you guys. What's your third good thing?"
        self.disclosure3 = tk.Button(self.buttonframe, wraplength=300, text=disclosure3_text, font=("Ariel",10), bg="lightgreen", 
                                   command=lambda m=disclosure3_text: self.speech_button(m))
        self.disclosure3.grid(row=4, column=0, sticky=tk.W+tk.E)
        
        # Conclusion
        conclusion_text = "Thank you for sharing! I enjoyed our conversation today."
        self.conclusion = tk.Button(self.buttonframe, wraplength=300, text=conclusion_text, font=("Ariel",10), bg="lightblue", 
                                  command=lambda m=conclusion_text: self.speech_button(m))
        self.conclusion.grid(row=4, column=1, sticky=tk.W+tk.E)

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

        # Add nonverbal behavior buttons
        self.nod_button = tk.Button(self.topbutton_frame, wraplength=300, text="Nod Head", font=("Ariel",10), command=lambda m="nod_head": self.action(m))
        self.nod_button.grid(row=0, column=1, padx=5, pady=0)
        
        self.surprise_button = tk.Button(self.topbutton_frame, wraplength=300, text="Surprise Reaction", font=("Ariel",10), command=lambda m="surprise_reaction": self.action(m))
        self.surprise_button.grid(row=0, column=2, padx=5, pady=0)
        
        self.happy_button = tk.Button(self.topbutton_frame, wraplength=300, text="Happy Reaction", font=("Ariel",10), command=lambda m="happy_reaction": self.action(m))
        self.happy_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.thinking_button = tk.Button(self.topbutton_frame, wraplength=300, text="Thinking Pose", font=("Ariel",10), command=lambda m="thinking_pose": self.action(m))
        self.thinking_button.grid(row=1, column=1, padx=5, pady=5)

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

        # Implement actions for each button
        if phrase == "move_head_1":
            misty.move_head(-15, 0, 0, 80)
        elif phrase == "nod_head":
            # Nodding motion (up and down)
            misty.move_head(0, 0, 0, 80)  
            time.sleep(1)
            misty.move_head(-40, 0, 0, 80)  
            time.sleep(1)
            misty.move_head(26, 0, 0, 80)  
            time.sleep(1)
            misty.move_head(-40, 0, 0, 80)  
            time.sleep(1)
            misty.move_head(26, 0, 0, 80)  
            time.sleep(1)
            misty.move_head(0, 0, 0, 80)  
        elif phrase == "surprise_reaction":
            # Surprise reaction (arms up, LED change, expression change)
            misty.change_led(255, 0, 255)  
            misty.move_arms(10, 10, 90, 90)  
            time.sleep(0.5)
            misty.display_image("e_Surprise.jpg")  
        elif phrase == "happy_reaction":
            # Happy reaction (LED green, arms wave, expression change)
            misty.change_led(0, 255, 0) 
            misty.display_image("e_Joy.jpg") 
            misty.move_arms(-30, 30, 90, 90) 
            time.sleep(0.5) 
        elif phrase == "thinking_pose":
            # Thinking pose (head tilt, LED blue, expression change)
            misty.change_led(0, 0, 255)  
            misty.move_head(0, 20, 15, 80)  
            time.sleep(0.5)
            misty.display_image("e_Contemplate.jpg")  

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
