# this one is good for rap, drill, etc.
from tapo import ApiClient
import asyncio
from audio.analyser import analyzer
from utils import utilities
import os

# instantiate analyser class
class Audio:

    def __init__(self, creds, s=1, m = 1):
        self.A = analyzer()
        self.U = utilities.Utils()
        self.c = creds
        self.sensitivity = s # how sensitive our audio is: greater s = greater sensitive
        self.mode = m
        self.tasks = []
        self.quit_event = asyncio.Event()
        self.client = ApiClient(self.c[0], self.c[1]) # creds[2] is type array

        self.BassThreshold = [100000, 300000, 800000]
        self.BassThresholdlower = [50000, 100000, 500000]

        self.FreqThreshold = [5, 10, 20]
        self.FreqDiff = [5, 10, 10]

        self.AmpThreshold = [60, 40, 30]

    
    def close(self):
        print("QUITTING")
        self.quit_event.set()
        for task in self.tasks:
            task.cancel()
        
        self.A.close()
        self.tasks = []
        
        return
    
    def updateS(self, s, m):
        self.sensitivity = s
        self.mode = m

    async def start(self):
        self.A = analyzer()
        self.quit_event = asyncio.Event()
        for i in self.c[2]:
            print(f"IP WORKING = {i}")
            #self.Proc = asyncio.create_task(self.main(i))
            self.tasks.append(asyncio.create_task(self.main(i)))
            
            #self.A.close()

        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            pass
                
    async def main(self, ip):
        print("STARTING")

        try:
            device = await self.client.l900(ip)
            await device.on()
        except:
            return
        
        #value = await device.get_device_info_json()
        #print(value['hue'])
        print(os.path.abspath(os.path.dirname( __file__ ) + "\color.txt"))

        AMPS = [0]
        FREQ = [0]
        BASS = [0]
        Signal = True
        Basses = False

        b = 1 # brightness
        h = 1 # hue
        last = 1 # last frequency



        while not self.quit_event.is_set():
            try:
                amp, freq, bass = self.A.analyse() # get computer audio
                
                AMPS.append(amp * self.sensitivity)
                #AMPS = AMPS[-15:]
                

                # add frequencies
                FREQ.append(freq * self.sensitivity)

                # add basses
                BASS.append(bass * self.sensitivity)
                FREQ = FREQ[-10:]
                AMPS = AMPS[-3:]
                BASS = BASS[-8:]

                #print(self.U.avg(FREQ))
                # if no signal detected
                if amp >= self.AmpThreshold[self.mode] and Signal:
                    Signal = False
                    if b != 1:
                        await device.set_brightness(1) # toggle 
                        b = 1
                    await device.set_hue_saturation(1, 100) # set to red when silent

                    with open(os.path.abspath(os.path.dirname( __file__ ) + "\color.txt"), "w") as f:
                        #val = await device.get_device_info_json()
                        #print(val['hue'])
                        f.write(str(1))
                        f.flush()


                    print("no signal")
                    continue
                
                # if signal detected
                if Signal == False:
                    if amp < 50:
                        Signal = True
                        if b != 20:
                            await device.set_brightness(20) # turn up colour
                            b = 20
                    else:
                        continue


                # bass detected
                if self.U.avg(BASS) > self.BassThreshold[self.mode] and not Basses:
                    Basses = True
                    if b != 100:
                        await device.set_brightness(100) # turn up the bass (bright)
                        #await device.set_hue_saturation(1, 100)
                        b = 100
                    continue
                elif self.U.avg(BASS) < self.BassThresholdlower[self.mode] and Basses: # bass not detected
                    Basses = False
                    if b != 50:
                        await device.set_brightness(20)  # turn colour down
                        b = 50

                
                # if bass and frequency is low
                # bass isnt quite in sync - i think that is because the last hue went off late. 
                # to fix that i think we can check the current frequency too and if it is quite low we should avoid changing hue?
                #if Basses and avg(FREQ) < 20:
                #    continue
                
                if int(90-self.U.avg(AMPS)) > 6:
                    # interested in higher frequencies
                    if (abs(self.U.avg(FREQ) - last) > self.FreqDiff[self.mode]): # if change in frequency is significant
                        
                        #if avg(FREQ) < 30 and abs(avg(FREQ) - last) > 10: # if we think a bass is coming, do nothing.
                        #    continue
                        last = self.U.avg(FREQ)
                        #print(self.U.avg(FREQ)-20)/(60-20)
                        amount = self.U.clamp(int((self.U.avg(FREQ)-self.FreqThreshold[self.mode])/(60-self.FreqThreshold[self.mode]) * 359 + 1)) # map frequency to colour
                        print(amount) 
                        if h != amount:
                            await device.set_hue_saturation(amount, 100) # set colour 
                            h = amount

                            with open(os.path.abspath(os.path.dirname( __file__ ) + "\color.txt"), "w") as f:
                                #val = await device.get_device_info_json()
                                #print(val['hue'])
                                f.write(str(amount))
                                f.flush()





            except asyncio.CancelledError:
                break  # Exit the loop if cancelled
            

