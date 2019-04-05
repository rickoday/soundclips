#!/usr/bin/python
import fnmatch
import os
import time
import sys
# auto format by the command:
# autopep8 --in-place --aggressive --aggressive tof_2b.py
"""
 * dial.py
 *
 * Created on: 1 Nov 2010
 * Author:     Duncan Law
 *
 *      Copyright (C) 2010 Duncan Law
 *      This program is free software; you can redistribute it and/or modify
 *      it under the terms of the GNU General Public License as published by
 *      the Free Software Foundation; either version 2 of the License, or
 *      (at your option) any later version.
 *
 *      This program is distributed in the hope that it will be useful,
 *      but WITHOUT ANY WARRANTY; without even the implied warranty of
 *      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *      GNU General Public License for more details.
 *
 *      You should have received a copy of the GNU General Public License
 *      along with this program; if not, write to the Free Software
 *      Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


 *      Thanks to Chootair at http://www.codeproject.com/Members/Chootair
 *      for the inspiration and the artwork that i based this code on.
 *      His full work is intended for C# and can be found here:
 *      http://www.codeproject.com/KB/miscctrl/Avionic_Instruments.aspx




 * Requires pySerial and pyGame to run.
 * http://pyserial.sourceforge.net
 * http://www.pygame.org

"""
# serial port listing:  dmesg | grep tty

import math
from math import pi
import serial
import pygame
from pygame.locals import *
pygame.init()


class Dial:
    """
    Generic dial type.
    """

    def __init__(self, image, frameImage, x=0, y=0, w=0, h=0):
        """
        x,y = coordinates of top left of dial.
        w,h = Width and Height of dial.
        """
        self.x = x
        self.y = y
        self.image = image
        self.frameImage = frameImage
        self.dial = pygame.Surface(self.frameImage.get_rect()[2:4])
        self.dial.fill(0xFFFF00)
        if(w == 0):
            w = self.frameImage.get_rect()[2]
        if(h == 0):
            h = self.frameImage.get_rect()[3]
        self.w = w
        self.h = h
        self.pos = self.dial.get_rect()
        self.pos = self.pos.move(x, y)

    def position(self, x, y):
        """
        Reposition top,left of dial at x,y.
        """
        self.x = x
        self.y = y
        self.pos[0] = x
        self.pos[1] = y

    def position_center(self, x, y):
        """
        Reposition centre of dial at x,y.
        """
        self.x = x
        self.y = y
        self.pos[0] = x - self.pos[2] / 2
        self.pos[1] = y - self.pos[3] / 2

    def rotate(self, image, angle):
        """
        Rotate supplied image by "angle" degrees.
        This rotates round the centre of the image.
        If you need to offset the centre, resize the image using self.clip.
        This is used to rotate dial needles and probably doesn't need to be used externally.
        """
        tmpImage = pygame.transform.rotate(image, angle)
        imageCentreX = tmpImage.get_rect()[0] + tmpImage.get_rect()[2] / 2
        imageCentreY = tmpImage.get_rect()[1] + tmpImage.get_rect()[3] / 2

        targetWidth = tmpImage.get_rect()[2]
        targetHeight = tmpImage.get_rect()[3]

        imageOut = pygame.Surface((targetWidth, targetHeight))
        imageOut.fill(0xFFFF00)
        imageOut.set_colorkey(0xFFFF00)
        imageOut.blit(
            tmpImage,
            (0,
             0),
            pygame.Rect(
                imageCentreX -
                targetWidth /
                2,
                imageCentreY -
                targetHeight /
                2,
                targetWidth,
                targetHeight))
        return imageOut

    def clip(self, image, x=0, y=0, w=0, h=0, oX=0, oY=0):
        """
        Cuts out a part of the needle image at x,y position to the correct size (w,h).
        This is put on to "imageOut" at an offset of oX,oY if required.
        This is used to centre dial needles and probably doesn't need to be used externally.
        """
        if(w == 0):
            w = image.get_rect()[2]
        if(h == 0):
            h = image.get_rect()[3]
        needleW = w + 2 * math.sqrt(oX * oX)
        needleH = h + 2 * math.sqrt(oY * oY)
        imageOut = pygame.Surface((needleW, needleH))
        imageOut.fill(0xFFFF00)
        imageOut.set_colorkey(0xFFFF00)
        imageOut.blit(
            image,
            (needleW /
             2 -
             w /
             2 +
             oX,
             needleH /
             2 -
             h /
             2 +
             oY),
            pygame.Rect(
                x,
                y,
                w,
                h))
        return imageOut

    def overlay(self, image, x, y, r=0):
        """
        Overlays one image on top of another using 0xFFFF00 (Yellow) as the overlay colour.
        """
        x -= (image.get_rect()[2] - self.dial.get_rect()[2]) / 2
        y -= (image.get_rect()[3] - self.dial.get_rect()[3]) / 2
        image.set_colorkey(0xFFFF00)
        self.dial.blit(image, (x, y))


