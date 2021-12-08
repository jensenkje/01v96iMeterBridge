import ast
import sys
from typing import Union, Any

import pygame
import pygame.midi
from pygame.locals import *

from spritesheet import load_sprite_sheet_array

class FPSCounter:
    def __init__(self, surface, font, clock, color, bgcolour, pos):
        self.surface = surface
        self.font = font
        self.clock = clock
        self.pos = pos
        self.color = color
        self.bgcolour = bgcolour
        self.fps = 0

        self.fps_text = self.font.render(str(int(self.clock.get_fps())) + "FPS", False, self.color)
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))

    def render(self):
        self.surface.blit(self.fps_text, self.fps_text_rect)

    def update(self):
        # remove old text
        self.fps_text = self.font.render(str(self.fps) + "FPS", False, self.bgcolour)
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))
        self.surface.blit(self.fps_text, self.fps_text_rect)

        # display new FPS
        self.fps = round(self.clock.get_fps())
        self.fps_text = self.font.render(str(self.fps) + "FPS", False, self.color)
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))
        self.surface.blit(self.fps_text, self.fps_text_rect)




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
        self.endX = self.positionx
        self.endY = self.positiony
        self.meter = []
        self.spritemap = spritemap
        self.grouptext = font_group.render(self.name,False,(255,255,255))
        screen.blit(self.grouptext,(self.positionx,self.positiony+5))
        self.meter = [meter_vu(self.spritemap, (self.positionx+(x*25),self.positiony+30)) for x in range(0,self.number_vu)]
        self.endX = self.positionx + (self.number_vu * 25)
        screen.blit(spritemap[13], (self.endX, self.positiony+30))
        screen.blit(spritemap[14], (self.endX + 20, self.positiony+30))
        self.endX = self.endX + 45

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
    def __init__(self, spritemap, posx, posy, address):
        self.spritemap = spritemap
        self.volume = -1
        self.background = spritemap[15]
        self.address = address
        self.posx = posx
        self.posy = posy
        self.sel = 0
        self.solo = 0
        self.on = 0
        # Draw objects on screen
        #screen.blit(BUTTONS[0], (self.posx,self.posy-75))       # SEL
        #screen.blit(BUTTONS[2], (self.posx,self.posy-50))       # SOLO
        #screen.blit(BUTTONS[4], (self.posx, self.posy-25))      # ON
        self.set_button("SEL",0)
        self.set_button("SOLO",0)
        self.set_button("ON",0)
        screen.blit(self.background, (self.posx,self.posy))
        message = [0xF0, 0x43, 0x30, 0x3E, 0x7F]
        message.extend(self.address)
        message.append(0xF7)
        midi_out.write_sys_ex(0, message)
        #print("message", message)

    def update(self, value, spriteNum=0):
        # expected input is the midi value
        self.volume = value
        x = (1023 - value) // 3.7                        # Flip it to match x,y coordinates on screen
        screen.blit(self.background, (self.posx, self.posy))
        screen.blit(FADERS[spriteNum], (self.posx, self.posy+x+30))
#        print("fader ", value, x, self.posy+x)
#        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x7F, 1, 79, 0, 1, 0xF7])

    def set_button(self, button, value):
        if button == "SEL":
            self.sel = value
            screen.blit(BUTTONS[2+value], (self.posx, self.posy - 75))
        elif button == "SOLO":
            self.solo = value
            screen.blit(BUTTONS[4+value], (self.posx, self.posy - 50))
        elif button == "ON":
            self.on = value
            screen.blit(BUTTONS[0+value], (self.posx, self.posy - 25))

class fader_group():
    def __init__(self, name, startfader, numfaders, spritemap, startX, startY, groupAddress ):
        self.name = name
        self.startX = startX
        self.startY = startY
        self.endX = startX
        self.endY = startY
        self.groupAddress = groupAddress
        self.numfaders = numfaders
        self.spritemap = spritemap
        self.midiId = ""
        self.midiCmd = ""
        self.fader = []
        self.faderSpriteNum = 0
        if self.name == "STEREO":
            self.faderSpriteNum = 1
        if self.name == "ST-IN":
            self.faderSpriteNum = 2
        self.groupAddress = groupAddress
        for x in range(0, self.numfaders):
            addr=list(self.groupAddress)
            addr.append(x+startfader)
            self.fader.append( fader(self.spritemap, self.startX + (x * 25), self.startY + 30, addr) )
        self.endX = self.startX+(numfaders*25)
        screen.blit(spritemap[16], (self.endX,self.startY+30))
        screen.blit(spritemap[17], (self.endX+20, self.startY+30))
        self.endX = self.endX + 45

    def set_midiId(self,  s ):
        self.midiId = s

    def set_midiCmd(self,  s ):
        self.midiId = s

    def update(self, faderNum, input ):
        # Expected input is four 7-bit numbers. Fader position in last two only ?
        value = int(input[2]) * 128 + int(input[3])
