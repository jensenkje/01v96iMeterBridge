import random
import sys

import pygame
import pygame.midi
from pygame.locals import *

from spritesheet import load_sprite_sheet_array

# Function to detect and find Mixer and wait for confirmation
def FindMixer():
    # Loop through all mixer channels and look for a message like  :
    #   F0 43 10 3E 1A 7F F7
    return 3

class meter_axis():
   def __init__(self,spritemap,position):
       self.spritemap = spritemap
       self.position = position
       self.positionx,self.positiony = self.position
       screen.blit(spritemap[13], (self.positionx,self.positiony));
       screen.blit(spritemap[14], (self.positionx+20,self.positiony));


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


def sendme_midi():
        # In this subroutine send the different midi controls
        # that will keep mixer to send mixer data
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x04, 0x00, 0x00, 0x00, 0x02, 0xF7]); # master
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x01, 0x00, 0x00, 0x00, 0x08, 0xF7]); # BUS ?
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x02, 0x00, 0x00, 0x00, 0x08, 0xF7]); # AUX
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x00, 0x00, 0x00, 0x00, 0x10, 0xF7]); # 1-16
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x00, 0x00, 0x10, 0x00, 0x10, 0xF7]); # 17-32
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x00, 0x00, 0x20, 0x00, 0x10, 0xF7]);  # Stereo In
        #print("sendme_midi: ")

# Define the MIDI in handler, should be interrupted when pygames support that
# in case we get backlog, ie retrieves multiple 20ms values for each meter, dump old values and use fresh data
def midi_transform(msg):
    tmp = []                                    # temporary list to hold data until 247
    result = {}                                 # The resulting data dict
    for x in msg:
        if x[0].count(247):                     # 247(F7) is sysex endcharacter.
            tmp.extend(x[0][:x[0].index(247)])
            #print("midi_transform (tmp):",tmp)
            data = tmp[9:]
            if len(data) > 0:
                result[str(tmp[6:9])]=tmp[9:]    # using dict to overwrite older values leaving only last value
            tmp=[]
        else:
            tmp.extend(x[0])
    return result

def get_segments(value):
    seg = 0     # number of segments to light up. Found no mathematical model that fits the data
    if value >= 12287:
        seg = 12        # over
    elif value >= 4095:
        seg = 11        # 0 dB
    elif value >= 3971:
        seg = 10
    elif value >= 3858:
        seg = 9
    elif value >= 3716:
        seg = 8
    elif value >= 3602:
        seg = 7
    elif value >= 3460:
        seg = 6
    elif value >= 3347:
        seg = 5
    elif value >= 3091:
        seg = 4
    elif value >= 2836:
        seg = 3
    elif value >= 2581:
        seg = 2
    elif value >= 2070:
        seg = 1
    else:
        seg = 0
    return seg

def midi_router(input):
    for a, b in input.items():
        #print("router", a, b)
        if a == "[4, 0, 0]":
            group5.update(b)
        elif a == "[0, 0, 0]":
            group1.update(b)
        elif a == "[0, 0, 16]":
            group2.update(b)
        elif a == "[2, 0, 0]":
            group3.update(b)
        elif a == "[1, 0, 0]":
            group4.update(b)
        elif a == "[0, 0, 32]":
            group6.update(b)

def print_midi_info():
	for i in range(pygame.midi.get_count()):
		(interf, name, input, output, opened)  = pygame.midi.get_device_info(i)
		if input:
			in_out = "input"
		if output:
			in_out = "output"
		print("%2i: interface :%s:, name :%s:, opened :%s: %s" % (i, interf, str(name,'UTF-8'), opened, in_out))

def waitfor_midi():
    # State = 0 => before midi init
    # State = 1 => after midi loaded, search for Yamaha device
    # State = 2 => Yamaha midi device found
    # State = 3 => Listening for HeartBeat on input channels
    # State = 4 => Heartbeat found and channel selected
    # State = 5 => Channels for input and output initialized, waiting for data
    # State = 6 => Data received, ready to start !
    print("waitformidi")
    state=0
    midi_input = 0
    midi_output = 0
    print_midi_info()
    print("State = 0, validating MIDI layer")
    while state < 1:
        # Just do a simple check to see if midi is initialized
        if pygame.midi.get_init:
            state = 1
        else:
            print("Error: pygame midi not initialized")
            pygame.init()
            pygame.time.wait(5000)
    print("State = ", state, ", search for Yamaha devices ...")
    while state < 2:
        # Search through midi devices for a Yamaha mixer .... future check for multiple
        for i in range(pygame.midi.get_count()):
            (interfaceNr, name, input, output, opened) = pygame.midi.get_device_info(i)
            if '01V96i' in str(name,'UTF-8') and input:
                print("attempt read from ",name)
                m_in = pygame.midi.Input(interfaceNr)
                pygame.time.wait(2000)
                if midi_in.poll():
                    message = midi_transform(midi_in.read(1000))
                    print message

                midi_int = i
                state = 2
        if state < 2:
            pygame.time.wait(2000)
    print(midi_int)
    print("State = ", state, ", looking for heartbeat")
    #while state < 3:
        # now it gets more complicated. Lets try to find heartbeat from device
        # We do not know which channel yet so try all input channels


    # start to display a window on top of screen
    # Show list of

# General Setup
pygame.init()
pygame.midi.init()
waitfor_midi()
pygame.font.init()
font_group = pygame.font.SysFont('Comic Sans MS', 30)
font_vu = pygame.font.SysFont('Arial', 18)
clock = pygame.time.Clock()
BLACK = (0,0,0)
MIDIME = USEREVENT+1
MidiChannel = 3     # Hardcode for now to use Channel 4

# Screen Setup
# Insert code here to calculate screen size
screeninfo = pygame.display.Info()
print(screeninfo)
screen_width = screeninfo.current_w
screen_height = screeninfo.current_h


screen = pygame.display.set_mode((screeninfo.current_w,screeninfo.current_h),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((screen_width,screen_height))
#screen = pygame.display.set_mode((3440,1440),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((2560,1440),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1680,1050),pygame.FULLSCREEN)
#VU_SPRITES = load_sprite_sheet_array("VU1.png",13,1,32,360)
VU_SPRITES = load_sprite_sheet_array("VU3.png",15,1,20,355)
#VU_SPRITES2 = load_sprite_sheet_array("VU1.png",13,1,32,360)

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
    group4 = meter_group("BUS",8,(1090,50),VU_SPRITES)
    for x in range(0,8):
        group4.vuname(x,str(x+1))
if screen_width > 1428:
    meter_axis(VU_SPRITES, (1288,80))
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
    group8 = meter_group("EFFECT OUT",8,(1695,600),VU_SPRITES)

# Configure Midi

# Settings for Rasberry PI
#midi_in = pygame.midi.Input(9)
#midi_out = pygame.midi.Output(8)

# Settings for OSX
midi_in = pygame.midi.Input(3)
midi_out = pygame.midi.Output(11)


# The last thing we do before starting mainloop is to ask mixer to send data
sendme_midi()
pygame.time.set_timer(MIDIME,9000)

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

    if midi_in.poll():
        midi_router(midi_transform(midi_in.read(1000)))

    pygame.display.flip()
    clock.tick(40)