class TxSerial:
    """
    Wrapper round pyserial.
    """

    def __init__(self, port, baud, testing=0):
        """
        Open serial port if possible.
        Exit program if not.
        "testing" = 1 prevents the program teminating if valid serial port is not found.
        """

        self.testing = testing
        self.buff = ''
        try:
            self.serial = serial.Serial(port, baud, timeout=1)
        except serial.SerialException:
            print serialPort + " not found."
            print
            print "Usage: " + sys.argv[0] + " [SERIAL_DEVICE]"
            print " Opens SERIAL_DEVICE and lisens for telemitery data."
            print " If SERIAL_DEVICE not specified, /dev/ttyUSB0 will be tried."
            print "Usage: " + sys.argv[0] + " test"
            print " Uses dummy data for testing purposes."
            print
            if (not testing):
                sys.exit()

    def doRead(self):
        bytestoread = self.serial.inWaiting()
        if(bytestoread > 0):
            self.buff = self.buff + self.serial.read(bytestoread)
        if self.buff.find('\n') != -1:
            inlin = self.buff
            print inlin
            self.buff = ""
            return inlin
        else:
            return ""

    def readline1(self):
        if (not self.testing):  # expect two values: gesture no. and vol delta
            #line = self.serial.readline()
            line = self.doRead()
            if(len(line) < 3):
                #print "short"
                return [0, 0]
            #line = "2 0"
            #print line.rstrip()
            a = line.lstrip()
            b = a.rstrip()
            b = ' '.join(b.split())  # remove inside multiple spaces
            c = b.split(' ')
            #print c
            try:
                d = [int(s) for s in c]
                print d
            except BaseException:
                d = [0, 0]
                print ' parsing error'
            if(len(d) >= 2):
                if(d[1] == 0):
                    print d
                return d
            else:
                return [0, 0]
            # if (self.countvals(line)<2 ): # partial line, read again...
            #   line = self.serial.readline()
        else:
            line = ''

        br_data = 0
        if (len(line) > 5):
            vals = self.parsevals(line)
            br_data = vals[3]
            if (br_data > 255):
                br_data = 255
            return br_data

    def countvals(line):
        a = line.lstrip()
        b = a.rstrip()
        c = b.split(' ')
        return len(c)

    def parsevals(line):
        a = line.lstrip()
        b = a.rstrip()
        c = b.split(' ')
        d = [int(s) for s in c]
        return d

    def close(self):
        """
        Close serial port.
        """
        if((not self.testing) and self.serial.isOpen()):
            self.serial.close()      # close serial port.
# ====================================================================