#        print("fader_group ",faderNum,input,value)
        self.fader[faderNum].update(value, self.faderSpriteNum)

    def set_button(self, faderNum, button, input):
        value = int(input[2]) * 128 + int(input[3])
        self.fader[faderNum].set_button(button, value)

    def set_sel(self, faderNum):
        global active_sel
        print("fadergroup set sel", faderNum)
        if active_sel != 0:
            active_sel.set_button("SEL",0)
        self.fader[faderNum].set_button("SEL",1)
        active_sel = self.fader[faderNum]


def sendme_midi():
        # In this subroutine send the different midi controls
        # that will keep mixer to send mixer data
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x04, 0x00, 0x00, 0x00, 0x02, 0xF7]) # master
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x01, 0x00, 0x00, 0x00, 0x08, 0xF7]) # BUS ?
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x02, 0x00, 0x00, 0x00, 0x08, 0xF7]) # AUX
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x00, 0x00, 0x00, 0x00, 0x10, 0xF7]) # 1-16
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x00, 0x00, 0x10, 0x00, 0x10, 0xF7]) # 17-32
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 0x21, 0x00, 0x00, 0x20, 0x00, 0x10, 0xF7]) # Stereo In
        #print("sendme_midi: ")

# Define the MIDI in handler, should be interrupted when pygames support that
# in case we get backlog, ie retrieves multiple 20ms values for each meter, dump old values and use fresh data
def midi_transform(msg, type=33):
    # input array of midi messages. Message = [[payload],timestamp]
    # Payload is 4 words in each message, terminated with 247.
    # type=33 => sysex RemoteMeter from mixer
    # type=127 => sysex heartbeat identification message
    # Header=word 1-5, address=word 6-9, data=word10-wordN
    tmp = []                                    # temporary list to hold data until 247
    result = {}                                 # The resulting data dict
    for x in msg:
        if x[0].count(247):                     # Do we have an end of message 247(F7) is sysex endcharacter.
            tmp.extend(x[0][:x[0].index(247)])
            #print("tmp=", tmp)  # only for debugging
            if len(tmp) >= 6:                   # If combined message is shorter than 6 words, throw it away
                address1 = tmp[5]
                if address1 == 127 and address1 == type:
                    return tmp
                #elif address1 == 33 and type == address1:
                else:
                    result[str(tmp[5:9])] = tmp[9:]   # using dict to overwrite older values leaving only last value
            tmp=[]
        else:
            tmp.extend(x[0])                # Message have no termination so keep combining

    #print("result=", result)
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
    for addrStr, data in input.items():                     # Loop across all midi messages received
        address = ast.literal_eval(addrStr)                 # workaround to fix string in literals
        #print("router", address, data)
        if address[0] == 127:
            pass
        elif address[0] == 33:                      # Address say this is METER data
            if address == [33, 4, 0, 0]:
                group5.update(data)
            elif address == [33, 0, 0, 0]:
                group1.update(data)
            elif address == [33, 0, 0, 16]:
                group2.update(data)
            elif address == [33, 2, 0, 0]:
                group3.update(data)
            elif address == [33, 1, 0, 0]:
                group4.update(data)
            elif address == [33, 0, 0, 32]:
                group6.update(data)
        elif address[0] == 1 and address[1] == 28:      # Fader position 1-32 + ST-IN !!!
            fader = address[3]
            if fader <= 15:                             # Fader 1-16
                fader1.update(fader,data)
            elif fader <= 31:                           # Fader 17-32
                fader2.update(fader-16, data)
            elif fader <= 39:                           # ST-IN
                fader6.update(fader-32, data)
        elif address[0] == 1 and address[1] == 77:      # ON STEREO
            fader5.set_button(address[3], "ON", data)
        elif address[0] == 1 and address[1] == 79:      # Fader STEREO
            fader5.update(address[3], data)
        elif address[0] == 1 and address[1] == 41:      # ON BUS
            fader4.set_button(address[3], "ON", data)
        elif address[0] == 1 and address[1] == 43:      # Fader BUS
            fader4.update(address[3], data)
        elif address[0] == 1 and address[1] == 54:      # ON AUX
            fader3.set_button(address[3], "ON", data)
        elif address[0] == 1 and address[1] == 57:      # Fader AUX
            fader3.update(address[3], data)
        elif address[0] == 1 and address[1] == 26:       # Channel on/off button
            fader = address[3]
            if fader <= 15:
                fader1.set_button(fader, "ON", data)
            elif fader <= 31:
                fader2.set_button(fader-16, "ON", data)
            elif fader <= 39:
                fader6.set_button(fader-32, "ON", data)
        elif address[0] == 3 and address[1] == 46:
            fader = address[3]
            if fader <= 15:                                 # CH1-16
                fader1.set_button(fader, "SOLO", data)
            elif fader <= 31:                               # CH17-32
                fader2.set_button(fader-16, "SOLO", data)
            elif fader <= 39:                               # ST-IN
                fader6.set_button(fader-32, "SOLO", data)
        elif address[0] == 3 and address[1] == 47:          # AUX
            fader = address[3]
            if fader <= 7:  # ???
                fader4.set_button(fader, "SOLO", data)
            elif fader <= 15:  # CH17-32
                fader3.set_button(fader - 8, "SOLO", data)
        elif address == [4, 9 ,24, 0]:
            fader = int(data[3])
            print("SEL", address,data)
            if fader <= 15:
                fader1.set_sel(fader)
            elif fader <= 31:
                fader2.set_sel(fader-16)
            elif fader <= 39:
                fader6.set_sel(fader - 32)
            elif fader <= 47:
                fader3.set_sel(fader-40)
            elif fader <= 55:
                fader4.set_sel(fader-48)
            elif fader <= 57:
                fader5.set_sel(fader-56)
        else:
            print("router unknown", address, data)


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
    print("State = 0, validating MIDI layer")
    #while state < 1:
        # Just do a simple check to see if midi is initialized
    #    if pygame.midi.get_init:
    #        state = 1
    #    else:
    #        print("Error: pygame midi not initialized")
    #        pygame.init()
    #        pygame.time.wait(5000)
    print("State = ", state, ", search for Yamaha devices ...")
    while state < 2:
        # Search through midi devices for a Yamaha mixer .... future check for multiple
        for i in range(pygame.midi.get_count()):
            (interface, name, input, output, opened) = pygame.midi.get_device_info(i)
            print(i,name)
            if '01V96' in str(name,'UTF-8') and input:
                print("attempt read from ",i,name)
                m_in = pygame.midi.Input(i)
                pygame.time.wait(1000)  # we expect 3-4 messages each second
                if m_in.poll():
                    res = midi_transform(m_in.read(100), 127)
                    print("got result : ", res)
                    if res[4] == 26:
                        print("Found 01v96i....")
                        midi_input = i
                        state = 4
                        m_in.close()
                        break
                    elif res[4] == 13:
                        print("Found 01v96....")
                        midi_input = i
                        state = 4
                        m_in.close()
                        break
                m_in.close()
        pygame.time.wait(3000)
        # Reload MIDI stack after each attempt to find new devices ?? Does Not work !
        pygame.quit()
        pygame.init()

    # Locate MIDI out based on name
    for i in range(pygame.midi.get_count()):
        (interface, name, input, output, opened) = pygame.midi.get_device_info(i)
        if name == pygame.midi.get_device_info(midi_input)[1] and output:
            midi_output = i
    return midi_input, midi_output

