import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.audio import SoundLoader
import cv2
import numpy as np
import time
import os

# --- CONFIGURATION ---
SENSITIVITY = 15000 
ALARM_SOUND = "alarm.wav" 

class GuardianApp(App):
    def build(self):
        # The main layout
        self.layout = BoxLayout(orientation='vertical')
        
        # The Camera (0 is the back camera)
        self.camera = Camera(play=True, resolution=(640, 480))
        self.layout.add_widget(self.camera)
        
        # Status Label
        self.status_label = Label(text="Guardian Active. Watching...", size_hint_y=0.1)
        self.layout.add_widget(self.status_label)
        
        # Setup OpenCV background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=100, detectShadows=False)
        
        # Setup Alarm Sound
        self.alarm = SoundLoader.load(ALARM_SOUND)
        if not self.alarm:
            print("Warning: alarm.wav not found.")
            
        self.alarm_playing = False
        self.last_capture = 0
        
        # Schedule the motion detection to run 10 times a second
        Clock.schedule_interval(self.detect_motion, 0.1)
        return self.layout

    def detect_motion(self, dt):
        # Get the current frame from the Kivy camera
        if not self.camera.texture:
            return

        # Convert Kivy texture to a numpy array for OpenCV
        texture = self.camera.texture
        size = texture.size
        pixels = texture.pixels
        
        # Convert RGBA to RGB
        frame = np.frombuffer(pixels, dtype=np.uint8).reshape(size[1], size[0], 4)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        
        # --- YOUR MOTION DETECTION LOGIC ---
        fg_mask = self.bg_subtractor.apply(frame)
        kernel = np.ones((5,5), np.uint8)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > SENSITIVITY:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h
                if 0.2 < aspect_ratio < 1.5: 
                    motion_detected = True
                    break 

        # --- ALARM & CAPTURE LOGIC ---
        if motion_detected:
            self.status_label.text = "🚨 INTRUDER DETECTED! 🚨"
            self.status_label.color = (1, 0, 0, 1) # Red
            
            if not self.alarm_playing and self.alarm:
                self.alarm.play()
                self.alarm_playing = True
                
            current_time = time.time()
            if current_time - self.last_capture > 3:
                # Save the image to Android storage
                folder = "/sdcard/guardian_intruders"
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"{folder}/intruder_{timestamp}.jpg"
                
                # OpenCV expects BGR for saving
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filename, bgr_frame)
                print(f"Saved: {filename}")
                self.last_capture = current_time
                
        else:
            self.status_label.text = "Guardian Active. Watching..."
            self.status_label.color = (1, 1, 1, 1) # White
            if self.alarm_playing and self.alarm:
                self.alarm.stop()
                self.alarm_playing = False

if __name__ == '__main__':
    GuardianApp().run()