# code that visualises audio
# Todo: clean up links

# Import and initialize the pygame library
import pygame
from analyser import analyzer
from itertools import repeat
import os
import sys
import time

# Add the project directory to sys.path
current_dir = os.path.dirname(__file__)
project_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_dir)

from utils.utilities import Utils
from utils.spotify import Spotify
from vfx.particles.p1 import Particle 

import threading



class Visualizer:
    def __init__(self):

        
        self.A = analyzer()
        self.U = Utils()
        self.S = Spotify()
        self.BASS = [0]
        self.AMP = [0]
        self.FREQ = [0]
        self.last = 0

        self.interval = 10

        self.out = None
        self.lastSong = ""
        # Run until the user asks to quit
        self.running = True
        self.assets = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets'))
        self.placeholder = self.assets + '\placeholder.jpg'
        self.get_current_track_in_thread(self.on_new_track)
        self.hue = 0
        self.sensitivity = 1

    def get_current_track_in_thread(self, callback):
        def worker():
            while True:
                track = self.S.getinfo()
                if track:
                    callback(track)
                else:
                    print("No song currently playing")

                # Sleep for 5 seconds before checking again
                time.sleep(5)

        # Start a new thread to run the API calls in the background
        thread = threading.Thread(target=worker)
        thread.daemon = True  # Ensures the thread will close when the main program exits
        thread.start()

    def on_new_track(self, current_track):
        self.out = current_track
        print(f"Now playing: {self.out[0]} by {self.out[1]}")

    def close(self):
        self.running = False
        # Done! Time to quit.
        pygame.quit()

    def draw_circle_with_stroke(self, surface, center, radius_x, radius_y, stroke_width, color, stroke_color):
        # Draw filled ellipse
        rect = pygame.Rect(0, 0, 2 * radius_x, 2 * radius_y)
        pygame.draw.ellipse(surface, color, rect)

        # Draw stroke
        pygame.draw.ellipse(surface, stroke_color, rect, stroke_width)

    def draw_circle_with_stroke2(self, surface, center, radius_x, radius_y, stroke_width, color, stroke_color):
        # Draw filled ellipse
        rect = pygame.Rect(center[0]-radius_x, center[1]-radius_y, 2 * radius_x, 2 * radius_y)
        pygame.draw.ellipse(surface, color, rect)

        # Scale image based on circle radius
        scale_factor = (2 * radius_x) / self.image_rect.width *0.8  # Assuming image width and height are the same
        scaled_image = pygame.transform.scale(self.image, (int(self.image_rect.width * scale_factor), int(self.image_rect.height * scale_factor)))

        # Draw stroke
        pygame.draw.ellipse(surface, stroke_color, rect, int(radius_x/10))

        surface.blit(scaled_image, (surface.get_width() // 2 - scaled_image.get_width() // 2, surface.get_height() // 2 - scaled_image.get_height() // 2))

    def start(self):
        self.running = True
        pygame.init()
        font = pygame.font.Font(self.assets + '\BebasNeue-Regular.ttf', 36)  # None means default font, size 36
        text_color = (255, 255, 255)  # White color
        text_surface = []
        
        
        offset = repeat((0, 0))
        all_particles = pygame.sprite.Group()
        amount = 1
        d = pygame.display.get_num_displays() - 1
        # Set up the drawing window
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, display=d)
        dark_overlay = pygame.Surface((self.screen.get_width(), self.screen.get_width()))
        dark_overlay.set_alpha(180)
        dark_overlay.fill((0, 0, 0)) 


        self.background_image = pygame.image.load(self.placeholder)

        self.background_image = pygame.transform.scale(self.background_image, (self.screen.get_width(), self.screen.get_width()))

        self.screen2 = self.screen.copy()
        self.center = (self.screen.get_width()/2, self.screen.get_height()/2)

        self.image = pygame.image.load(self.assets + '\logo.png')  # Replace 'your_image.png' with the path to your image
        self.image_rect = self.image.get_rect()

        while self.running:

            amp, freq, bass = self.A.analyse() # get computer audio
            self.BASS.append(int(bass/1000))
            self.AMP.append(amp)
            self.FREQ.append(freq)
            self.BASS = self.BASS[-8:]
            self.AMP = self.AMP[-3:]
            self.FREQ = self.FREQ[-10:]




            if self.out != None:
                if self.out[0] != self.lastSong:
                    self.lastSong = self.out[0]
                    text_surface = [font.render(self.out[0], True, text_color), font.render(self.out[1], True, text_color)]
                    #img = Image.open(self.out[2])
                    #blurred_image = img.filter(ImageFilter.BoxBlur(5))
                    #blurred_image.save(self.blur)

                    self.background_image = pygame.image.load(self.assets + '\\album.png')
                    self.background_image = pygame.transform.scale(self.background_image, (self.screen.get_width(), self.screen.get_width()))

            #print(int(self.U.avg(self.FREQ)))
            # Did the user click the window close button?
            for event in pygame.event.get():
                if event.type == pygame.QUIT or ((event.type == pygame.KEYDOWN) and event.key == pygame.K_ESCAPE):
                    self.close()

            # Fill the background with black
            self.screen.fill((0, 0, 0))
            self.screen2.fill((0, 0, 0, 0))
            y_position = (self.screen.get_height() - self.screen.get_width()) // 2
            self.screen.blit(self.background_image, (0, y_position))
            self.screen.blit(dark_overlay, (0, 0))
            if text_surface != []:
                text_x = 10  # Small padding from the left edge
                text_y = self.screen.get_height() - text_surface[0].get_height() - 10  # Small padding from the bottom edge
                self.screen.blit(text_surface[1], (text_x, text_y))
                self.screen.blit(text_surface[0], (text_x, text_y - 40))

            #pygame.draw.circle(screen, (225, 0, 0), (250, 250), int(avg(BASS))) 
            
            if self.U.avg(self.AMP) < 60:
                for _ in range(1+ int(self.U.avg(self.BASS)/100)):  # Number of particles to emit per frame
                    particle = Particle(self.center, self.U.hue_to_rgb(amount), int((85-self.U.avg(self.AMP))/5))
                    all_particles.add(particle)

            # Update and draw particles
            all_particles.update()
            for particle in all_particles:
                particle.draw(self.screen) # paint particles on black background


            # red circle
            #screen2.blit(circle_surf(int(avg(BASS)), (255, 0, 0)), (center[0] - int(avg(BASS)), center[1] - int(avg(BASS))), special_flags=pygame.BLEND_RGB_ADD)
            #s = circle_surf(bassDev(BASS) + 20, (225, 0, 0))
            
            # create new surface with screen size
            if self.U.avg(self.BASS) > 10:
                surf = pygame.Surface((self.screen.get_width(), self.screen.get_height()+500))
                # create circle on surface with centre being that of the surface/screen
                w = int(self.U.avg(self.BASS))/2 + self.U.bassDev(self.BASS, False)
                h = int(self.U.avg(self.BASS))/2 + self.U.bassDev(self.BASS, False)
                self.draw_circle_with_stroke(surf, self.center, w, h, 10, (225, 0, 0), (225, 0, 0))
                surf.set_colorkey((0, 0, 0)) 
                self.screen.blit(surf, (self.center[0]-w, self.center[1]-h), special_flags=pygame.BLEND_RGB_ADD) # THIS BLOCKS OUT THE BACKGROUND? i want the circle behind transparent on screen 2

            # Draw a solid blue circle in the center
            if (int(90-self.U.avg(self.AMP)) > 6):
                if abs(self.U.avg(self.FREQ) - self.last) > 10:
                    # new hue
                    self.last = self.U.avg(self.FREQ)
                    #amount = self.U.clamp(int((self.U.avg(self.FREQ)-20)/(60-20) * 359 + 1)) # map frequency to colour
                    amount = self.hue
                
                self.draw_circle_with_stroke2(self.screen2, (self.center), int(90-self.U.avg(self.AMP))*2+ self.U.bassDev(self.AMP, True), int(90-self.U.avg(self.AMP))*2+ self.U.bassDev(self.AMP, True), 10, self.U.hue_to_rgb(amount), (255, 255, 255)) # this i think also inteferes


            if abs(self.BASS[0] - self.BASS[-1]) > 50:
                offset = self.U.shake(abs(self.BASS[0] - self.BASS[-1]))

            # Flip the display
                    
            self.screen2.set_colorkey((0, 0, 0)) 
            #self.screen.blit(background_image, (0, 0))  # (0, 0) is the top-left corner
            self.screen.blit(self.screen2, next(offset))
            pygame.display.flip()



if __name__ == "__main__":
    v = Visualizer()
    v.start()
    