def get_active_select():
    print("active select request")
    midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 4, 9, 24, 0, 0xF7])
   #midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x7F, 0x04, 0x09, 0x18, 0x00, 0xF7])



def get_active_on():
    # simply send request for all on addresses from 0 to ?
    # Warning: word 3 and 4 is really system dependent ... improve
    for x in range(0,39):
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x7F, 1, 26, 0, x, 0xF7]) #CH1-32 + ST-IN
    for x in range(0,8):
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x7F, 1, 41, 0, x, 0xF7])  # BUS
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x7F, 1, 54, 0, x, 0xF7])  # AUX
    for x in range(0,2):
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x7F, 1, 77, 0, x, 0xF7])  # MAIN

def get_active_solo():
    for x in range(0,39):
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 3, 46, 0 , x, 0xF7]) #CH1-32 + ST-IN
    for x in range(0, 16):
        midi_out.write_sys_ex(0, [0xF0, 0x43, 0x30, 0x3E, 0x1A, 3, 47, 0, x, 0xF7])  # CH1-32 + ST-IN


#=========================== MAIN =====================================

# General Setup
pygame.init()
pygame.midi.init()
#print_midi_info()
mi,mo = waitfor_midi()
print("midi = ",mi,mo)
pygame.midi.init()
pygame.midi.quit()
pygame.midi.init()
# Settings for OSX
midi_in = pygame.midi.Input(mi)
midi_out = pygame.midi.Output(mo)
#midi_out = pygame.midi.Output(17)      # To be able to see sent midi data in MidiView
#print_midi_info()
pygame.font.init()
font_group = pygame.font.SysFont('Comic Sans MS', 30)
font_vu = pygame.font.SysFont('Arial', 18)
clock = pygame.time.Clock()
BLACK = (0,0,0)
MIDIME = USEREVENT+1
vuPosY = 0
faderPosY = 625
display_fps = 0
active_sel = 0          # initially. Will be active fader object ref later