class Volknob(Dial):
    """
    Generic Dial. This is built on by other dials.
    """

    def __init__(self, x=0, y=0, w=0, h=0):
        """
        Initialise dial at x,y.
        Default size of 300px can be overidden using w,h.
        """
        self.frameImage = pygame.image.load('volumeknob2.png').convert()
        self.image = pygame.image.load('volumemark.png').convert()
        self.blackdot = self.image
        self.greendot = pygame.image.load('volumedotgreen1.png').convert()

        self.imagedotarr = pygame.image.load('dots_arrows.png').convert()
        # gesture image overlays...
        self.imagedot = self.clip(self.imagedotarr, 20, 13, 60, 60, 0, 0)
        self.imagearr = self.clip(self.imagedotarr, 11, 92, 116, 66, 0, 0)
        self.imagearrrl = pygame.transform.flip(self.imagearr, 1, 0)
        self.imagearrup = pygame.transform.rotate(self.imagearr, 90)
        self.imagearrdn = pygame.transform.rotate(self.imagearr, -90)

        Dial.__init__(self, self.image, self.frameImage, x, y, w, h)

        # buttons background
        self.chunk = self.clip(self.frameImage, 0, 0, 10, 10, 0, 0)
        self.chunk1 = pygame.transform.smoothscale(self.chunk, (307, 80))
        screen.blit(self.chunk1, (0, 300))

        # buttons
        #self.imagebutt = pygame.image.load('glossy-media-player-buttons-md-crop.png').convert_alpha()
        self.imagebutt = pygame.image.load(
            'Glossy-media-player-buttons-Inverted.png').convert_alpha()
        colorkey = self.imagebutt.get_at((0, 0))
        self.imagebutt.set_colorkey(colorkey, RLEACCEL)
        #print 'colorkey: ', colorkey
        # self.imagebutt.set_colorkey(0xFEFEFE)
        self.imagebutt = pygame.transform.smoothscale(
            self.imagebutt, (299, 111 * 299 / 589))
        screen.blit(self.imagebutt, (0, 310))

        self.dimcirc = pygame.image.load('butt_dim_circ1.png').convert()
        self.dimcirc.set_colorkey(0xFFFFFF)
        self.bluecirc = pygame.image.load('butt_blue_circ.png').convert()
        self.bluecirc.set_colorkey(0xFFFFFF)

    def blit_alpha(self, target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface(
            (source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)
        temp.set_colorkey(0xFFFFFF)
        target.blit(temp, location)

    def mod_butt(self, butt_no, dimage):
        x = butt_no * 60 + 0
        self.blit_alpha(screen, dimage, (x, 309), 200)

    def update_butts(self, dimval, dotval):
        screen.blit(self.imagebutt, (0, 310))
        for i in range(5):
                    #print i, dimval
            if (dimval & 1):
                #print 50*i
                self.mod_butt(i, self.dimcirc)
            dimval = dimval >> 1
        for i in range(5):
            #print i, dotval
            if (dotval & 1):
                #print 50*i
                self.mod_butt(i, self.bluecirc)
            dotval = dotval >> 1
       # time.sleep(1)
        pygame.display.flip()

    def update(self, screen, angleX, cntrl, pause):
        """
        Called to update a Generic dial.
        "angleX" and "angleY" are the inputs.
        "screen" is the surface to draw the dial on.
        """

        angleX %= 360
        angleX = 360 - angleX
        if (cntrl == 7):
            self.image = self.greendot
            # if beep_enable:
            # beep1.play()
        if (cntrl == 6):
            self.image = self.blackdot
            # if beep_enable:
            # beep1.play()
        #pygame.transform.threshold(self.image, self.image,(0,0,0,255),(0,0,0,0),(0,254,0,255))
        #pygame.transform.threshold(self.image, self.image,(0,0,0),(100,100,100),(0,254,0),2,None,1)
        #arr = PixelArray( self.image )
        #arr.replace( (0,0,0,255), (0,255,0,255) )
        #del arr
        tmpImage = self.clip(self.image, 0, 0, 0, 0, 0, -83)

        tmpImage = self.rotate(tmpImage, angleX)
        self.overlay(self.frameImage, 0, 0)
        self.overlay(tmpImage, 0, 9)
        if(pause):
            dimval = 1
        else:
            dimval = 4

        # control symbols to overlay
        dotval = 0
        if (cntrl == 1):
            self.overlay(self.imagedot, 0, 9)
            dotval = dimval
        if (cntrl == 2):
            self.overlay(self.imagedot, -40, 9)
            self.overlay(self.imagedot, 40, 9)
            dotval = 8
        if (cntrl == 3):
            self.overlay(self.imagedot, -75, 9)
            self.overlay(self.imagedot, 75, 9)
            self.overlay(self.imagedot, 00, 9)
            dotval = 16
        # if (cntrl == 8):
            #self.overlay( self.imagearr, 0, 9 )
        # if (cntrl == 7):
            #self.overlay( self.imagearrrl, 0, 9 )
        if (cntrl == 11):
            self.overlay(self.imagearr, -65, 9)
            self.overlay(self.imagearr, 65, 9)

        if (cntrl == 77):
            self.overlay(self.imagearrrl, -65, 9)
            self.overlay(self.imagearrrl, 65, 9)
        if (cntrl == 9):
            self.overlay(self.imagearrup, 0, 9)
        if (cntrl == 10):
            self.overlay(self.imagearrdn, 0, 9)
        if (cntrl == 110):
            self.overlay(self.imagearrup, 0, 9 - 65)
            self.overlay(self.imagearrup, 0, 9 + 65)
        if (cntrl == 110):
            self.overlay(self.imagearrdn, 0, 9 - 65)
            self.overlay(self.imagearrdn, 0, 9 + 65)

        self.dial.set_colorkey(0xFFFF00)
        screen.blit(
            pygame.transform.scale(
                self.dial, (self.w, self.h)), self.pos)
        pygame.display.update()
        screen.blit(self.chunk1, (165, 300))
        self.update_butts(dimval + 2, dotval)
        if (cntrl > 0 and cntrl <= 11):
            pygame.time.delay(400)
            self.overlay(self.frameImage, 0, 0)
            self.overlay(tmpImage, 0, 9)
            screen.blit(
                pygame.transform.scale(
                    self.dial, (self.w, self.h)), self.pos)
            self.update_butts(dimval + 2, 0)
            # pygame.time.delay(500)

        GREEN = (0, 255, 0)
        #print angle
        #pygame.draw.arc(screen, GREEN,[183, 27, 282, 282], 0, pi*230.0/180.0, pi*angle/180.0)


def millisec():
    return int(round(time.time() * 1000))

# ====================================================================
# ====================================================================


serialPort = '/dev/ttyUSB0'
serialPort = '/dev/ttyACM0'
print ' '
print 'AIDP song control demo 20181015'
print '  m - stop/start music'
print '  b - enable/disable audible feedback beeps'
print ' '
print 'Port: ' + serialPort
baud = 115200

if (len(sys.argv) == 1):
    # No options used at run time. Presume serial port is "dev/ttyUSB0"
    test = 0
    #serialPort = '/dev/ttyUSB0'
elif (sys.argv[1] == 'test'):
    # Option "test" was selected. Run in test mode. (Dummy data used.)
    test = 1
else:
    # An option other that "test" was enterd. Maybe it's the Serial port.
    test = 0
    serialPort = sys.argv[1]

# Initialise Serial port.
ser = TxSerial(serialPort, baud, test)

# Initialise screen.
#screen = pygame.display.set_mode((640, 480))
screen = pygame.display.set_mode((307, 380))
screen.fill(0x222222)

# Initialise Dial.
volume = Volknob(0, 10, 307, 273)

# initialize strip chart
# https://stackoverflow.com/questions/557069/quick-and-dirty-stripchart-in-python
volvalue = 32
posprev = 0
a = 0
idx = 0
pause = 0
music_enable = 0
beep_enable = 1
t0 = millisec()
tvol = millisec()
tclick = millisec()
vol_state = 'vol_mid'
new_state = vol_state

#fnames = ["01 - Band On The Run.mp3",  "05 Dreamboat Annie.mp3", "04 Rhiannon.mp3", "13 - Blackbird.mp3", "04 - Two Hearts.mp3"]
# get file names of all mp3 files in this folder
#fnames = fnmatch.filter(os.listdir('.'), '*.mp3')
strpath = './mp3files/'
fnames = fnmatch.filter(os.listdir(strpath), '*.mp3')
nfiles = len(fnames)
mousebuttprev = pygame.mouse.get_pressed()

file = fnames[idx]
if(not test):
    pygame.display.set_caption('Bose AID&P Demo')
else:
    pygame.display.set_caption('Bose AID&P Demo Player - Test Mode')

# pygame.mixer.quit()
pygame.mixer.pre_init(22050, -16, 2, 2048)
pygame.init()
pygame.mixer.quit()
#pygame.mixer.init(22050, -16, 2, 4096)
pygame.mixer.init(22050, -16, 2, 512)
# pygame.mixer.init()
# pygame.init()

beep1 = pygame.mixer.Sound('./mp3files/beep1.wav')
beep2 = pygame.mixer.Sound('./mp3files/beep2.wav')
volbeepenable = 0

pygame.mixer.music.load(strpath + file)
if music_enable:
    pygame.mixer.music.play()
volume.update(screen, -90, 0, 0)
pygame.display.update()
pygame.mixer.music.set_volume(64)
while True:
    # -------------   Main program loop.   ----------------
    br_data = [0, 0]
    for event in pygame.event.get():
        if event.type == QUIT:
            print "Exiting...."
            ser.close()  # close serial port.
            sys.exit()   # end program.
        if event.type == pygame.KEYDOWN:  # if key pressed...
            print "key pressed  "
            # determine if a number key was pressed...
            if(event.key > pygame.K_0 and event.key <= pygame.K_9):
                ctrl = event.key - pygame.K_0
            else:
                ctrl = 0
            br_data = [ctrl, 0]
            # if letter key pressed, mode change...
            if (event.key == pygame.K_x or event.key == pygame.K_m):
                if(music_enable == 1):
                    music_enable = 0
                    pygame.mixer.music.stop()
                    print "Music off."
                else:
                    music_enable = 1
                    pygame.mixer.music.play()
                    print "Music on."
            if (event.key == pygame.K_b):
                if(beep_enable == 1):
                    beep_enable = 0
                    print "Beeps off."
                    volume.overlay(
                        volume.greendot, 50, 50)  # =================
                else:
                    beep_enable = 1
                    print "Beeps on."
                    volume.overlay(
                        volume.blackdot, 50, 50)  # =================

    if(test):
        # Use dummy test data
        curPos = pygame.mouse.get_pos()

        mousebutt = pygame.mouse.get_pressed()
        if((mousebutt[0] == 1) and (mousebuttprev == 0)):
            posprev = curPos[0] / 1
#      print mousebutt
        if((curPos[0] / 1 - posprev) != 0 and mousebutt[0]):
            br_data[1] = curPos[0] / 1 - posprev
            br_data[1] = br_data[1] * 2
            posprev = curPos[0] / 1
            print curPos
        pygame.time.delay(50)
        mousebuttprev = mousebutt[0]
    else:
        # Get real data from USB port.
        br_data = ser.readline1()

#   pygame.mixer.music.set_volume(float(volvalue)/255)

    if(br_data):  # if we have data....
        if(br_data[0] == 20 or br_data[1] == 21): # if volume change commands: 21=down, 20=up.
            # volvalue += br_data[1]/2 # for brooch
            # volvalue += br_data[1]/1 # for brooch
            # volvalue += br_data[1]*2 # for hart
            # volvalue += br_data[1]*2.5 # for TOF sensor
            # Volume change commands:  21 is down, 20 is up...
            volincrement = ((20 - br_data[0]) + 0.5) * 2  # direction sign
            volincrement *= br_data[1]  # aplpy increment
            # volvalue += br_data[1]*2.5 # for TOF sensor
            volvalue += volincrement  # for TOF sensor
            if(volvalue > 255):
                volvalue = 255
            elif(volvalue < 5):
                volvalue = 5
            # print(br_data)
            vol_level = float(volvalue) / 255
            pygame.mixer.music.set_volume(vol_level)
            #print( " vol: %5.3f" % vol_level)

        # volume sound queues at reacing max and min...
        #print 'volvalue  ', volvalue, '  state ', vol_state, '  data ', br_data[1]
        if vol_state == 'vol_max':
            if volvalue < 255:
                new_state = 'vol_mid'
        if vol_state == 'vol_min':
            if volvalue > 5.5:
                new_state = 'vol_mid'
        if vol_state == 'vol_mid':
            if volvalue == 255:
                new_state = 'vol_max'
                tclick = millisec()
                if beep_enable:
                    beep2.play(1)
            if volvalue < 5.5:
                new_state = 'vol_min'
                tclick = millisec()
                if beep_enable:
                    beep2.play(1)
        vol_state = new_state

        # music playing stuff...

        ctrl = br_data[0]
        if(ctrl == 1):  # play/pause
            if(pause):
                if music_enable:
                    pygame.mixer.music.unpause()
                pause = 0
                if beep_enable:
                    beep1.play()
            else:
                if music_enable:
                    pygame.mixer.music.pause()
                pause = 1
                if beep_enable:
                    beep1.play()

        if (ctrl == 2):  # skip to next song
            if music_enable:
                idx += 1
                if(idx >= nfiles):
                    idx = 0  # wrap around
                pygame.mixer.music.stop()
                pygame.mixer.music.load(strpath + fnames[idx])
                pygame.mixer.music.play()
            if beep_enable:
                beep1.play(1)

        if (ctrl == 3):  # skip to prev song
            if music_enable:
                idx -= 1
                if(idx < 0):
                    idx = nfiles - 1  # wrap around
                pygame.mixer.music.stop()
                pygame.mixer.music.load(strpath + fnames[idx])
                pygame.mixer.music.play()
            if beep_enable:
                beep1.play(2)

        # if (ctrl == 7 ): # beep while in volume change state
        if (ctrl == 200):  # beep while in volume change state
            tclick = millisec()
            if beep_enable:
                beep1.play()
                time.sleep(0.250)
                beep1.set_volume(0.5)
                volbeepenable = 1
        if (ctrl == 6):
            if beep_enable:
                beep1.set_volume(1.0)
                beep1.play(1)
            volbeepenable = 0

        # Update dial image...
        if (ctrl != 0 or br_data[1] != 0):
            angle = (volvalue * 280) / 255 - 140
            volume.update(screen, angle, ctrl, pause)

            pygame.display.update()

    if(not pygame.mixer.music.get_busy()):
        if music_enable:
            idx += 1
            if(idx >= nfiles):
                idx = 0
            pygame.mixer.music.load(strpath + fnames[idx])
            pygame.mixer.music.play()


    if (millisec() - tclick > 750) and volbeepenable:
        #print 'time: ', t0
        beep1.play()
        tclick = millisec()

    while millisec() - t0 < 10:
        aaa = 5
    t0 = t0 + 10

#   elif not ser.testing:
#      # We do not have any data to display.
#      print " * No data received. Is the transmitter powered on?"
#      print " * Restarting " + serialPort + ".\n"
#      ser = TxSerial(serialPort, baud)


# ick@HP-ProBook-4530s ~/Desktop/cockpit1/cockpit $ sudo moserial
# rick@HP-ProBook-4530s ~/Desktop/cockpit1/cockpit $ sudo moserial
# rick@HP-ProBook-4530s ~/Desktop/cockpit1/cockpit $ sudo python volume.py /dev/ttyACM0
#['', '0', '0', '30', '\n']
