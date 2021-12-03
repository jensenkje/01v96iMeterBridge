import sys

import pygame
import pygame.midi
from pygame.locals import *

from spritesheet import load_sprite_sheet_array

class meter_axis():
   def __init__(self,spritemap,position):
       self.spritemap = spritemap
       self.position = position
       self.positionx,self.positiony = self.position
       screen.blit(spritemap[13], (self.positionx,self.positiony))
       screen.blit(spritemap[14], (self.positionx+20,self.positiony))

# Define the WU class
class meter_vu():
   def __init__(self,spritemap,position):
       self.spritemap = spritemap
       self.position = position
       screen.blit(spritemap[0], self.position)
   def name(self,name):
       self.name = name
       x,y = self.position
       self.grouptext = font_vu.render(self.name, False, (255, 255, 255))
       screen.blit(self.grouptext,(x,y+370))
   def update(self,value):
       self.value = value
       screen.blit(self.spritemap[self.value], self.position)

class meter_group():
    def __init__(self,name,number_vu,position,spritemap):
        self.name = name
        self.number_vu = number_vu
        self.positionx,self.positiony = position
        self.meter = []
        self.spritemap = spritemap
        self.grouptext = font_group.render(self.name,False,(255,255,255))
        screen.blit(self.grouptext,(self.positionx,self.positiony+5))
        self.meter = [meter_vu(self.spritemap, (self.positionx+(x*25),self.positiony+30)) for x in range(0,self.number_vu)]
    def convert(self,data):
        i = []
        for x in range(0, self.number_vu):
            i.append(int(data[x * 2]) * 128 + int(data[x * 2 + 1]))
        return i
    def update(self,value):
        #print(self.number_vu)
        # Throw away incomplete data
        if len(value) < self.number_vu*2:
            return
        data = self.convert(value)
        #print(value,data)
        for x in range(0,self.number_vu):
            #print("meter",x,"data",data[x])
            self.meter[x].update(get_segments(data[x]))
    def vuname(self, index, name):
        self.meter[index].name(name)

class fader():
    def __init__(self, spritemap,posx, posy, stereo):
        self.spritemap = spritemap
        self.stereo = stereo
        if self.stereo:
            self.posx = posx
            self.posy = posy
            screen.blit(spritemap[15], (self.posx, self.posy))
            screen.blit(spritemap[15], (self.posx+25, self.posy))
            self.posx = self.posx + 15
        else:
            self.posx = posx
            self.posy = posy
            screen.blit(spritemap[15], (self.posx,self.posy))

class fader_group():
    def __init__(self,name, numfaders, spritemap, startX, startY, stereo=0 ):
        self.startX = startX
        self.startY = startY
        self.endX = startX
        self.endY = startY
        self.stereo = stereo
        self.numfaders = numfaders
        self.spritemap = spritemap
        self.midiId = ""
        self.midiCmd = ""
        self.fader = []

        if self.stereo:
            self.endX = self.startX+(numfaders*50)
            self.fader = [fader(self.spritemap, self.startX + (x * 50), self.startY + 30, stereo=self.stereo) for x in range(0, self.numfaders)]
        else:
            self.fader = [fader(self.spritemap, self.startX + (x * 25), self.startY + 30, stereo=self.stereo) for x in range(0, self.numfaders)]
            self.endX = self.startX+(numfaders*25)

        screen.blit(spritemap[16], (self.endX,self.startY+30))
        screen.blit(spritemap[17], (self.endX+20, self.startY+30))
        self.endX = self.endX + 45

    def set_midiId( s ):
        self.midiId = s

    def set_midiCmd( s ):
        self.midiId = s



# General Setup
pygame.init()

pygame.font.init()
font_group = pygame.font.SysFont('Comic Sans MS', 30)
font_vu = pygame.font.SysFont('Arial', 18)
clock = pygame.time.Clock()
BLACK = (0,0,0)
MIDIME = USEREVENT+1

# Screen Setup
# Insert code here to calculate screen size
screeninfo = pygame.display.Info()
print(screeninfo)
screen_width = screeninfo.current_w
screen_height = screeninfo.current_h


#screen = pygame.display.set_mode((screeninfo.current_w,screeninfo.current_h),pygame.FULLSCREEN)
screen = pygame.display.set_mode((screeninfo.current_w,screeninfo.current_h))
#screen = pygame.display.set_mode((screen_width,screen_height))
#screen = pygame.display.set_mode((3440,1440),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((2560,1440),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1680,1050),pygame.FULLSCREEN)
#VU_SPRITES = load_sprite_sheet_array("VU1.png",13,1,32,360)
VU_SPRITES = load_sprite_sheet_array("VU4.png",18,1,20,355)
#VU_SPRITES2 = load_sprite_sheet_array("VU1.png",13,1,32,360)

fader1 = fader_group("1-16", 16, VU_SPRITES, 0, 700, stereo=0)
fader2 = fader_group("16-32", 16, VU_SPRITES, fader1.endX, 700, stereo=0)
fader3 = fader_group("AUX", 8, VU_SPRITES, fader2.endX, 700, stereo=0)
fader4 = fader_group("BUS", 8, VU_SPRITES, fader3.endX, 700, stereo=0)
fader5 = fader_group("MAIN", 1, VU_SPRITES, fader4.endX, 700, stereo=1)
fader6 = fader_group("ST-IN", 4, VU_SPRITES, fader5.endX, 700, stereo=1 )

# Load and draw the objects of the screen
#meter1 = meter_vu(VU_SPRITES, (50,50))
#meter2 = meter_vu(VU_SPRITES, (200,50))
if screen_width > 500:
    group1 = meter_group("1-16",16,(0,50),VU_SPRITES)
    for x in range(0,16):
        group1.vuname(x,str(x+1))
    meter_axis(VU_SPRITES, (398,80))
if screen_width > 890:
    group2 = meter_group("17-32",16,(445,50),VU_SPRITES)
    for x in range(0,16):
        group2.vuname(x,str(x+17))
    meter_axis(VU_SPRITES, (843,80))
if screen_width > 1288:
    group3 = meter_group("AUX",8,(890,50),VU_SPRITES)
    for x in range(0,8):
        group3.vuname(x,str(x+1))
    meter_axis(VU_SPRITES, (1088, 80))
    group4 = meter_group("BUS",8,(1133,50),VU_SPRITES)
    for x in range(0,8):
        group4.vuname(x,str(x+1))
if screen_width > 1428:
    meter_axis(VU_SPRITES, (1335,80))
    group5 = meter_group("STEREO",2,(1334,50),VU_SPRITES)
    group5.vuname(0," L")
    group5.vuname(1," R")
    meter_axis(VU_SPRITES, (1382,80))
if screen_width > 1628:
    group6 = meter_group("Stereo-IN",8,(1428,50),VU_SPRITES)
    group6.vuname(0,"1L+R")
    group6.vuname(2,"2L+R")
    group6.vuname(4,"3L+R")
    group6.vuname(6,"4L+R")
if screen_width > 1795:
    meter_axis(VU_SPRITES, (1630, 80))
    group7 = meter_group("EFFECT IN",8,(1695,50),VU_SPRITES)
    group8 = meter_group("EFFECT OUT",8,(1695,300),VU_SPRITES)


# The last thing we do before starting mainloop is to ask mixer to send data


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MIDIME:
            sendme_midi()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()


    pygame.display.flip()
    clock.tick(40)