# Screen Setup
# Insert code here to calculate screen size
screeninfo = pygame.display.Info()
print(screeninfo)
screen_width = screeninfo.current_w
screen_height = screeninfo.current_h


screen = pygame.display.set_mode((screeninfo.current_w,screeninfo.current_h),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((screeninfo.current_w,screeninfo.current_h))
#screen = pygame.display.set_mode((screen_width,screen_height))
#screen = pygame.display.set_mode((3440,1440),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((2560,1440),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1680,1050),pygame.FULLSCREEN)
#VU_SPRITES = load_sprite_sheet_array("VU1.png",13,1,32,360)
VU_SPRITES = load_sprite_sheet_array("VU4.png",18,1,20,355)
BUTTONS = load_sprite_sheet_array("buttons.png",6,1,20,20)
FADERS = load_sprite_sheet_array("faders.png",3,1,20,36)
#VU_SPRITES2 = load_sprite_sheet_array("VU1.png",13,1,32,360)

# Display FPS
fps_counter = FPSCounter(screen,font_group,clock,(255,0,0),(0,0,0),(150,10))

# Load and draw the objects of the screen
if screen_width > 500:
    group1 = meter_group("1-16", 16,(0,50),VU_SPRITES)
    fader1 = fader_group("1-16", 0, 16, VU_SPRITES, 0, faderPosY, [1,28,0])
    for x in range(0,16):
        group1.vuname(x,str(x+1))
if screen_width > 890:
    group2 = meter_group("17-32", 16,(group1.endX,50),VU_SPRITES)
    fader2 = fader_group("17-32", 16, 16, VU_SPRITES, fader1.endX, faderPosY, [1,28,0])

    for x in range(0,16):
        group2.vuname(x,str(x+17))
if screen_width > 1288:
    group3 = meter_group("AUX",8,(group2.endX,50),VU_SPRITES)
    fader3 = fader_group("AUX", 0, 8, VU_SPRITES, fader2.endX, faderPosY, [1, 57, 0])
    for x in range(0,8):
        group3.vuname(x,str(x+1))
    group4 = meter_group("BUS",8,(group3.endX,50),VU_SPRITES)
    fader4 = fader_group("BUS", 0, 8, VU_SPRITES, fader3.endX, faderPosY, [1, 43, 0])
    for x in range(0,8):
        group4.vuname(x,str(x+1))
if screen_width > 1428:
    group5 = meter_group("STEREO",2,(group4.endX,50),VU_SPRITES)
    fader5 = fader_group("STEREO", 0, 2, VU_SPRITES, fader4.endX, faderPosY, [1, 79, 0])
    group5.vuname(0," L")
    group5.vuname(1," R")
if screen_width > 1628:
    group6 = meter_group("Stereo-IN",8,(group5.endX,50),VU_SPRITES)
    fader6 = fader_group("ST-IN", 32, 8, VU_SPRITES, fader5.endX, faderPosY, [1, 28, 0])
    group6.vuname(0,"1L+R")
    group6.vuname(2,"2L+R")
    group6.vuname(4,"3L+R")
    group6.vuname(6,"4L+R")
if screen_width > 1795:
    #meter_axis(VU_SPRITES, (1630, 80))
    group7 = meter_group("EFFECT IN", 8, (group6.endX,50),VU_SPRITES)
    group8 = meter_group("EFFECT OUT", 8, (group7.endX,50),VU_SPRITES)


# The last thing we do before starting mainloop is to ask mixer to send data

get_active_solo()
get_active_on()
sendme_midi()
get_active_select()
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
            if event.key == K_f:
                display_fps = 1

    if midi_in.poll():
        midi_router(midi_transform(midi_in.read(1000)))

    pygame.display.flip()
    clock.tick(40)

    if display_fps:
        fps_counter.update()
