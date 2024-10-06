# Main audio controller: DOES NOT HANDLE VISUALISER
# will manage logging, IP, settings

import tkinter
import tkinter.messagebox
import customtkinter
from utils import utilities
from audio import audio
import asyncio
import threading
from screenAnalysis import screenAnalyse

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"



# MAIN WINDOW
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # configure window
        self.title("LED CONTROLLER V1")
        self.geometry(f"{500}x{500}")
        self.resizable(False, False)

        self.mode = 1
        self.AUDIOMODE = 0 # 0 = party, 1 = screen
        self.LIGHTMODE = 1 # 0 = soft (lofi, chill), 1 = Mid (basic rap), 2 = Hard (Hardstyle, phonk, etc.)

        #GUI
        self.frame = customtkinter.CTkFrame(self, width=450, height=450)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        Title = customtkinter.CTkLabel(self.frame, text="LED CONTROLLER", font=customtkinter.CTkFont(size=20, weight="bold"))
        Title.pack(padx=20, pady=20, side="top")

        self.seg_button_1 = customtkinter.CTkSegmentedButton(self.frame, command=self.changeMode)
        self.seg_button_1.pack(padx=20, pady=20, fill="x", side="top")



        s = customtkinter.CTkLabel(self.frame, text="Sensitivity", font=customtkinter.CTkFont(size=15, weight="bold"))
        s.pack(padx=20, pady=(20,0), side="top")



        self.slider_1 = customtkinter.CTkSlider(self.frame, from_=0, to=2, number_of_steps=10, command=self.updateSv)
        self.slider_1.pack(padx=20, pady=20, fill="x", side="top")
        #self.slider_1.configure(state="disabled")

        s2 = customtkinter.CTkLabel(self.frame, text="Light Mode", font=customtkinter.CTkFont(size=15, weight="bold"))
        s2.pack(padx=20, pady=(20,0), side="top")
        self.seg_button_2 = customtkinter.CTkSegmentedButton(self.frame, command=self.changeLight)
        self.seg_button_2.pack(padx=20, pady=20, fill="x", side="top")

        self.seg_button_2.configure(values=["Soft", "Mid", "Hard"])
        self.seg_button_2.set("Mid")
        self.seg_button_2.configure(state="disabled")

        self.setBTN = customtkinter.CTkButton(self.frame, text="STOP", command=self.Apply)
        self.setBTN.pack(padx=20, pady=20, fill="x", side="bottom")
        self.seg_button_1.configure(values=["Party Mode", "Movie Mode"])
        self.seg_button_1.set("Party Mode")
        self.seg_button_1.configure(state="disabled")


        self.progressbar_1 = customtkinter.CTkProgressBar(self.frame)
        self.progressbar_1.pack(padx=20, pady=0, fill="x", side="bottom")
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()

        

        u = utilities.Utils()
        creds = u.creds()
        self.Audio = audio.Audio([creds["user"], creds["pass"], creds["IP"]], s=(float(self.slider_1.get())), m=self.LIGHTMODE)
        self.screen = screenAnalyse.screen([creds["user"], creds["pass"], creds["IP"]], s=(float(self.slider_1.get())))
        #self.v = visualizer.Visualizer()
        self.T1 = None
        self.create()

    def changeMode(self, event):
        s = self.seg_button_1.get()
        if s == "Party Mode":
            self.AUDIOMODE = 0
        elif s == "Movie Mode":
            self.AUDIOMODE = 1

    def changeLight(self, event):
        s = self.seg_button_2.get()
        if s == "Soft":
            self.LIGHTMODE = 0
        elif s == "Mid":
            self.LIGHTMODE = 1
        elif s == "Hard":
            self.LIGHTMODE = 2

    def updateSv(self, event):
        if self.mode == 0:
            return
        s = (float(self.slider_1.get()))
        #print(s)
        if self.AUDIOMODE == 0:
            self.Audio.updateS(s, self.LIGHTMODE)
        elif self.AUDIOMODE == 1: # movie
            self.screen.updateS(s)

    def create(self):
        # start audio
        if self.AUDIOMODE == 0: # start party
            self.T1 = threading.Thread(target=asyncio.run, args=[self.Audio.start()])
            s = (float(self.slider_1.get()))
            self.Audio.updateS(s, self.LIGHTMODE) 
        elif self.AUDIOMODE == 1: # start movie
            self.T1 = threading.Thread(target=asyncio.run, args=[self.screen.start()])
            s = (float(self.slider_1.get()))
            self.screen.updateS(s)    
        
        self.T1.start()



    def stop(self):

        if self.AUDIOMODE == 0:
            self.Audio.close()
        elif self.AUDIOMODE == 1:
            self.screen.close()
        #self.v.close()

        if self.mode == 0:
            return
        self.T1.join(timeout=1)
        self.T1 = None
    
    def Apply(self): # pressed the button (pause)
        if self.mode == 1: # stop
            self.setBTN.configure(text="START")
            
            self.progressbar_1.stop()
            
            self.progressbar_1.configure(mode="determinate")
            self.progressbar_1.set(100)
            self.seg_button_1.configure(state="enabled")
            self.seg_button_2.configure(state="enabled")

            self.stop()
            self.mode = 0
            
        else: # start
            self.setBTN.configure(text="STOP")
            self.progressbar_1.configure(mode="indeterminnate")
            self.progressbar_1.start()
            self.seg_button_1.configure(state="disabled")
            self.seg_button_2.configure(state="disabled")
            self.mode = 1
            self.create()


if __name__ == "__main__":

    

    app = App()

    def close():
        app.stop()
        app.destroy()
    app.protocol("WM_DELETE_WINDOW", close)
    app.mainloop()
    #app.create()